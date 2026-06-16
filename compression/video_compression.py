"""
video_compression.py - Kompresi Video dengan H.264 (FFmpeg)

Menggunakan FFmpeg via subprocess untuk melakukan encode
video ke codec H.264 dengan parameter CRF (Constant Rate Factor).
Metode kompresi lossy standar industri untuk video.
"""

import subprocess
import tempfile
import os


def compress(video_bytes, crf=23):
    """
    Kompres video menggunakan codec H.264 via FFmpeg.

    Parameters:
        video_bytes (bytes): Data video input (format apapun yang
                            didukung FFmpeg, misal AVI, MP4, MOV).
        crf (int): Constant Rate Factor (0-51). Semakin rendah,
                   semakin baik kualitas tapi ukuran besar.
                   Standard: 18-28 (23 = default x264).

    Returns:
        bytes: Data video terkompresi dalam format MP4 (H.264).
    """
    # Buat file temporary untuk input video
    with tempfile.NamedTemporaryFile(suffix='.input', delete=False) as tmp_in:
        tmp_in.write(video_bytes)
        tmp_in_path = tmp_in.name

    # File temporary untuk output video MP4
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_out:
        tmp_out_path = tmp_out.name

    try:
        # Jalankan FFmpeg untuk encode H.264
        cmd = [
            'ffmpeg', '-y',
            '-i', tmp_in_path,               # input file
            '-c:v', 'libx264',               # video codec: H.264
            '-crf', str(crf),                # quality (lower = better)
            '-preset', 'medium',             # encode speed vs compression
            '-c:a', 'aac',                   # audio codec: AAC
            '-b:a', '128k',                  # audio bitrate
            tmp_out_path
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f'FFmpeg error: {result.stderr}'
            )

        # Baca hasil video terkompresi
        with open(tmp_out_path, 'rb') as f:
            compressed = f.read()

        return compressed

    finally:
        # Bersihkan file temporary
        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.remove(tmp_out_path)


def decompress(video_bytes):
    """
    Dekompres video H.264/MP4 kembali ke format AVI.

    Parameters:
        video_bytes (bytes): Data video MP4 (H.264) input.

    Returns:
        bytes: Data video AVI (uncompressed/lossless).
    """
    # Buat file temporary untuk input MP4
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_in:
        tmp_in.write(video_bytes)
        tmp_in_path = tmp_in.name

    # File temporary untuk output AVI
    with tempfile.NamedTemporaryFile(suffix='.avi', delete=False) as tmp_out:
        tmp_out_path = tmp_out.name

    try:
        # Jalankan FFmpeg untuk decode ke AVI
        cmd = [
            'ffmpeg', '-y',
            '-i', tmp_in_path,
            '-c:v', 'mpeg4',                 # video codec output
            '-q:v', '1',                     # quality terbaik
            tmp_out_path
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f'FFmpeg error: {result.stderr}'
            )

        # Baca hasil AVI
        with open(tmp_out_path, 'rb') as f:
            decompressed = f.read()

        return decompressed

    finally:
        # Bersihkan file temporary
        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.remove(tmp_out_path)
