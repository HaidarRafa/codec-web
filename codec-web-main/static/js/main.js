let uploadedFiles = [];
let isUploading = false;

function setupDragDrop(dropZoneId, inputId) {
    const dropZone = document.getElementById(dropZoneId);
    const input = document.getElementById(inputId);

    if (!dropZone || !input) return;

    dropZone.addEventListener('click', function (e) {
        if (e.target.closest('.trash-btn')) return;
        input.click();
    });

    dropZone.addEventListener('dragenter', function (e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('dragover');
    });

    dropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', function (e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    });

    input.addEventListener('change', function () {
        if (this.files.length > 0) {
            handleFiles(this.files);
        }
    });
}

function handleFiles(files) {
    for (const file of files) {
        const ext = file.name.split('.').pop().toLowerCase();
        const allowed = ['jpg', 'jpeg', 'png', 'bmp'];
        if (!allowed.includes(ext)) {
            showToast('error', 'Format ' + ext + ' tidak didukung');
            continue;
        }
        addFile(file);
    }
}

function addFile(file) {
    const existing = uploadedFiles.findIndex(f => f.name === file.name && f.size === file.size);
    if (existing !== -1) return;

    uploadedFiles.push(file);
    renderFiles();
    simulateUpload();
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    renderFiles();
    updateProcessButton();
}

function renderFiles() {
    const container = document.getElementById('uploaded-files');
    if (!container) return;

    const section = document.getElementById('uploaded-section');
    if (uploadedFiles.length === 0) {
        if (section) section.style.display = 'none';
        return;
    }

    if (section) section.style.display = 'block';

    let html = '';
    uploadedFiles.forEach(function (file, idx) {
        html += '<div class="file-item">' +
            '<div class="file-item-left">' +
            '<i class="bi bi-file-earmark-check file-item-icon"></i>' +
            '<span class="file-item-name" title="' + escapeHtml(file.name) + '">' + escapeHtml(file.name) + '</span>' +
            '</div>' +
            '<button class="trash-btn" data-index="' + idx + '">' +
            '<i class="bi bi-trash"></i>' +
            '</button>' +
            '</div>';
    });
    container.innerHTML = html;

    container.querySelectorAll('.trash-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const idx = parseInt(this.dataset.index, 10);
            removeFile(idx);
        });
    });

    updateProcessButton();
}

function updateProcessButton() {
    const btn = document.getElementById('btn-process');
    if (!btn) return;
    btn.disabled = uploadedFiles.length === 0;
}

function simulateUpload() {
    const section = document.getElementById('progress-section');
    const progressBar = document.getElementById('progress-bar');
    const progressLabel = document.getElementById('progress-label');
    if (!section || !progressBar) return;

    isUploading = true;
    section.style.display = 'block';
    progressLabel.textContent = 'Uploading - ' + uploadedFiles.length + '/' + uploadedFiles.length + ' file';
    progressBar.style.width = '0%';

    let width = 0;
    const interval = setInterval(function () {
        width += 5;
        progressBar.style.width = Math.min(width, 100) + '%';
        if (width >= 100) {
            clearInterval(interval);
            isUploading = false;
        }
    }, 40);
}

function showToast(type, message) {
    const container = document.getElementById('result-display');
    if (!container) return;
    const cls = type === 'success' ? 'success' : 'error';
    container.innerHTML = '<div class="result-box ' + cls + '">' + escapeHtml(message) + '</div>';
    container.style.display = 'block';
    setTimeout(function () {
        container.style.display = 'none';
    }, 3000);
}

function showResult(resultId, type, htmlContent) {
    const el = document.getElementById(resultId);
    if (!el) return;
    el.innerHTML = '<div class="result-box ' + type + '">' + htmlContent + '</div>';
    el.style.display = 'block';
}

function showSpinner(spinnerId) {
    const el = document.getElementById(spinnerId);
    if (el) el.classList.remove('d-none');
}

function hideSpinner(spinnerId) {
    const el = document.getElementById(spinnerId);
    if (el) el.classList.add('d-none');
}

function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
