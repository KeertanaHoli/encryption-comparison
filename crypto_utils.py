import os
import hashlib
import time
from Crypto.Cipher import AES, ChaCha20_Poly1305
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import ascon

ALGORITHM_IDS = {
    'AES-256-GCM': b'AES',
    'Ascon-128a': b'ASC',
    'ChaCha20-Poly1305': b'CHA'
}

ALGORITHM_NAMES = {v: k for k, v in ALGORITHM_IDS.items()}

def derive_key(passphrase: str, salt: bytes) -> bytes:
    return PBKDF2(passphrase, salt, dkLen=32, count=200000, hmac_hash_module=SHA256)

def encrypt_file(file_data: bytes, passphrase: str, algorithm: str) -> tuple:
    start_time = time.perf_counter()
    
    salt = get_random_bytes(16)
    key = derive_key(passphrase, salt)
    
    algorithm_id = ALGORITHM_IDS[algorithm]
    
    if algorithm == 'AES-256-GCM':
        nonce = get_random_bytes(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(file_data)
        
    elif algorithm == 'Ascon-128a':
        nonce = get_random_bytes(16)
        key_16 = key[:16]
        ciphertext = ascon.encrypt(key_16, nonce, b'', file_data)
        tag = ciphertext[-16:]
        ciphertext = ciphertext[:-16]
        
    elif algorithm == 'ChaCha20-Poly1305':
        nonce = get_random_bytes(12)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(file_data)
    
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    encrypted_data = algorithm_id + salt + nonce + tag + ciphertext
    
    end_time = time.perf_counter()
    encryption_time_ms = (end_time - start_time) * 1000
    
    file_hash = hashlib.sha256(file_data).hexdigest()
    
    metadata = {
        'algorithm': algorithm,
        'file_hash': file_hash,
        'nonce': nonce.hex(),
        'tag': tag.hex(),
        'salt': salt.hex(),
        'file_size': len(file_data),
        'encryption_time_ms': encryption_time_ms
    }
    
    return encrypted_data, metadata

def decrypt_file(encrypted_data: bytes, passphrase: str) -> tuple:
    start_time = time.perf_counter()
    
    algorithm_id = encrypted_data[:3]
    
    if algorithm_id not in ALGORITHM_NAMES:
        raise ValueError("Unknown encryption algorithm or corrupted file")
    
    algorithm = ALGORITHM_NAMES[algorithm_id]
    
    offset = 3
    salt = encrypted_data[offset:offset+16]
    offset += 16
    
    key = derive_key(passphrase, salt)
    
    if algorithm == 'AES-256-GCM':
        nonce = encrypted_data[offset:offset+12]
        offset += 12
        tag = encrypted_data[offset:offset+16]
        offset += 16
        ciphertext = encrypted_data[offset:]
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError as e:
            raise ValueError("Decryption failed: Invalid passphrase or corrupted file")
            
    elif algorithm == 'Ascon-128a':
        nonce = encrypted_data[offset:offset+16]
        offset += 16
        tag = encrypted_data[offset:offset+16]
        offset += 16
        ciphertext = encrypted_data[offset:]
        
        key_16 = key[:16]
        try:
            plaintext = ascon.decrypt(key_16, nonce, b'', ciphertext + tag)
        except Exception as e:
            raise ValueError("Decryption failed: Invalid passphrase or corrupted file")
            
    elif algorithm == 'ChaCha20-Poly1305':
        nonce = encrypted_data[offset:offset+12]
        offset += 12
        tag = encrypted_data[offset:offset+16]
        offset += 16
        ciphertext = encrypted_data[offset:]
        
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError as e:
            raise ValueError("Decryption failed: Invalid passphrase or corrupted file")
    
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    end_time = time.perf_counter()
    decryption_time_ms = (end_time - start_time) * 1000
    
    file_hash = hashlib.sha256(plaintext).hexdigest()
    
    metadata = {
        'algorithm': algorithm,
        'file_hash': file_hash,
        'nonce': nonce.hex(),
        'tag': tag.hex(),
        'salt': salt.hex(),
        'file_size': len(plaintext),
        'decryption_time_ms': decryption_time_ms
    }
    
    return plaintext, metadata
