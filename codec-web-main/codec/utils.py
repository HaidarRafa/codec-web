"""
utils.py - Fungsi bantuan untuk format file .cmp

Menyediakan fungsi untuk membuat dan membaca header file terkompresi
dengan format kustom (.cmp) yang digunakan oleh algoritma RLE + Huffman.

Format header file .cmp:
  - 4 bytes: Magic number 'CMP1'
  - 4 bytes: Original size (unsigned int)
  - 4 bytes: Panjang metadata
  - N bytes: Metadata string (diakhiri null byte)
  - 4 bytes: Ukuran data tree Huffman
  - 4 bytes: Ukuran data terkompresi
"""

import struct

# Magic number untuk identifikasi file .cmp
MAGIC = b'CMP1'


def make_header(original_size, meta, tree_data_size, compressed_size):
    """
    Buat header untuk file .cmp.

    Parameters:
        original_size (int): Ukuran data asli (sebelum kompresi)
        meta (str): Metadata string (contoh: '1920x1080' untuk gambar)
        tree_data_size (int): Ukuran data tree Huffman
        compressed_size (int): Ukuran data terkompresi

    Returns:
        bytes: Header lengkap
    """
    # Pack magic number + original size + panjang metadata
    header = struct.pack('<4sII', MAGIC, original_size, len(meta))
    # Tambahkan metadata string + null terminator
    header += meta.encode('utf-8') + b'\x00'
    # Pack ukuran tree + ukuran compressed data
    header += struct.pack('<II', tree_data_size, compressed_size)
    return header


def parse_header(data):
    """
    Baca dan parse header dari file .cmp.

    Parameters:
        data (bytes): Seluruh data file .cmp

    Returns:
        dict: Informasi header (original_size, meta, tree_data_size,
              compressed_size, header_end)
    """
    offset = 0

    # Baca magic number dan validasi
    magic = data[:4]
    if magic != MAGIC:
        raise ValueError('Not a valid compressed file')
    offset += 4

    # Baca original size
    original_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4

    # Baca panjang metadata
    meta_len = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4

    # Baca metadata string (sampai null byte)
    meta_end = data.find(b'\x00', offset)
    meta = data[offset:meta_end].decode('utf-8')
    offset = meta_end + 1

    # Baca ukuran tree data
    tree_data_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4

    # Baca ukuran compressed data
    compressed_size = struct.unpack('<I', data[offset:offset+4])[0]
    offset += 4

    return {
        'original_size': original_size,
        'meta': meta,
        'tree_data_size': tree_data_size,
        'compressed_size': compressed_size,
        'header_end': offset,  # Posisi awal data setelah header
    }
