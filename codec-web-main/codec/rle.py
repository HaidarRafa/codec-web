"""
rle.py - Algoritma Run-Length Encoding (RLE)

RLE adalah algoritma kompresi sederhana yang menggantikan
data berulang dengan pasangan (count, value).
Contoh: AAAABBBCC -> (4,A),(3,B),(2,C)

Kelebihan: Sederhana dan cepat
Kekurangan: Efektif hanya jika ada banyak data berulang
"""


def rle_encode(data):
    """
    Encode data menggunakan algoritma RLE.

    Parameters:
        data (bytes): Data input mentah

    Returns:
        bytes: Data terkompresi dengan format [count, value, count, value, ...]
               Setiap count dan value adalah 1 byte (0-255).
    """
    if not data:
        return b''

    result = bytearray()
    count = 1          # Hitung kemunculan berurutan
    prev = data[0]     # Byte sebelumnya untuk perbandingan

    for b in data[1:]:
        if b == prev and count < 255:
            # Byte sama dan belum overflow (max 255)
            count += 1
        else:
            # Byte berbeda, simpan pasangan (count, value)
            result.append(count)
            result.append(prev)
            prev = b
            count = 1

    # Simpan pasangan terakhir
    result.append(count)
    result.append(prev)

    return bytes(result)


def rle_decode(data):
    """
    Decode data yang telah di-RLE ke bentuk asli.

    Parameters:
        data (bytes): Data terkompresi RLE

    Returns:
        bytes: Data asli yang sudah didekompresi
    """
    if not data:
        return b''

    result = bytearray()

    # Iterasi setiap pasangan (count, value)
    for i in range(0, len(data), 2):
        count = data[i]       # Jumlah pengulangan
        value = data[i + 1]   # Byte yang diulang
        result.extend([value] * count)

    return bytes(result)
