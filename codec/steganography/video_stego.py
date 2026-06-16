"""
video_stego.py - Steganografi LSB untuk Video

LSB pada video menyembunyikan pesan rahasia pada bit terakhir
dari setiap channel pixel (B, G, R) di setiap frame video.
Karena setiap frame memiliki ribuan pixel, kapasitas penyimpanan
video steganografi sangat besar.

Format penyisipan:
  - 4 byte pertama: panjang pesan (32-bit little-endian)
  - Byte berikutnya: isi pesan (UTF-8)
  - Bit disisipkan secara sekuensial dari frame pertama hingga pesan habis
"""

import io
import numpy as np

try:
    import cv2
    HAVE_CV2 = True
except ImportError:
    HAVE_CV2 = False


def encode(video_bytes, secret_text):
    """
    Sembunyikan pesan rahasia dalam video menggunakan LSB.

    Parameters:
        video_bytes (bytes): Data video AVI cover
        secret_text (str): Pesan rahasia

    Returns:
        bytes: Data video AVI stego (berisi pesan tersembunyi)
    """
    if not HAVE_CV2:
        raise RuntimeError('OpenCV (cv2) is not installed')

    # Simpan input video ke file temporary
    temp_path = io.BytesIO(video_bytes)
    temp_path.seek(0)
    tmpfile = 'temp_video_stego_input.avi'
    with open(tmpfile, 'wb') as f:
        f.write(temp_path.read())

    # Baca parameter video
    cap = cv2.VideoCapture(tmpfile)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Siapkan payload bits
    text_bytes = secret_text.encode('utf-8')
    header = len(text_bytes).to_bytes(4, 'little')
    payload = bytearray(header + text_bytes)

    payload_bits = []
    for b in payload:
        payload_bits.extend([(b >> i) & 1 for i in range(8)])

    # Kapasitas = total pixel * 3 channel
    max_bits = total_frames * width * height * 3
    if len(payload_bits) > max_bits:
        raise ValueError(
            f'Message too long for this video (max {max_bits // 8} bytes)'
        )

    # Buat video writer
    out_path = 'temp_video_stego_output.avi'
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out_writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    bit_idx = 0  # Index bit payload saat ini
    frame_count = 0

    # Proses setiap frame video
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Sisipkan bit ke frame ini selama masih ada bit payload
        if bit_idx < len(payload_bits):
            flat = frame.flatten()
            bytes_to_mod = min(len(payload_bits) - bit_idx, len(flat))
            for i in range(bytes_to_mod):
                flat[i] = (flat[i] & 0xFE) | payload_bits[bit_idx + i]
            bit_idx += bytes_to_mod
            frame = flat.reshape((height, width, 3)).astype(np.uint8)

        out_writer.write(frame)
        frame_count += 1

    cap.release()
    out_writer.release()

    # Baca hasil video stego
    with open(out_path, 'rb') as f:
        result = f.read()

    import os
    os.remove(tmpfile)
    os.remove(out_path)
    return result


def decode(video_bytes):
    """
    Ekstrak pesan rahasia dari video stego.

    Parameters:
        video_bytes (bytes): Data video AVI stego

    Returns:
        str: Pesan rahasia yang ditemukan
    """
    if not HAVE_CV2:
        raise RuntimeError('OpenCV (cv2) is not installed')

    # Simpan video ke file temporary
    temp_path = io.BytesIO(video_bytes)
    temp_path.seek(0)
    tmpfile = 'temp_video_stego_decode.avi'
    with open(tmpfile, 'wb') as f:
        f.write(temp_path.read())

    # Baca video frame per frame
    cap = cv2.VideoCapture(tmpfile)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    bits = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        flat = frame.flatten()
        for i in range(min(len(flat), width * height * 3)):
            bits.append(flat[i] & 1)

    cap.release()

    if len(bits) < 32:
        raise ValueError('Video too short to contain a message')

    # Baca 32 bit pertama = panjang pesan
    msg_len = 0
    for j in range(32):
        msg_len |= bits[j] << (j % 8)

    if msg_len <= 0 or msg_len > (len(bits) // 8) - 4:
        raise ValueError('No hidden message found or message corrupted')

    # Baca bit-bit pesan
    total_bits = 32 + msg_len * 8
    if total_bits > len(bits):
        raise ValueError('Message corrupted or too short')

    msg_bits = bits[32:total_bits]

    # Konversi bit ke string
    chars = bytearray()
    for i in range(0, len(msg_bits), 8):
        if i + 8 > len(msg_bits):
            break
        byte = 0
        for j in range(8):
            byte |= msg_bits[i + j] << j
        chars.append(byte)

    import os
    os.remove(tmpfile)
    return chars.decode('utf-8', errors='replace')
