"""
video_codec.py - Kompresi Video Kustom (Frame Diff + RLE + Huffman)

Menggunakan Frame Differencing untuk mendeteksi perubahan antar frame,
kemudian mengompresi perbedaan tersebut dengan RLE + Huffman Coding.

Alur kompresi:
  1. Baca video frame per frame menggunakan OpenCV
  2. Frame pertama: simpan sebagai grayscale reference
  3. Frame berikutnya: hitung perbedaan (absdiff) dari frame sebelumnya
  4. RLE + Huffman encode data perbedaan
  5. Simpan header + tree + compressed + padding

File hasil berekstensi .cmp (lossless).
"""

import io
import numpy as np
import struct
from .huffman import huffman_compress, huffman_decompress
from .rle import rle_encode, rle_decode
from .utils import MAGIC, make_header, parse_header

try:
    import cv2
    HAVE_CV2 = True
except ImportError:
    HAVE_CV2 = False


def _frame_diff(prev_frame, curr_frame):
    """Hitung absolute difference antara dua frame grayscale."""
    return cv2.absdiff(prev_frame, curr_frame)


def compress(video_bytes):
    """
    Kompres video menggunakan Frame Differencing + RLE + Huffman.

    Parameters:
        video_bytes (bytes): Data video AVI input

    Returns:
        bytes: File .cmp terkompresi
    """
    if not HAVE_CV2:
        raise RuntimeError('OpenCV (cv2) is not installed')

    # Simpan input video ke file temporary
    temp_path = io.BytesIO(video_bytes)
    temp_path.seek(0)
    tmpfile = 'temp_video_input.avi'
    with open(tmpfile, 'wb') as f:
        f.write(temp_path.read())

    # Buka video dengan OpenCV
    cap = cv2.VideoCapture(tmpfile)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    all_data = bytearray()

    # Baca frame pertama sebagai reference (grayscale)
    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        cv2.destroyAllWindows()
        return b''

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    all_data.extend(prev_gray.tobytes())

    # Proses frame-frame berikutnya
    frame_count = 1
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = _frame_diff(prev_gray, gray)  # Perbedaan antar frame
        diff_bytes = diff.tobytes()
        all_data.extend(diff_bytes)
        prev_gray = gray
        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    # Kompresi: RLE -> Huffman
    raw_bytes = bytes(all_data)
    rle_data = rle_encode(raw_bytes)
    compressed, padding, tree_data, _ = huffman_compress(rle_data)

    # Metadata: dimensi, fps, jumlah frame
    meta = f'{width}x{height}x{fps:.2f}x{frame_count}'
    header = make_header(len(raw_bytes), meta, len(tree_data), len(compressed))

    # Gabungkan dan return
    out = bytearray()
    out.extend(header)
    out.extend(tree_data)
    out.extend(compressed)
    out.extend(struct.pack('<B', padding))

    import os
    os.remove(tmpfile)
    return bytes(out)


def decompress(file_bytes):
    """
    Dekompres file .cmp video kembali ke AVI.

    Parameters:
        file_bytes (bytes): Data file .cmp

    Returns:
        bytes: Data video AVI hasil dekompresi
    """
    if not HAVE_CV2:
        raise RuntimeError('OpenCV (cv2) is not installed')

    # Parse header
    info = parse_header(file_bytes)
    offset = info['header_end']

    # Baca tree data
    tree_data = file_bytes[offset:offset + info['tree_data_size']]
    offset += info['tree_data_size']

    # Baca compressed data
    compressed = file_bytes[offset:offset + info['compressed_size']]
    offset += info['compressed_size']

    # Baca padding
    padding = struct.unpack('<B', file_bytes[offset:offset+1])[0]

    # Dekompresi: Huffman -> RLE
    rle_data = huffman_decompress(compressed, padding, tree_data)
    raw_bytes = rle_decode(rle_data)

    # Baca metadata
    parts = info['meta'].split('x')
    width = int(parts[0])
    height = int(parts[1])
    fps = float(parts[2])
    total_frames = int(parts[3])

    # Rekonstruksi dimensi
    frame_size = width * height
    if len(raw_bytes) < frame_size * total_frames:
        raw_bytes = raw_bytes + b'\x00' * (frame_size * total_frames - len(raw_bytes))

    # Tulis video output frame per frame
    out_path = 'temp_video_output.avi'
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height), isColor=False)

    offset_ptr = 0
    for i in range(total_frames):
        frame_bytes = raw_bytes[offset_ptr:offset_ptr + frame_size]
        offset_ptr += frame_size
        frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape((height, width))
        out_writer.write(frame)

    out_writer.release()

    # Baca hasil video
    with open(out_path, 'rb') as f:
        result = f.read()

    import os
    os.remove(out_path)
    return result
