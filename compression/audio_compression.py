"""
audio_compression.py - Kompresi Audio dengan MP3 Standard

Menggunakan library pydub (wrapper FFmpeg) untuk mengkonversi
audio WAV ke MP3 dengan parameter bitrate yang bisa diatur.
Metode kompresi lossy standar industri untuk audio.
"""

import io
import subprocess
import tempfile
import os


def compress(audio_bytes, bitrate='128k'):
    """
    Kompres audio WAV ke MP3 menggunakan FFmpeg dengan bitrate tertentu.

    Parameters:
        audio_bytes (bytes): Data audio WAV input.
        bitrate (str): Bitrate MP3, contoh: '64k', '128k', '192k', '320k'.
                       Semakin rendah bitrate, semakin kecil ukuran.

    Returns:
        bytes: Data audio MP3 terkompresi.
    """
    # Buat file temporary untuk input WAV
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_in:
        tmp_in.write(audio_bytes)
        tmp_in_path = tmp_in.name

    # Buat file temporary untuk output MP3
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_out:
        tmp_out_path = tmp_out.name

    try:
        # Jalankan FFmpeg: WAV -> MP3 dengan bitrate tertentu
        cmd = [
            'ffmpeg', '-y',                  # overwrite output
            '-i', tmp_in_path,               # input file
            '-b:a', bitrate,                 # audio bitrate
            '-q:a', '2',                     # quality (2 = high quality)
            tmp_out_path
        ]
        # Jalankan proses, tangkap error output
        result = subprocess.run(
            cmd, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f'FFmpeg error: {result.stderr}'
            )

        # Baca hasil MP3 dari file temporary
        with open(tmp_out_path, 'rb') as f:
            compressed = f.read()

        return compressed

    finally:
        # Bersihkan file temporary
        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.remove(tmp_out_path)


def decompress(audio_bytes):
    """
    Dekompres audio MP3 kembali ke WAV menggunakan FFmpeg.

    Parameters:
        audio_bytes (bytes): Data audio MP3 input.

    Returns:
        bytes: Data audio WAV (uncompressed).
    """
    # Buat file temporary untuk input MP3
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_in:
        tmp_in.write(audio_bytes)
        tmp_in_path = tmp_in.name

    # Buat file temporary untuk output WAV
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_out:
        tmp_out_path = tmp_out.name

    try:
        # Jalankan FFmpeg: MP3 -> WAV
        cmd = [
            'ffmpeg', '-y',
            '-i', tmp_in_path,
            tmp_out_path
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f'FFmpeg error: {result.stderr}'
            )

        # Baca hasil WAV
        with open(tmp_out_path, 'rb') as f:
            decompressed = f.read()

        return decompressed

    finally:
        # Bersihkan file temporary
        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.remove(tmp_out_path)
