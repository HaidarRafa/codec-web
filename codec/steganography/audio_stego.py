"""
audio_stego.py - Steganografi LSB untuk Audio

LSB pada audio menyembunyikan pesan rahasia pada bit terakhir
dari setiap sample audio. Karena sample audio memiliki rentang
nilai yang besar (misal int16: -32768..32767), perubahan bit
terakhir tidak akan terdengar oleh telinga manusia.

Format penyisipan (sama dengan image_stego):
  - 4 byte pertama: panjang pesan (32-bit little-endian)
  - Byte berikutnya: isi pesan (UTF-8)
"""

import wave
import io


def encode(audio_bytes, secret_text):
    """
    Sembunyikan pesan rahasia dalam file audio WAV menggunakan LSB.

    Parameters:
        audio_bytes (bytes): Data audio WAV cover
        secret_text (str): Pesan rahasia

    Returns:
        bytes: Data audio WAV stego (berisi pesan tersembunyi)
    """
    # Baca file WAV
    with wave.open(io.BytesIO(audio_bytes), 'rb') as wav:
        nchannels = wav.getnchannels()
        sampwidth = wav.getsampwidth()  # Bytes per sample
        framerate = wav.getframerate()
        nframes = wav.getnframes()
        frames = bytearray(wav.readframes(nframes))

    # Siapkan payload: header + isi pesan
    text_bytes = secret_text.encode('utf-8')
    header = len(text_bytes).to_bytes(4, 'little')
    payload = bytearray(header + text_bytes)

    # Konversi payload ke bit
    payload_bits = []
    for b in payload:
        payload_bits.extend([(b >> i) & 1 for i in range(8)])

    # Kapasitas = jumlah sample
    sample_size = sampwidth
    total_samples = len(frames) // sample_size
    max_bits = total_samples

    if len(payload_bits) > max_bits:
        raise ValueError(
            f'Message too long for this audio (max {max_bits // 8} bytes)'
        )

    # Sisipkan bit ke LSB byte pertama setiap sample
    for i in range(len(payload_bits)):
        byte_idx = i * sample_size
        frames[byte_idx] = (frames[byte_idx] & 0xFE) | payload_bits[i]

    # Simpan sebagai WAV baru
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_out:
        wav_out.setnchannels(nchannels)
        wav_out.setsampwidth(sampwidth)
        wav_out.setframerate(framerate)
        wav_out.writeframes(bytes(frames))
    return buf.getvalue()


def decode(audio_bytes):
    """
    Ekstrak pesan rahasia dari file audio WAV stego.

    Parameters:
        audio_bytes (bytes): Data audio WAV stego

    Returns:
        str: Pesan rahasia yang ditemukan
    """
    # Baca file WAV
    with wave.open(io.BytesIO(audio_bytes), 'rb') as wav:
        sampwidth = wav.getsampwidth()
        nframes = wav.getnframes()
        frames = wav.readframes(nframes)

    # Hitung jumlah sample
    sample_size = sampwidth
    total_bytes = len(frames)
    total_samples = total_bytes // sample_size

    # Baca LSB dari setiap sample
    bits = []
    for i in range(total_samples):
        byte_idx = i * sample_size
        bits.append(frames[byte_idx] & 1)

    if len(bits) < 32:
        raise ValueError('Audio too short to contain a message')

    # Baca 32 bit pertama = panjang pesan
    msg_len = 0
    for j in range(32):
        msg_len |= bits[j] << (j % 8)

    if msg_len <= 0 or msg_len > (total_samples // 8) - 4:
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

    return chars.decode('utf-8', errors='replace')
