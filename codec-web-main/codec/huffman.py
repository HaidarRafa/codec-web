"""
huffman.py - Algoritma Huffman Coding

Huffman Coding adalah algoritma kompresi lossless yang menggunakan
frekuensi kemunculan data untuk membuat kode biner dengan panjang variabel.
Data yang sering muncul mendapat kode pendek, yang jarang muncul kode panjang.

Cara kerja:
1. Hitung frekuensi setiap byte
2. Bangun binary tree berdasarkan frekuensi
3. Assign kode biner (0/1) berdasarkan traversal tree
4. Simpan tree untuk keperluan dekompresi
"""

import heapq
from collections import Counter


class HuffmanNode:
    """
    Node untuk pohon Huffman.

    Attributes:
        symbol (int/None): Nilai byte (None untuk internal node)
        freq (int): Frekuensi kemunculan
        left (HuffmanNode): Anak kiri (bit '0')
        right (HuffmanNode): Anak kanan (bit '1')
    """

    def __init__(self, symbol, freq):
        self.symbol = symbol
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(freqs):
    """
    Bangun Huffman tree dari frekuensi data menggunakan priority queue.

    Parameters:
        freqs (dict): Mapping byte -> frekuensi

    Returns:
        HuffmanNode: Root dari Huffman tree
    """
    # Buat min-heap dari semua node
    heap = [HuffmanNode(sym, f) for sym, f in freqs.items()]
    heapq.heapify(heap)

    # Gabungkan dua node dengan frekuensi terkecil
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)

    return heap[0] if heap else None


def _build_codes(node, prefix, codebook):
    """
    Rekursif: assign kode biner ke setiap leaf node.

    Parameters:
        node (HuffmanNode): Node saat ini
        prefix (str): Kode biner prefix sejauh ini
        codebook (dict): Mapping byte -> kode biner
    """
    if node is None:
        return
    if node.symbol is not None:
        # Leaf node: simpan kode biner untuk symbol ini
        codebook[node.symbol] = prefix or '0'
        return
    _build_codes(node.left, prefix + '0', codebook)
    _build_codes(node.right, prefix + '1', codebook)


def build_codes(tree):
    """Bangun codebook dari Huffman tree."""
    codebook = {}
    _build_codes(tree, '', codebook)
    return codebook


def encode(data):
    """
    Encode data menggunakan Huffman coding.

    Returns:
        bit_str (str): String biner hasil encoding
        codebook (dict): Mapping byte -> kode biner
    """
    if not data:
        return b'', {}
    freqs = Counter(data)
    tree = build_tree(freqs)
    codebook = build_codes(tree)
    bit_str = ''.join(codebook[b] for b in data)
    return bit_str, codebook


def decode(bit_str, tree):
    """
    Decode string biner kembali ke data asli menggunakan Huffman tree.

    Parameters:
        bit_str (str): String biner
        tree (HuffmanNode): Huffman tree yang digunakan saat encode

    Returns:
        bytes: Data asli hasil dekompresi
    """
    if not bit_str or tree is None:
        return b''
    result = bytearray()
    node = tree
    for bit in bit_str:
        # Traverse tree: 0 = kiri, 1 = kanan
        node = node.left if bit == '0' else node.right
        if node.symbol is not None:
            # Sampai di leaf node, dapatkan symbol asli
            result.append(node.symbol)
            node = tree  # Kembali ke root untuk byte berikutnya
    return bytes(result)


def bits_to_bytes(bit_str):
    """
    Konversi string biner ke bytes dengan padding.

    Parameters:
        bit_str (str): String biner (contoh: '01010101...')

    Returns:
        data (bytes): Data byte
        padding (int): Jumlah bit padding yang ditambahkan
    """
    padding = (8 - len(bit_str) % 8) % 8
    bit_str_padded = bit_str + '0' * padding
    data = bytearray()
    for i in range(0, len(bit_str_padded), 8):
        byte = bit_str_padded[i:i+8]
        data.append(int(byte, 2))
    return bytes(data), padding


def bytes_to_bits(data, padding):
    """
    Konversi bytes kembali ke string biner, buang padding.

    Parameters:
        data (bytes): Data byte
        padding (int): Jumlah bit padding

    Returns:
        str: String biner
    """
    bit_str = ''.join(f'{b:08b}' for b in data)
    if padding:
        bit_str = bit_str[:-padding]
    return bit_str


def serialize_tree(node):
    """
    Serialisasi Huffman tree ke bytes untuk disimpan dalam file.

    Format: 0x00 untuk internal node, 0x01 + byte untuk leaf node.

    Parameters:
        node (HuffmanNode): Root node

    Returns:
        bytes: Representasi tree
    """
    if node is None:
        return b''
    if node.symbol is not None:
        # Leaf node: flag 0x01 + nilai byte
        return b'\x01' + bytes([node.symbol])
    # Internal node: flag 0x00 + left + right
    return b'\x00' + serialize_tree(node.left) + serialize_tree(node.right)


def deserialize_tree(data, offset=0):
    """
    Deserialisasi bytes kembali ke Huffman tree.

    Parameters:
        data (bytes): Data serialisasi tree
        offset (int): Posisi awal baca

    Returns:
        (HuffmanNode, int): Root node dan offset setelah baca
    """
    if offset >= len(data):
        return None, offset
    flag = data[offset]
    offset += 1
    if flag == 1:
        # Leaf node: baca nilai byte
        return HuffmanNode(data[offset], 0), offset + 1
    # Internal node: baca left lalu right
    left, offset = deserialize_tree(data, offset)
    right, offset = deserialize_tree(data, offset)
    node = HuffmanNode(None, 0)
    node.left = left
    node.right = right
    return node, offset


def huffman_compress(data):
    """
    Fungsi lengkap kompresi Huffman: encode + serialize tree.

    Returns:
        byte_data (bytes): Data terkompresi
        padding (int): Padding bits
        tree_data (bytes): Huffman tree terserialisasi
        codebook (dict): Mapping kode (opsional)
    """
    bit_str, codebook = encode(data)
    byte_data, padding = bits_to_bytes(bit_str)
    tree_data = serialize_tree(build_tree(Counter(data)))
    return byte_data, padding, tree_data, codebook


def huffman_decompress(byte_data, padding, tree_data):
    """
    Fungsi lengkap dekompresi Huffman: deserialize + decode.

    Returns:
        bytes: Data asli hasil dekompresi
    """
    tree, _ = deserialize_tree(tree_data)
    bit_str = bytes_to_bits(byte_data, padding)
    return decode(bit_str, tree)
