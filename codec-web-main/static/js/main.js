/**
 * main.js - Fungsi shared untuk seluruh halaman
 * Berisi utility untuk sidebar, upload file, spinner, result display
 */

// =============================================
// 1. SIDEBAR TOGGLE (untuk mobile)
// =============================================

/**
 * Toggle sidebar untuk tampilan mobile
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('show');
}

// Event listener untuk tombol toggle sidebar
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', toggleSidebar);
    }

    // Tutup sidebar jika klik di luar (mobile)
    document.addEventListener('click', function (e) {
        const sidebar = document.getElementById('sidebar');
        const toggle = document.getElementById('menu-toggle');
        if (window.innerWidth < 768 &&
            sidebar && sidebar.classList.contains('show') &&
            !sidebar.contains(e.target) &&
            toggle && !toggle.contains(e.target)) {
            sidebar.classList.remove('show');
        }
    });
});

// =============================================
// 2. FILE UPLOAD HELPER
// =============================================

/**
 * Setup input file: disable/enable button berdasarkan file
 * @param {string} inputId - ID elemen input file
 * @param {string} btnId - ID tombol yang akan di-enable/disable
 */
function setupFileInput(inputId, btnId) {
    const input = document.getElementById(inputId);
    const btn = document.getElementById(btnId);
    if (!input || !btn) return;

    input.addEventListener('change', function () {
        btn.disabled = !this.files.length;
    });
}

/**
 * Setup input file + textarea untuk stego encode
 * Button enable hanya jika ada file DAN pesan
 */
function setupStegoInput(inputId, msgId, btnId) {
    const input = document.getElementById(inputId);
    const msg = document.getElementById(msgId);
    const btn = document.getElementById(btnId);
    if (!input || !msg || !btn) return;

    function checkEnable() {
        btn.disabled = !(input.files.length && msg.value.trim());
    }

    input.addEventListener('change', checkEnable);
    msg.addEventListener('input', checkEnable);
}

// =============================================
// 3. SPINNER CONTROL
// =============================================

/**
 * Tampilkan spinner loading
 */
function showSpinner(spinnerId) {
    const el = document.getElementById(spinnerId);
    if (el) el.classList.remove('d-none');
}

/**
 * Sembunyikan spinner loading
 */
function hideSpinner(spinnerId) {
    const el = document.getElementById(spinnerId);
    if (el) el.classList.add('d-none');
}

// =============================================
// 4. RESULT DISPLAY
// =============================================

/**
 * Tampilkan hasil (success atau error) ke dalam elemen result
 * @param {string} resultId - ID elemen result container
 * @param {string} type - 'success' atau 'error'
 * @param {string} htmlContent - Konten HTML yang akan ditampilkan
 */
function showResult(resultId, type, htmlContent) {
    const el = document.getElementById(resultId);
    if (!el) return;
    el.innerHTML = '<div class="result-box ' + type + '">' + htmlContent + '</div>';
    el.style.display = 'block';
}

/**
 * Format bytes ke human-readable string (B, KB, MB)
 */
function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

/**
 * Escape HTML untuk mencegah XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// =============================================
// 5. API CALL HELPER
// =============================================

/**
 * Upload file ke API dan tampilkan hasilnya
 * Fungsi generic yang dipakai oleh semua halaman (image)
 *
 * @param {string} url - API endpoint URL
 * @param {File} file - File object dari input
 * @param {string} spinnerId - ID spinner element
 * @param {string} resultId - ID result container
 * @param {string} successLabel - Label sukses
 * @param {string|null} extraMsg - Pesan tambahan (untuk stego encode)
 * @param {object|null} extraParams - Parameter tambahan (method, quality, dll)
 */
function callApi(url, file, spinnerId, resultId, successLabel, extraMsg, extraParams) {
    const formData = new FormData();
    formData.append('file', file);
    if (extraMsg) formData.append('message', extraMsg);
    if (extraParams) {
        for (const key in extraParams) {
            formData.append(key, extraParams[key]);
        }
    }

    showSpinner(spinnerId);
    document.getElementById(resultId).style.display = 'none';

    fetch(url, { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
            hideSpinner(spinnerId);
            if (data.error) {
                showResult(resultId, 'error', '<strong>Error:</strong> ' + escapeHtml(data.error));
            } else {
                let html = '<strong>' + successLabel + '</strong>';

                // Tampilkan statistik kompresi jika ada
                if (data.ratio !== undefined) {
                    html += '<div class="result-stat"><span>Original:</span><span>' +
                        formatBytes(data.original_size) + '</span></div>';
                    html += '<div class="result-stat"><span>Compressed:</span><span>' +
                        formatBytes(data.compressed_size) + '</span></div>';
                    html += '<div class="result-stat"><span>Ratio:</span><span>' +
                        data.ratio + '%</span></div>';
                }

                // Tampilkan pesan hasil decode jika ada
                if (data.message !== undefined) {
                    html += '<div class="message-box">' + escapeHtml(data.message) + '</div>';
                }

                // Tombol download jika ada file
                if (data.file) {
                    html += '<a class="btn btn-success btn-sm download-btn" ' +
                        'href="/static/uploads/' + data.file + '" download>' +
                        '<i class="bi bi-download me-1"></i>Download File</a>';
                }

                showResult(resultId, 'success', html);
            }
        })
        .catch(err => {
            hideSpinner(spinnerId);
            showResult(resultId, 'error', '<strong>Error:</strong> ' + escapeHtml(err.message));
        });
}
