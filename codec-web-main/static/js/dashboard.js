document.addEventListener('DOMContentLoaded', function () {
    setupDragDrop('drop-zone', 'file-input');

    const btn = document.getElementById('btn-process');
    if (btn) {
        btn.addEventListener('click', processFiles);
    }

    const qualityGroup = document.getElementById('param-quality-group');
    const stegoGroup = document.getElementById('param-stego-message');

    const methodBtns = document.querySelectorAll('.method-btn');
    const subToggle = document.getElementById('sub-toggle');
    const subBtns = document.querySelectorAll('.sub-btn');

    methodBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            methodBtns.forEach(function (b) { b.classList.remove('active'); });
            this.classList.add('active');
            updateUI();
        });
    });

    subBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            subBtns.forEach(function (b) { b.classList.remove('active'); });
            this.classList.add('active');
            updateUI();
        });
    });

    function updateUI() {
        var methodEl = document.querySelector('.method-btn.active');
        var subEl = document.querySelector('.sub-btn.active');
        if (!methodEl) return;
        var m = methodEl.dataset.method;
        var s = subEl ? subEl.dataset.sub : null;

        if (subToggle) subToggle.classList.toggle('show', m === 'compress' || m === 'decompress');
        if (qualityGroup) qualityGroup.style.display = (m === 'compress' && s === 'std') ? 'block' : 'none';
        if (stegoGroup) stegoGroup.style.display = m === 'stego_encode' ? 'block' : 'none';
    }

    const qualitySlider = document.getElementById('param-quality');
    const qualityValue = document.getElementById('quality-value');
    if (qualitySlider && qualityValue) {
        qualitySlider.addEventListener('input', function () {
            qualityValue.textContent = this.value;
        });
    }
});

function processFiles() {
    if (uploadedFiles.length === 0 || isUploading) return;

    const file = uploadedFiles[0];
    var activeMethod = document.querySelector('.method-btn.active');
    var activeSub = document.querySelector('.sub-btn.active');
    if (!activeMethod) return;
    var method = activeMethod.dataset.method;
    var sub = activeSub ? activeSub.dataset.sub : null;

    let url;
    let params = {};

    if (method === 'compress') {
        if (sub === 'std') {
            url = '/api/image/compress_std';
            params.quality = document.getElementById('param-quality').value || 85;
        } else {
            url = '/api/image/compress';
        }
    } else if (method === 'decompress') {
        url = sub === 'std' ? '/api/image/decompress_std' : '/api/image/decompress';
    } else if (method === 'stego_encode') {
        url = '/api/image/stego/encode';
        params.message = document.getElementById('stego-message').value.trim();
        if (!params.message) {
            showToast('error', 'Masukkan pesan rahasia untuk stego encode');
            return;
        }
    } else if (method === 'stego_decode') {
        url = '/api/image/stego/decode';
    }

    callApiDashboard(url, file, params);
}

function callApiDashboard(url, file, extraParams) {
    const formData = new FormData();
    formData.append('file', file);
    if (extraParams) {
        for (const key in extraParams) {
            formData.append(key, extraParams[key]);
        }
    }

    const spinner = document.getElementById('spinner-processing');
    const result = document.getElementById('result-display');

    showSpinner('spinner-processing');
    result.style.display = 'none';

    fetch(url, { method: 'POST', body: formData })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            hideSpinner('spinner-processing');
            if (data.error) {
                showResult('result-display', 'error', '<strong>Error:</strong> ' + escapeHtml(data.error));
            } else {
                let label = 'File berhasil diproses!';
                // Check method for appropriate label
                var methodEl = document.querySelector('.method-btn.active');
                var method = methodEl ? methodEl.dataset.method : '';
                if (method === 'compress') {
                    label = 'Gambar berhasil dikompresi!';
                } else if (method === 'decompress') {
                    label = 'Gambar berhasil didekompresi!';
                } else if (method === 'stego_encode') {
                    label = 'Pesan berhasil disembunyikan!';
                } else if (method === 'stego_decode') {
                    label = 'Pesan rahasia ditemukan!';
                }

                let html = '<strong>' + label + '</strong>';

                if (data.ratio !== undefined) {
                    html += '<div class="result-stat"><span>Original:</span><span>' +
                        formatBytes(data.original_size) + '</span></div>';
                    html += '<div class="result-stat"><span>Compressed:</span><span>' +
                        formatBytes(data.compressed_size) + '</span></div>';
                    html += '<div class="result-stat"><span>Ratio:</span><span>' +
                        data.ratio + '%</span></div>';
                }

                if (data.message !== undefined) {
                    html += '<div class="message-box">' + escapeHtml(data.message) + '</div>';
                }

                if (data.file) {
                    html += '<a class="btn btn-success btn-sm download-btn mt-2" ' +
                        'href="/static/uploads/' + data.file + '" download>' +
                        '<i class="bi bi-download me-1"></i>Download File</a>';
                }

                showResult('result-display', 'success', html);
            }
        })
        .catch(function (err) {
            hideSpinner('spinner-processing');
            showResult('result-display', 'error', '<strong>Error:</strong> ' + escapeHtml(err.message));
        });
}
