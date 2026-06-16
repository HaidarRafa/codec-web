/**
 * audio.js - Logic untuk halaman Audio Codec
 * Mengatur interaksi Compress, Decompress, Stego Encode/Decode untuk audio
 */

document.addEventListener('DOMContentLoaded', function () {

    // =============================================
    // SETUP FILE INPUTS
    // =============================================
    setupFileInput('file-compress', 'btn-compress');
    setupFileInput('file-decompress', 'btn-decompress');
    setupStegoInput('file-stego-encode', 'msg-encode', 'btn-stego-encode');
    setupFileInput('file-stego-decode', 'btn-stego-decode');

    // =============================================
    // METHOD SELECTOR - Tampilkan/sembunyikan parameter
    // =============================================
    const methodSelect = document.getElementById('audio-method');
    const bitrateGroup = document.getElementById('param-bitrate-group');

    if (methodSelect && bitrateGroup) {
        methodSelect.addEventListener('change', function () {
            // Tampilkan parameter bitrate hanya untuk metode Standard (MP3)
            bitrateGroup.style.display = this.value === 'std' ? 'block' : 'none';
        });
    }

    // =============================================
    // BUTTON: COMPRESS
    // =============================================
    document.getElementById('btn-compress').addEventListener('click', function () {
        const file = document.getElementById('file-compress').files[0];
        if (!file) return;

        const method = document.getElementById('audio-method').value;
        let url;
        let params = { method: method };

        if (method === 'std') {
            // Standard MP3 compression: tambah parameter bitrate
            url = '/api/audio/compress_std';
            params.bitrate = document.getElementById('param-bitrate').value;
        } else {
            // Custom RLE + Huffman compression
            url = '/api/audio/compress';
        }

        callApi(url, file, 'spinner-compress', 'result-compress', 'Audio berhasil dikompresi!', null, params);
    });

    // =============================================
    // BUTTON: DECOMPRESS
    // =============================================
    document.getElementById('btn-decompress').addEventListener('click', function () {
        const file = document.getElementById('file-decompress').files[0];
        if (!file) return;

        // Deteksi metode dari ekstensi file
        const isCustom = file.name.toLowerCase().endsWith('.cmp');
        const url = isCustom ? '/api/audio/decompress' : '/api/audio/decompress_std';

        callApi(url, file, 'spinner-decompress', 'result-decompress', 'Audio berhasil didekompresi!');
    });

    // =============================================
    // BUTTON: STEGO ENCODE
    // =============================================
    document.getElementById('btn-stego-encode').addEventListener('click', function () {
        const file = document.getElementById('file-stego-encode').files[0];
        const msg = document.getElementById('msg-encode').value.trim();
        if (!file || !msg) return;

        callApi('/api/audio/stego/encode', file, 'spinner-stego-encode', 'result-stego-encode',
            'Pesan berhasil disembunyikan!', msg);
    });

    // =============================================
    // BUTTON: STEGO DECODE
    // =============================================
    document.getElementById('btn-stego-decode').addEventListener('click', function () {
        const file = document.getElementById('file-stego-decode').files[0];
        if (!file) return;

        callApi('/api/audio/stego/decode', file, 'spinner-stego-decode', 'result-stego-decode',
            'Pesan rahasia ditemukan!');
    });
});
