"""
image_codec.py - Kompresi Gambar Kustom (RLE + Huffman)

Menggunakan kombinasi RLE (Run-Length Encoding) dan Huffman Coding
untuk kompresi gambar lossless. File hasil berekstensi .cmp.

Alur kompresi:
  1. Baca pixel gambar (RGB)
  2. RLE encode pixel data
  3. Huffman encode hasil RLE
  4. Simpan header + tree + compressed + padding ke file .cmp
"""

from PIL import Image
import io
import struct
from .huffman import huffman_compress, huffman_decompress
from .rle import rle_encode, rle_decode
from .utils import MAGIC, make_header, parse_header


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

    # Kompresi: RLE -> Huffman
    rle_data = rle_encode(pixels)
    compressed, padding, tree_data, _ = huffman_compress(rle_data)

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

    # Dekompresi: Huffman -> RLE -> pixel data
    rle_data = huffman_decompress(compressed, padding, tree_data)
    pixels = rle_decode(rle_data)

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
