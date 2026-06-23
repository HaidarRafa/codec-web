/**
 * image.js - Logic untuk halaman Image Codec
 * Mengatur interaksi Compress, Decompress, Stego Encode/Decode untuk gambar
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
    // QUALITY SLIDER - Update nilai saat digeser
    // =============================================
    const qualitySlider = document.getElementById('param-quality');
    if (qualitySlider) {
        qualitySlider.addEventListener('input', function () {
            document.getElementById('quality-value').textContent = this.value;
        });
    }

    // =============================================
    // METHOD SELECTOR - Tampilkan/sembunyikan parameter
    // =============================================
    const methodSelect = document.getElementById('image-method');
    const qualityGroup = document.getElementById('param-quality-group');

    if (methodSelect && qualityGroup) {
        methodSelect.addEventListener('change', function () {
            // Tampilkan slider quality hanya untuk metode Standard (JPEG)
            qualityGroup.style.display = this.value === 'std' ? 'block' : 'none';
        });
    }

    // =============================================
    // BUTTON: COMPRESS
    // =============================================
    document.getElementById('btn-compress').addEventListener('click', function () {
        const file = document.getElementById('file-compress').files[0];
        if (!file) return;

        const method = document.getElementById('image-method').value;

        // Tentukan URL API berdasarkan metode yang dipilih
        let url;
        let params = { method: method };

        if (method === 'std') {
            // Standard JPEG compression: tambah parameter quality
            url = '/api/image/compress_std';
            params.quality = document.getElementById('param-quality').value;
        } else {
            // Custom RLE + Huffman compression
            url = '/api/image/compress';
        }

        callApi(url, file, 'spinner-compress', 'result-compress', 'Gambar berhasil dikompresi!', null, params);
    });

    // =============================================
    // BUTTON: DECOMPRESS
    // =============================================
    document.getElementById('btn-decompress').addEventListener('click', function () {
        const file = document.getElementById('file-decompress').files[0];
        if (!file) return;

        // Deteksi metode dari ekstensi file
        // .cmp = custom, .jpg/.jpeg = standard
        const isCustom = file.name.toLowerCase().endsWith('.cmp');
        const url = isCustom ? '/api/image/decompress' : '/api/image/decompress_std';

        callApi(url, file, 'spinner-decompress', 'result-decompress', 'Gambar berhasil didekompresi!');
    });

    // =============================================
    // BUTTON: STEGO ENCODE
    // =============================================
    document.getElementById('btn-stego-encode').addEventListener('click', function () {
        const file = document.getElementById('file-stego-encode').files[0];
        const msg = document.getElementById('msg-encode').value.trim();
        if (!file || !msg) return;

        callApi('/api/image/stego/encode', file, 'spinner-stego-encode', 'result-stego-encode',
            'Pesan berhasil disembunyikan!', msg);
    });

    // =============================================
    // BUTTON: STEGO DECODE
    // =============================================
    document.getElementById('btn-stego-decode').addEventListener('click', function () {
        const file = document.getElementById('file-stego-decode').files[0];
        if (!file) return;

        callApi('/api/image/stego/decode', file, 'spinner-stego-decode', 'result-stego-decode',
            'Pesan rahasia ditemukan!');
    });
});
