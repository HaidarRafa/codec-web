"""
image_stego.py - Steganografi LSB untuk Gambar

Least Significant Bit (LSB) adalah teknik steganografi yang menyembunyikan
pesan rahasia pada bit terakhir (least significant bit) dari setiap
channel warna pixel (R, G, B).

Konsep:
  - Pixel RGB memiliki 3 byte (R, G, B), masing-masing 8 bit
  - Bit terakhir (LSB) dari setiap byte bisa dimodifikasi
  - Perubahan LSB tidak terlihat oleh mata manusia
  - Contoh: pixel (255, 128, 64) -> (254, 129, 64) perubahan tidak kasat mata

Format penyisipan:
  - 4 byte pertama: panjang pesan (32-bit little-endian)
  - Byte berikutnya: isi pesan (UTF-8)
"""

from PIL import Image
import io


def _text_to_bits(text):
    """Konversi string teks ke array bit (integer 0/1)."""
    bits = []
    for char in text.encode('utf-8'):
        # Ambil setiap bit dari byte (LSB first)
        bits.extend([(char >> i) & 1 for i in range(8)])
    return bits


def _bits_to_text(bits):
    """Konversi array bit kembali ke string teks."""
    chars = bytearray()
    for i in range(0, len(bits), 8):
        if i + 8 > len(bits):
            break
        byte = 0
        # Rekonstruksi byte dari bit (LSB first)
        for j in range(8):
            byte |= bits[i + j] << j
        chars.append(byte)
    return chars.decode('utf-8', errors='replace')


def encode(image_bytes, secret_text):
    """
    Sembunyikan pesan rahasia dalam gambar menggunakan LSB.

    Parameters:
        image_bytes (bytes): Data gambar cover (tempat pesan disembunyikan)
        secret_text (str): Pesan rahasia yang akan disembunyikan

    Returns:
        bytes: Data gambar stego (berisi pesan tersembunyi) dalam format PNG
    """
    # Buka gambar dan konversi ke RGB
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = bytearray(img.tobytes())

    # Siapkan payload: 4 byte header (panjang pesan) + isi pesan
    text_bytes = secret_text.encode('utf-8')
    header = len(text_bytes).to_bytes(4, 'little')  # 32-bit length
    payload = bytearray(header + text_bytes)

    # Konversi payload ke array bit
    payload_bits = []
    for b in payload:
        payload_bits.extend([(b >> i) & 1 for i in range(8)])

    # Validasi kapasitas: setiap pixel byte bisa nyimpan 1 bit
    max_bits = len(pixels)
    if len(payload_bits) > max_bits:
        raise ValueError(
            f'Message too long for this image (max {max_bits // 8} bytes)'
        )

    # Sisipkan setiap bit payload ke LSB pixel
    for i in range(len(payload_bits)):
        # Clear LSB: pixel & 0xFE, lalu set dengan payload bit
        pixels[i] = (pixels[i] & 0xFE) | payload_bits[i]

    # Simpan gambar stego sebagai PNG
    img_stego = Image.frombytes('RGB', img.size, bytes(pixels))
    buf = io.BytesIO()
    img_stego.save(buf, format='PNG')
    return buf.getvalue()


def decode(image_bytes):
    """
    Ekstrak pesan rahasia dari gambar stego.

    Parameters:
        image_bytes (bytes): Data gambar stego (berisi pesan tersembunyi)

    Returns:
        str: Pesan rahasia yang ditemukan
    """
    # Buka gambar
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = list(img.tobytes())

    # Baca 32 bit pertama = panjang pesan (LSB dari 32 pixel pertama)
    msg_len_bits = [pixels[i] & 1 for i in range(32)]
    msg_len = 0
    for j in range(32):
        msg_len |= msg_len_bits[j] << (j % 8)

    # Validasi panjang pesan
    if msg_len <= 0 or msg_len > (len(pixels) // 8) - 4:
        raise ValueError('No hidden message found or message corrupted')

    # Baca bit-bit pesan
    total_bits = 32 + msg_len * 8
    if total_bits > len(pixels):
        raise ValueError('Message corrupted or too short')

    bits = [pixels[i] & 1 for i in range(32, total_bits)]
    return _bits_to_text(bits)
