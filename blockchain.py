import sqlite3
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_FILE = 'ledger.db'

def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            index_num INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            tx_hash TEXT NOT NULL,
            algorithm TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            nonce_b64 TEXT NOT NULL,
            tag_b64 TEXT NOT NULL,
            salt_b64 TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            enc_time_ms REAL,
            dec_time_ms REAL
        )
    ''')
    
    conn.commit()
    conn.close()

def calculate_hash(block_data: Dict) -> str:
    block_string = json.dumps(block_data, sort_keys=True)
    return hashlib.sha256(block_string.encode()).hexdigest()

def get_last_block() -> Optional[Dict]:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM blockchain ORDER BY index_num DESC LIMIT 1')
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'index_num': row[1],
            'timestamp': row[2],
            'prev_hash': row[3],
            'tx_hash': row[4],
            'algorithm': row[5],
            'file_name': row[6],
            'file_hash': row[7],
            'nonce_b64': row[8],
            'tag_b64': row[9],
            'salt_b64': row[10],
            'file_size_bytes': row[11],
            'enc_time_ms': row[12],
            'dec_time_ms': row[13]
        }
    return None

def add_block(
    algorithm: str,
    file_name: str,
    file_hash: str,
    nonce_b64: str,
    tag_b64: str,
    salt_b64: str,
    file_size_bytes: int,
    enc_time_ms: Optional[float] = None,
    dec_time_ms: Optional[float] = None
) -> Dict:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    last_block = get_last_block()
    
    if last_block is None:
        index_num = 0
        prev_hash = '0' * 64
    else:
        index_num = last_block['index_num'] + 1
        prev_hash = last_block['tx_hash']
    
    timestamp = datetime.utcnow().isoformat()
    
    block_data = {
        'index_num': index_num,
        'timestamp': timestamp,
        'prev_hash': prev_hash,
        'algorithm': algorithm,
        'file_name': file_name,
        'file_hash': file_hash,
        'nonce_b64': nonce_b64,
        'tag_b64': tag_b64,
        'salt_b64': salt_b64,
        'file_size_bytes': file_size_bytes,
        'enc_time_ms': enc_time_ms,
        'dec_time_ms': dec_time_ms
    }
    
    tx_hash = calculate_hash(block_data)
    
    cursor.execute('''
        INSERT INTO blockchain (
            index_num, timestamp, prev_hash, tx_hash, algorithm,
            file_name, file_hash, nonce_b64, tag_b64, salt_b64,
            file_size_bytes, enc_time_ms, dec_time_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        index_num, timestamp, prev_hash, tx_hash, algorithm,
        file_name, file_hash, nonce_b64, tag_b64, salt_b64,
        file_size_bytes, enc_time_ms, dec_time_ms
    ))
    
    conn.commit()
    conn.close()
    
    block_data['tx_hash'] = tx_hash
    return block_data

def get_all_blocks() -> List[Dict]:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM blockchain ORDER BY index_num ASC')
    rows = cursor.fetchall()
    
    conn.close()
    
    blocks = []
    for row in rows:
        blocks.append({
            'id': row[0],
            'index_num': row[1],
            'timestamp': row[2],
            'prev_hash': row[3],
            'tx_hash': row[4],
            'algorithm': row[5],
            'file_name': row[6],
            'file_hash': row[7],
            'nonce_b64': row[8],
            'tag_b64': row[9],
            'salt_b64': row[10],
            'file_size_bytes': row[11],
            'enc_time_ms': row[12],
            'dec_time_ms': row[13]
        })
    
    return blocks

def verify_blockchain() -> Dict:
    blocks = get_all_blocks()
    
    if not blocks:
        return {'valid': True, 'message': 'Blockchain is empty'}
    
    for i, block in enumerate(blocks):
        if block['index_num'] != i:
            return {'valid': False, 'message': f'Invalid index at block {i}'}
        
        if i == 0:
            if block['prev_hash'] != '0' * 64:
                return {'valid': False, 'message': 'Genesis block has invalid prev_hash'}
        else:
            if block['prev_hash'] != blocks[i-1]['tx_hash']:
                return {'valid': False, 'message': f'Broken chain at block {i}'}
        
        block_data = {
            'index_num': block['index_num'],
            'timestamp': block['timestamp'],
            'prev_hash': block['prev_hash'],
            'algorithm': block['algorithm'],
            'file_name': block['file_name'],
            'file_hash': block['file_hash'],
            'nonce_b64': block['nonce_b64'],
            'tag_b64': block['tag_b64'],
            'salt_b64': block['salt_b64'],
            'file_size_bytes': block['file_size_bytes'],
            'enc_time_ms': block['enc_time_ms'],
            'dec_time_ms': block['dec_time_ms']
        }
        
        expected_hash = calculate_hash(block_data)
        if block['tx_hash'] != expected_hash:
            return {'valid': False, 'message': f'Invalid hash at block {i}'}
    
    return {'valid': True, 'message': f'Blockchain is valid with {len(blocks)} blocks'}

def clear_blockchain():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blockchain')
    conn.commit()
    conn.close()
