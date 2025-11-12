#!/usr/bin/env python3
import crypto_utils

def test_encryption_decryption():
    algorithms = ['AES-256-GCM', 'Ascon-128a', 'ChaCha20-Poly1305']
    test_data = b"This is a test file for encryption demonstration."
    passphrase = "test_passphrase_123"
    
    print("Testing encryption and decryption for all algorithms...\n")
    
    for algorithm in algorithms:
        print(f"Testing {algorithm}...")
        try:
            encrypted_data, enc_metadata = crypto_utils.encrypt_file(test_data, passphrase, algorithm)
            print(f"  ✓ Encryption successful")
            print(f"    - File size: {enc_metadata['file_size']} bytes")
            print(f"    - Encryption time: {enc_metadata['encryption_time_ms']:.2f} ms")
            print(f"    - File hash: {enc_metadata['file_hash'][:16]}...")
            
            decrypted_data, dec_metadata = crypto_utils.decrypt_file(encrypted_data, passphrase)
            print(f"  ✓ Decryption successful")
            print(f"    - Decryption time: {dec_metadata['decryption_time_ms']:.2f} ms")
            
            if decrypted_data == test_data:
                print(f"  ✓ Data integrity verified")
            else:
                print(f"  ✗ Data integrity check failed!")
                
            print()
            
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            return False
    
    print("All tests passed! ✓")
    return True

if __name__ == '__main__':
    test_encryption_decryption()
