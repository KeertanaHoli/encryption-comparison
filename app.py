import os
from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import crypto_utils
import blockchain
import benchmark
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'storage'

ALLOWED_ALGORITHMS = ['AES-256-GCM', 'Ascon-128a', 'ChaCha20-Poly1305']

blockchain.init_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        algorithm = request.form.get('algorithm')
        passphrase = request.form.get('passphrase')
        
        if not algorithm or algorithm not in ALLOWED_ALGORITHMS:
            return jsonify({'error': 'Invalid algorithm'}), 400
        
        if not passphrase:
            return jsonify({'error': 'Passphrase is required'}), 400
        
        file_data = file.read()
        original_filename = secure_filename(file.filename)
        
        encrypted_data, metadata = crypto_utils.encrypt_file(file_data, passphrase, algorithm)
        
        encrypted_filename = f"{original_filename}.enc"
        encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encrypted', encrypted_filename)
        
        os.makedirs(os.path.dirname(encrypted_path), exist_ok=True)
        
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        blockchain.add_block(
            algorithm=metadata['algorithm'],
            file_name=original_filename,
            file_hash=metadata['file_hash'],
            nonce_b64=metadata['nonce'],
            tag_b64=metadata['tag'],
            salt_b64=metadata['salt'],
            file_size_bytes=metadata['file_size'],
            enc_time_ms=metadata['encryption_time_ms'],
            dec_time_ms=None
        )
        
        return send_file(
            encrypted_path,
            as_attachment=True,
            download_name=encrypted_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        passphrase = request.form.get('passphrase')
        
        if not passphrase:
            return jsonify({'error': 'Passphrase is required'}), 400
        
        encrypted_data = file.read()
        original_filename = secure_filename(file.filename)
        
        decrypted_data, metadata = crypto_utils.decrypt_file(encrypted_data, passphrase)
        
        decrypted_filename = original_filename.replace('.enc', '')
        if decrypted_filename == original_filename:
            decrypted_filename = f"decrypted_{original_filename}"
        
        decrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decrypted', decrypted_filename)
        
        os.makedirs(os.path.dirname(decrypted_path), exist_ok=True)
        
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_data)
        
        blockchain.add_block(
            algorithm=metadata['algorithm'],
            file_name=decrypted_filename,
            file_hash=metadata['file_hash'],
            nonce_b64=metadata['nonce'],
            tag_b64=metadata['tag'],
            salt_b64=metadata['salt'],
            file_size_bytes=metadata['file_size'],
            enc_time_ms=None,
            dec_time_ms=metadata['decryption_time_ms']
        )
        
        return send_file(
            decrypted_path,
            as_attachment=True,
            download_name=decrypted_filename,
            mimetype='application/octet-stream'
        )
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/benchmark')
def benchmark_page():
    try:
        chart_data = benchmark.generate_benchmark_chart()
        blocks = blockchain.get_all_blocks()
        return render_template('benchmark.html', chart_data=chart_data, blocks=blocks)
    except Exception as e:
        return render_template('benchmark.html', chart_data=None, blocks=[], error=str(e))

@app.route('/ledger')
def ledger_page():
    try:
        blocks = blockchain.get_all_blocks()
        return render_template('ledger.html', blocks=blocks)
    except Exception as e:
        return render_template('ledger.html', blocks=[], error=str(e))

@app.route('/verify')
def verify():
    try:
        result = blockchain.verify_blockchain()
        return jsonify(result)
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500

@app.route('/clear-chart', methods=['POST'])
def clear_chart():
    try:
        blockchain.clear_blockchain()
        return jsonify({'success': True, 'message': 'All chart data has been cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
