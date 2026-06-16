"""
image_compression.py - Kompresi Gambar dengan JPEG Standard

Menggunakan library Pillow untuk melakukan kompresi gambar
ke format JPEG dengan parameter quality yang bisa diatur.
Ini adalah metode kompresi lossy standar industri.
"""

from PIL import Image
import io


def compress(image_bytes, quality=85):
    """
    Kompres gambar menggunakan JPEG quality compression.

    Parameters:
        image_bytes (bytes): Data gambar input (PNG, BMP, JPEG, dll.)
        quality (int): Kualitas JPEG (1-100). Semakin rendah,
                      semakin kecil ukuran tapi kualitas turun.

    Returns:
        bytes: Data gambar terkompresi dalam format JPEG.
    """
    # Buka gambar dari byte stream
    img = Image.open(io.BytesIO(image_bytes))

    # Konversi ke RGB jika perlu (JPEG tidak support alpha channel)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # Simpan ke buffer sebagai JPEG dengan quality tertentu
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def decompress(image_bytes):
    """
    Dekompres gambar JPEG kembali ke format PNG (lossless).

    Parameters:
        image_bytes (bytes): Data gambar JPEG.

    Returns:
        bytes: Data gambar dalam format PNG.
    """
    # Buka gambar JPEG dari byte stream
    img = Image.open(io.BytesIO(image_bytes))

    # Simpan ke buffer sebagai PNG (lossless)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
