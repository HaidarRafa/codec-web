/**
 * video.js - Logic untuk halaman Video Codec
 * Mengatur interaksi Compress, Decompress, Stego Encode/Decode untuk video
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
    // CRF SLIDER - Update nilai saat digeser
    // =============================================
    const crfSlider = document.getElementById('param-crf');
    if (crfSlider) {
        crfSlider.addEventListener('input', function () {
            document.getElementById('crf-value').textContent = this.value;
        });
    }

    // =============================================
    // METHOD SELECTOR - Tampilkan/sembunyikan parameter
    // =============================================
    const methodSelect = document.getElementById('video-method');
    const crfGroup = document.getElementById('param-crf-group');

    if (methodSelect && crfGroup) {
        methodSelect.addEventListener('change', function () {
            // Tampilkan parameter CRF hanya untuk metode Standard (H.264)
            crfGroup.style.display = this.value === 'std' ? 'block' : 'none';
        });
    }

    // =============================================
    // BUTTON: COMPRESS
    // =============================================
    document.getElementById('btn-compress').addEventListener('click', function () {
        const file = document.getElementById('file-compress').files[0];
        if (!file) return;

        const method = document.getElementById('video-method').value;
        let url;
        let params = { method: method };

        if (method === 'std') {
            // Standard H.264 compression: tambah parameter CRF
            url = '/api/video/compress_std';
            params.crf = document.getElementById('param-crf').value;
        } else {
            // Custom Frame Diff + RLE + Huffman compression
            url = '/api/video/compress';
        }

        callApi(url, file, 'spinner-compress', 'result-compress', 'Video berhasil dikompresi!', null, params);
    });

    // =============================================
    // BUTTON: DECOMPRESS
    // =============================================
    document.getElementById('btn-decompress').addEventListener('click', function () {
        const file = document.getElementById('file-decompress').files[0];
        if (!file) return;

        // Deteksi metode dari ekstensi file
        const isCustom = file.name.toLowerCase().endsWith('.cmp');
        const url = isCustom ? '/api/video/decompress' : '/api/video/decompress_std';

        callApi(url, file, 'spinner-decompress', 'result-decompress', 'Video berhasil didekompresi!');
    });

    // =============================================
    // BUTTON: STEGO ENCODE
    // =============================================
    document.getElementById('btn-stego-encode').addEventListener('click', function () {
        const file = document.getElementById('file-stego-encode').files[0];
        const msg = document.getElementById('msg-encode').value.trim();
        if (!file || !msg) return;

        callApi('/api/video/stego/encode', file, 'spinner-stego-encode', 'result-stego-encode',
            'Pesan berhasil disembunyikan!', msg);
    });

    // =============================================
    // BUTTON: STEGO DECODE
    // =============================================
    document.getElementById('btn-stego-decode').addEventListener('click', function () {
        const file = document.getElementById('file-stego-decode').files[0];
        if (!file) return;

        callApi('/api/video/stego/decode', file, 'spinner-stego-decode', 'result-stego-decode',
            'Pesan rahasia ditemukan!');
    });
});
