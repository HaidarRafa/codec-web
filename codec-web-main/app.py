"""
app.py - Main Application Flask untuk Media Codec Steganography System

Fitur:
- Kompresi standar: JPEG (gambar)
- Kompresi kustom: RLE + Huffman (lossless)
- Steganografi: LSB (Least Significant Bit) untuk gambar
- Dashboard dengan Chart.js untuk visualisasi statistik
- install requrements dengan pip install -r requirements.txt (flask, pillow, pydub, ffmpeg-python, matplotlib)
"""

import os
import json
import uuid
import datetime
from flask import Flask, render_template, request, jsonify, send_file

# ------------------------------------------------------------
# Import modul kompresi standar (JPEG)
# ------------------------------------------------------------
from compression.image_compression import compress as img_std_compress
from compression.image_compression import decompress as img_std_decompress

# ------------------------------------------------------------
# Import modul kompresi kustom (RLE + Huffman)
# ------------------------------------------------------------
from codec.image_codec import compress as img_custom_compress
from codec.image_codec import decompress as img_custom_decompress

# ------------------------------------------------------------
# Import modul steganografi LSB
# ------------------------------------------------------------
from codec.steganography.image_stego import encode as img_stego_encode
from codec.steganography.image_stego import decode as img_stego_decode

# ------------------------------------------------------------
# Konfigurasi Flask
# ------------------------------------------------------------
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max 100MB upload

# Folder untuk menyimpan file upload dan output
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('static', 'uploads')
HISTORY_FILE = os.path.join(BASE_DIR, 'history.json')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ------------------------------------------------------------
# Fungsi Bantuan (Utility)
# ------------------------------------------------------------
def save_upload(file_storage):
    """
    Simpan file upload ke folder static/uploads dengan nama unik.

    Parameters:
        file_storage: FileStorage object dari request.files

    Returns:
        str: Path lengkap file yang tersimpan
    """
    ext = os.path.splitext(file_storage.filename)[1] if file_storage.filename else '.bin'
    filename = str(uuid.uuid4()) + ext
    path = os.path.join(UPLOAD_FOLDER, filename)
    file_storage.save(path)
    return path


def result_path(ext='.bin'):
    """
    Generate path untuk file hasil/output dengan nama unik.

    Parameters:
        ext (str): Ekstensi file output

    Returns:
        str: Path lengkap file output
    """
    filename = str(uuid.uuid4()) + ext
    return os.path.join(UPLOAD_FOLDER, filename)


def add_history(media, method, original_size, compressed_size, ratio):
    """
    Catat riwayat kompresi ke file history.json untuk dashboard.

    Parameters:
        media (str): Tipe media ('image')
        method (str): Metode kompresi ('JPEG', 'MP3', 'H.264', 'RLE+Huffman')
        original_size (int): Ukuran file asli dalam bytes
        compressed_size (int): Ukuran file setelah kompresi
        ratio (float): Persentase kompresi
    """
    entry = {
        'media': media,
        'method': method,
        'original_size': original_size,
        'compressed_size': compressed_size,
        'ratio': ratio,
        'timestamp': datetime.datetime.now().isoformat()
    }
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        else:
            history = []
        history.append(entry)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass  # Abaikan error history


# ------------------------------------------------------------
# ROUTES: Halaman (Page Routes)
# ------------------------------------------------------------
@app.route('/')
def index():
    """Redirect root ke dashboard."""
    return render_template('dashboard.html', active_page='dashboard')


@app.route('/dashboard')
def dashboard():
    """Halaman dashboard dengan statistik dan Chart.js."""
    return render_template('dashboard.html', active_page='dashboard')


@app.route('/image')
def image_page():
    """Halaman Image Codec & Steganography."""
    return render_template('image.html', active_page='image')


# ------------------------------------------------------------
# API: Dashboard Stats
# ------------------------------------------------------------
@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """
    API untuk data dashboard:
    - Total file, rata-rata ratio, total ukuran
    - Data grafik per media type
    - Riwayat lengkap
    """
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        else:
            history = []
    except Exception:
        history = []

    # Hitung statistik global
    total_files = len(history)
    total_original = sum(item['original_size'] for item in history)
    total_compressed = sum(item['compressed_size'] for item in history)
    avg_ratio = round(
        sum(item['ratio'] for item in history) / total_files, 2
    ) if total_files > 0 else 0

    # Data untuk bar chart (per media type)
    media_types = ['image']
    size_data = []
    media_data = []

    for media in media_types:
        items = [h for h in history if h['media'] == media]
        if items:
            size_data.append({
                'media': media.capitalize(),
                'original': sum(h['original_size'] for h in items),
                'compressed': sum(h['compressed_size'] for h in items)
            })
            media_data.append({
                'media': media.capitalize(),
                'count': len(items)
            })

    return jsonify({
        'success': True,
        'total_files': total_files,
        'total_original': total_original,
        'total_compressed': total_compressed,
        'avg_ratio': avg_ratio,
        'size_data': size_data,
        'media_data': media_data,
        'history': history
    })


