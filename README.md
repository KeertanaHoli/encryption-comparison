# Comparative Study of File Encryption and Decryption

A Flask web application comparing three encryption algorithms: **AES-256-GCM**, **Ascon-128a**, and **ChaCha20-Poly1305**.

## Features

- **File Encryption/Decryption**: Upload files, choose algorithm, and encrypt/decrypt with passphrase
- **Blockchain Ledger**: All operations recorded in an immutable blockchain with integrity verification
- **Performance Benchmarks**: Automated charts comparing encryption/decryption times and file sizes
- **Three Algorithms**:
  - AES-256-GCM (Advanced Encryption Standard)
  - Ascon-128a (Lightweight authenticated encryption)
  - ChaCha20-Poly1305 (Stream cipher with authentication)

## Security Features

- PBKDF2 key derivation (200,000 iterations, SHA-256)
- Random salt generation for each encryption
- Authenticated encryption with associated data (AEAD)
- Blockchain ledger for tamper detection
- Passphrases never stored

## Technology Stack

- Python 3.11+
- Flask
- pycryptodome
- ascon
- matplotlib
- pandas
- SQLite

## Usage

1. **Encrypt File**: Upload file → Select algorithm → Enter passphrase → Download encrypted file
2. **Decrypt File**: Upload encrypted file → Enter passphrase → Download decrypted file
3. **View Benchmarks**: Automatically generated charts from blockchain data
4. **Verify Ledger**: Check blockchain integrity

## File Structure

```
├── app.py                 # Flask application
├── crypto_utils.py        # Encryption/decryption logic
├── blockchain.py          # Blockchain ledger
├── benchmark.py           # Chart generation
├── templates/            # HTML templates
├── storage/              # Encrypted/decrypted files
└── ledger.db             # SQLite blockchain database
```

## Educational Purpose

This application is for educational purposes to demonstrate and compare cryptographic algorithms. Not for production use.
