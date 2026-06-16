"""
audio_codec.py - Kompresi Audio Kustom (RLE + Huffman)

Menggunakan kombinasi RLE dan Huffman Coding untuk kompresi
audio WAV lossless. File hasil berekstensi .cmp.

Alur kompresi:
  1. Baca file WAV (sample rate, channels, sample width)
  2. Konversi sample ke numpy array
  3. RLE encode sample data
  4. Huffman encode hasil RLE
  5. Simpan header + tree + compressed + padding
"""

import wave
import io
import struct
import numpy as np
from .huffman import huffman_compress, huffman_decompress
from .rle import rle_encode, rle_decode
from .utils import MAGIC, make_header, parse_header


def compress(audio_bytes):
    """
    Kompres audio WAV menggunakan RLE + Huffman coding.

    Parameters:
        audio_bytes (bytes): Data audio WAV input

    Returns:
        bytes: File .cmp terkompresi
    """
    # Baca file WAV untuk mendapatkan parameter audio
    with wave.open(io.BytesIO(audio_bytes), 'rb') as wav:
        nchannels = wav.getnchannels()    # Mono(1) / Stereo(2)
        sampwidth = wav.getsampwidth()    # Bytes per sample (1/2/4)
        framerate = wav.getframerate()    # Sample rate (Hz)
        nframes = wav.getnframes()        # Jumlah frame
        frames = wav.readframes(nframes)  # Raw frame data

    # Konversi sample bytes ke array numpy
    dtype = np.int16 if sampwidth == 2 else np.int8
    samples = np.frombuffer(frames, dtype=dtype)
    raw_bytes = samples.tobytes()

    # Kompresi: RLE -> Huffman
    rle_data = rle_encode(raw_bytes)
    compressed, padding, tree_data, _ = huffman_compress(rle_data)

    # Metadata: parameter audio untuk rekonstruksi WAV
    meta = f'{nchannels},{sampwidth},{framerate},{nframes}'
    header = make_header(len(raw_bytes), meta, len(tree_data), len(compressed))

    # Gabungkan header + tree + compressed + padding
    out = bytearray()
    out.extend(header)
    out.extend(tree_data)
    out.extend(compressed)
    out.extend(struct.pack('<B', padding))

    return bytes(out)


def decompress(file_bytes):
    """
    Dekompres file .cmp audio kembali ke WAV.

    Parameters:
        file_bytes (bytes): Data file .cmp

    Returns:
        bytes: Data audio WAV hasil dekompresi
    """
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

    # Parse metadata untuk parameter WAV
    parts = info['meta'].split(',')
    nchannels = int(parts[0])
    sampwidth = int(parts[1])
    framerate = int(parts[2])
    nframes = int(parts[3])

    # Sesuaikan panjang data dengan expected size
    expected = nframes * nchannels * sampwidth
    if len(raw_bytes) < expected:
        raw_bytes = raw_bytes + b'\x00' * (expected - len(raw_bytes))
    elif len(raw_bytes) > expected:
        raw_bytes = raw_bytes[:expected]

    # Rekonstruksi file WAV
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav:
        wav.setnchannels(nchannels)
        wav.setsampwidth(sampwidth)
        wav.setframerate(framerate)
        wav.writeframes(raw_bytes)

    return buf.getvalue()
