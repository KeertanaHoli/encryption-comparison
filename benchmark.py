import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from blockchain import get_all_blocks

def generate_benchmark_chart() -> str:
    blocks = get_all_blocks()
    
    if not blocks:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No data available yet.\nEncrypt or decrypt files to see benchmarks.',
                ha='center', va='center', fontsize=14, color='#666')
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f'data:image/png;base64,{img_base64}'
    
    latest_data = {}
    
    for block in reversed(blocks):
        algo = block['algorithm']
        
        if algo not in latest_data:
            latest_data[algo] = {
                'Algorithm': algo,
                'Encryption Time (ms)': 0,
                'Decryption Time (ms)': 0,
                'File Size (KB)': 0
            }
        
        if block['enc_time_ms'] is not None and latest_data[algo]['Encryption Time (ms)'] == 0:
            latest_data[algo]['Encryption Time (ms)'] = block['enc_time_ms']
            latest_data[algo]['File Size (KB)'] = block['file_size_bytes'] / 1024
        
        if block['dec_time_ms'] is not None and latest_data[algo]['Decryption Time (ms)'] == 0:
            latest_data[algo]['Decryption Time (ms)'] = block['dec_time_ms']
            if latest_data[algo]['File Size (KB)'] == 0:
                latest_data[algo]['File Size (KB)'] = block['file_size_bytes'] / 1024
    
    agg_data = pd.DataFrame(list(latest_data.values()))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    algorithms = agg_data['Algorithm'].tolist()
    enc_times = agg_data['Encryption Time (ms)'].tolist()
    dec_times = agg_data['Decryption Time (ms)'].tolist()
    
    x_pos = range(len(algorithms))
    width = 0.35
    
    colors_enc = ['#667eea', '#764ba2', '#f093fb']
    colors_dec = ['#4facfe', '#00f2fe', '#43e97b']
    
    bars1 = ax1.bar([p - width/2 for p in x_pos], enc_times, width, 
                     label='Encryption', color=colors_enc[:len(algorithms)], alpha=0.8)
    bars2 = ax1.bar([p + width/2 for p in x_pos], dec_times, width,
                     label='Decryption', color=colors_dec[:len(algorithms)], alpha=0.8)
    
    ax1.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Time (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('Encryption/Decryption Performance', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(algorithms, rotation=15, ha='right')
    ax1.legend(loc='upper left')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    file_sizes = agg_data['File Size (KB)'].tolist()
    bars3 = ax2.bar(x_pos, file_sizes, color=colors_enc[:len(algorithms)], alpha=0.8)
    
    ax2.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
    ax2.set_ylabel('File Size (KB)', fontsize=12, fontweight='bold')
    ax2.set_title('File Size Processed', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(algorithms, rotation=15, ha='right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar in bars3:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f'data:image/png;base64,{img_base64}'
