"""
image_codec.py - Kompresi Gambar Kustom (Delta + Huffman)

Menggunakan Delta prediction + Huffman Coding
untuk kompresi gambar lossless. File hasil berekstensi .cmp.

Alur kompresi:
  1. Baca pixel gambar (RGB)
  2. Delta encode pixel data (selisih antar pixel berurutan)
  3. Huffman encode hasil delta
  4. Simpan header + tree + compressed + padding ke file .cmp
"""

from PIL import Image
import io
import struct
from .huffman import huffman_compress, huffman_decompress
from .utils import MAGIC, make_header, parse_header


def _delta_encode(data):
    """Encode data with delta prediction (difference from previous byte)."""
    result = bytearray(len(data))
    result[0] = data[0]
    for i in range(1, len(data)):
        result[i] = (data[i] - data[i - 1]) & 0xFF
    return bytes(result)


def _delta_decode(data):
    """Decode delta-encoded data back to original."""
    result = bytearray(len(data))
    result[0] = data[0]
    for i in range(1, len(data)):
        result[i] = (data[i] + result[i - 1]) & 0xFF
    return bytes(result)


def compress(image_bytes):
    """
    Kompres gambar menggunakan RLE + Huffman coding.

    Parameters:
        image_bytes (bytes): Data gambar input (PNG, BMP, dll.)

    Returns:
        bytes: File .cmp terkompresi
    """
    # Buka gambar dan konversi ke RGB
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Ambil dimensi dan pixel data
    width, height = img.size
    pixels = list(img.tobytes())

    # Kompresi: Delta -> Huffman
    delta_data = _delta_encode(pixels)
    compressed, padding, tree_data, _ = huffman_compress(delta_data)

    # Metadata: dimensi gambar
    meta = f'{width}x{height}'
    header = make_header(len(pixels), meta, len(tree_data), len(compressed))

    # Gabungkan header + tree + compressed + padding
    out = bytearray()
    out.extend(header)
    out.extend(tree_data)
    out.extend(compressed)
    out.extend(struct.pack('<B', padding))

    return bytes(out)


def decompress(file_bytes):
    """
    Dekompres file .cmp kembali ke gambar PNG.

    Parameters:
        file_bytes (bytes): Data file .cmp

    Returns:
        bytes: Data gambar PNG hasil dekompresi
    """
    # Parse header untuk mendapatkan metadata
    info = parse_header(file_bytes)
    offset = info['header_end']

    # Baca tree data Huffman
    tree_data = file_bytes[offset:offset + info['tree_data_size']]
    offset += info['tree_data_size']

    # Baca data terkompresi
    compressed = file_bytes[offset:offset + info['compressed_size']]
    offset += info['compressed_size']

    # Baca padding bits
    padding = struct.unpack('<B', file_bytes[offset:offset+1])[0]

    # Dekompresi: Huffman -> Delta -> pixel data
    delta_data = huffman_decompress(compressed, padding, tree_data)
    pixels = _delta_decode(delta_data)

    # Baca dimensi dari metadata
    parts = info['meta'].split('x')
    width, height = int(parts[0]), int(parts[1])

    # Trim jika ada kelebihan data
    if len(pixels) != width * height * 3:
        pixels = pixels[:width * height * 3]

    # Rekonstruksi gambar dan simpan sebagai PNG
    img = Image.frombytes('RGB', (width, height), bytes(pixels))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
