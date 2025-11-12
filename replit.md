# File Encryption Comparative Study

## Project Overview
A Flask web application for comparative study of file encryption and decryption using three cryptographic algorithms:
- **AES-256-GCM** (Advanced Encryption Standard)
- **Ascon-128a** (Lightweight authenticated encryption)
- **ChaCha20-Poly1305** (Stream cipher with authentication)

All operations are logged to an immutable blockchain ledger with automated performance benchmarking.

## Recent Changes (November 12, 2025)
- Initial project setup with complete implementation
- Created crypto_utils.py with three encryption algorithms
- Implemented blockchain.py with SQLite-based ledger
- Built benchmark.py for automated chart generation
- Created Flask app.py with all routes
- Designed purple gradient UI matching reference design
- Configured Flask workflow on port 5000
- **UPDATE**: Changed benchmark chart to show LAST file only (not averages)
- **UPDATE**: Implemented "Clear Chart" button that erases all blockchain data
- **UPDATE**: Improved button sensitivity with faster transitions and better hover effects

## Project Architecture

### Backend Structure
- **app.py**: Flask application with routes (/, /encrypt, /decrypt, /benchmark, /ledger, /verify)
- **crypto_utils.py**: Encryption/decryption logic for all three algorithms
- **blockchain.py**: SQLite-based blockchain ledger with integrity verification
- **benchmark.py**: Matplotlib chart generation from blockchain data

### Frontend
- **index.html**: Main page with encrypt/decrypt forms
- **benchmark.html**: Performance comparison charts
- **ledger.html**: Blockchain transaction viewer
- Purple gradient UI (Bootstrap 5)

### Data Storage
- **ledger.db**: SQLite blockchain database
- **storage/encrypted/**: Encrypted files
- **storage/decrypted/**: Decrypted files

## Security Implementation
- PBKDF2 key derivation (200,000 iterations, SHA-256)
- Random salt generation per encryption
- Authenticated encryption (AEAD)
- Metadata embedded in encrypted file headers
- Blockchain ledger for tamper detection
- No passphrase storage

## Key Features
1. File encryption/decryption with three algorithms
2. Automatic blockchain logging of all operations
3. Real-time performance benchmarking with charts
4. Blockchain integrity verification
5. Purple gradient UI matching design specifications

## Technology Stack
- Python 3.11
- Flask (web framework)
- pycryptodome (AES, ChaCha20)
- ascon (Ascon-128a)
- matplotlib (charts)
- pandas (data processing)
- SQLite3 (blockchain storage)
- Bootstrap 5 (UI)

## Environment
- Port: 5000 (webview)
- Session secret stored in SESSION_SECRET environment variable
- Max file upload: 50MB

## User Preferences
N/A - Initial implementation

## Educational Purpose
This application is designed for educational purposes to demonstrate and compare cryptographic algorithms. Not intended for production use.