@app.route('/api/history/clear', methods=['POST'])
def api_history_clear():
    """Hapus semua riwayat kompresi."""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------
# API: IMAGE - Compress (Standard JPEG)
# ------------------------------------------------------------
@app.route('/api/image/compress_std', methods=['POST'])
def api_image_compress_std():
    """
    Kompres gambar standard menggunakan JPEG quality compression.
    Parameter: quality (1-100), default 85.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    quality = int(request.form.get('quality', 85))
    in_path = save_upload(file)

    try:
        with open(in_path, 'rb') as f:
            data = f.read()

        # Kompres dengan JPEG
        compressed = img_std_compress(data, quality=quality)
        out_path = result_path('.jpg')
        with open(out_path, 'wb') as f:
            f.write(compressed)

        orig_size = len(data)
        comp_size = len(compressed)
        ratio = round((1 - comp_size / orig_size) * 100, 2) if orig_size > 0 else 0

        # Catat ke history
        add_history('image', f'JPEG (q={quality})', orig_size, comp_size, ratio)

        return jsonify({
            'success': True,
            'file': os.path.basename(out_path),
            'original_size': orig_size,
            'compressed_size': comp_size,
            'ratio': ratio,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)


# ------------------------------------------------------------
# API: IMAGE - Compress (Custom RLE + Huffman)
# ------------------------------------------------------------
@app.route('/api/image/compress', methods=['POST'])
def api_image_compress():
    """Kompres gambar custom dengan algoritma RLE + Huffman (lossless)."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    in_path = save_upload(file)
    try:
        with open(in_path, 'rb') as f:
            data = f.read()
        compressed = img_custom_compress(data)
        out_path = result_path('.cmp')
        with open(out_path, 'wb') as f:
            f.write(compressed)
        orig_size = len(data)
        comp_size = len(compressed)
        ratio = round((1 - comp_size / orig_size) * 100, 2) if orig_size > 0 else 0

        add_history('image', 'RLE+Huffman', orig_size, comp_size, ratio)

        return jsonify({
            'success': True,
            'file': os.path.basename(out_path),
            'original_size': orig_size,
            'compressed_size': comp_size,
            'ratio': ratio,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)


# ------------------------------------------------------------
# API: IMAGE - Decompress
# ------------------------------------------------------------
@app.route('/api/image/decompress_std', methods=['POST'])
def api_image_decompress_std():
    """Dekompres gambar JPEG kembali ke PNG."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    in_path = save_upload(file)
    try:
        with open(in_path, 'rb') as f:
            data = f.read()
        decompressed = img_std_decompress(data)
        out_path = result_path('.png')
        with open(out_path, 'wb') as f:
            f.write(decompressed)
        return jsonify({
            'success': True,
            'file': os.path.basename(out_path),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)


@app.route('/api/image/decompress', methods=['POST'])
def api_image_decompress_custom():
    """Dekompres file .cmp (RLE+Huffman) kembali ke PNG."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    in_path = save_upload(file)
    try:
        with open(in_path, 'rb') as f:
            data = f.read()
        decompressed = img_custom_decompress(data)
        out_path = result_path('.png')
        with open(out_path, 'wb') as f:
            f.write(decompressed)
        return jsonify({
            'success': True,
            'file': os.path.basename(out_path),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)


# ------------------------------------------------------------
# API: IMAGE - Steganography
# ------------------------------------------------------------
@app.route('/api/image/stego/encode', methods=['POST'])
def api_image_stego_encode():
    """
    Steganografi LSB: sembunyikan pesan dalam gambar.
    Pesan disisipkan di bit terakhir setiap channel RGB.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    secret = request.form.get('message', '')
    if not secret:
        return jsonify({'error': 'No secret message provided'}), 400
    in_path = save_upload(file)
    try:
        with open(in_path, 'rb') as f:
            data = f.read()
        stego = img_stego_encode(data, secret)
        out_path = result_path('.png')
        with open(out_path, 'wb') as f:
            f.write(stego)
        return jsonify({
            'success': True,
            'file': os.path.basename(out_path),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)


@app.route('/api/image/stego/decode', methods=['POST'])
def api_image_stego_decode():
    """
    Steganografi LSB: ekstrak pesan tersembunyi dari gambar stego.
    Membaca bit terakhir setiap channel RGB untuk merekonstruksi pesan.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    in_path = save_upload(file)
    try:
        with open(in_path, 'rb') as f:
            data = f.read()
        message = img_stego_decode(data)
        return jsonify({
            'success': True,
            'message': message,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(in_path):
            os.remove(in_path)


# ------------------------------------------------------------
# API: Download File
# ------------------------------------------------------------
@app.route('/static/uploads/<filename>')
def download_file(filename):
    """Endpoint untuk mendownload file hasil processing."""
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)


# ------------------------------------------------------------
# MAIN (Run Server)
# ------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
