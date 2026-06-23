/**
 * dashboard.js - Logic untuk halaman Dashboard
 * Mengambil data dari API dan menampilkan Chart.js + tabel riwayat
 */

// =============================================
// 1. LOAD DATA DASHBOARD SAAT HALAMAN DIBUKA
// =============================================

document.addEventListener('DOMContentLoaded', function () {
    loadDashboardData();
    document.getElementById('btn-clear-history').addEventListener('click', clearHistory);
});

/**
 * Fetch data dashboard dari backend API
 */
function loadDashboardData() {
    fetch('/api/dashboard/stats')
        .then(r => r.json())
        .then(data => {
            if (data.error) return;

            // Update stat cards
            document.getElementById('stat-total').textContent = data.total_files;
            document.getElementById('stat-avg-ratio').textContent = data.avg_ratio + '%';
            document.getElementById('stat-original').textContent = formatBytesDashboard(data.total_original);
            document.getElementById('stat-compressed').textContent = formatBytesDashboard(data.total_compressed);

            // Render charts
            renderSizeChart(data.size_data);
            renderMediaChart(data.media_data);

            // Render history table
            renderHistoryTable(data.history);
        })
        .catch(err => console.error('Dashboard error:', err));
}

/**
 * Format bytes untuk tampilan dashboard (lebih lengkap)
 */
function formatBytesDashboard(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
    return (bytes / 1073741824).toFixed(2) + ' GB';
}

// =============================================
// 2. CHART.JS - SIZE COMPARISON BAR CHART
// =============================================

let sizeChartInstance = null;

/**
 * Render bar chart perbandingan ukuran original vs compressed
 * Data dikelompokkan per media type (Image, Audio, Video)
 */
function renderSizeChart(sizeData) {
    const ctx = document.getElementById('sizeChart').getContext('2d');

    // Hancurkan chart lama jika ada
    if (sizeChartInstance) sizeChartInstance.destroy();

    // Siapkan labels dan datasets dari data API
    const labels = sizeData.map(item => item.media);
    const originalData = sizeData.map(item => item.original);
    const compressedData = sizeData.map(item => item.compressed);

    sizeChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Original Size',
                data: originalData,
                backgroundColor: 'rgba(251, 191, 36, 0.7)',
                borderColor: 'rgba(251, 191, 36, 1)',
                borderWidth: 1
            }, {
                label: 'Compressed Size',
                data: compressedData,
                backgroundColor: 'rgba(56, 189, 248, 0.7)',
                borderColor: 'rgba(56, 189, 248, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#9ca3af' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#9ca3af',
                        callback: function (value) {
                            return formatBytesDashboard(value);
                        }
                    },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    ticks: { color: '#9ca3af' },
                    grid: { display: false }
                }
            }
        }
    });
}

// =============================================
// 3. CHART.JS - MEDIA DISTRIBUTION PIE CHART
// =============================================

let mediaChartInstance = null;

/**
 * Render pie chart distribusi jumlah file per media type
 */
function renderMediaChart(mediaData) {
    const ctx = document.getElementById('mediaChart').getContext('2d');

    if (mediaChartInstance) mediaChartInstance.destroy();

    // Siapkan labels dan data dari API
    const labels = mediaData.map(item => item.media);
    const counts = mediaData.map(item => item.count);
    const colors = [
        'rgba(56, 189, 248, 0.8)'
    ];

    mediaChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: colors,
                borderColor: '#1a1d23',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#9ca3af', padding: 16 }
                }
            }
        }
    });
}

// =============================================
// 4. HISTORY TABLE
// =============================================

/**
 * Render tabel riwayat kompresi
 * @param {Array} history - Array objek riwayat dari API
 */
function renderHistoryTable(history) {
    const tbody = document.getElementById('history-body');
    if (!tbody) return;

    if (!history || history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">' +
            'Belum ada riwayat kompresi</td></tr>';
        return;
    }

    let html = '';
    // Tampilkan riwayat terbaru di atas (descending)
    history.slice().reverse().forEach(function (item) {
        const time = new Date(item.timestamp).toLocaleString('id-ID');
        html += '<tr>' +
            '<td><span class="badge bg-' + getMediaBadge(item.media) + '">' +
            escapeHtml(item.media) + '</span></td>' +
            '<td>' + escapeHtml(item.method) + '</td>' +
            '<td>' + formatBytesDashboard(item.original_size) + '</td>' +
            '<td>' + formatBytesDashboard(item.compressed_size) + '</td>' +
            '<td>' + item.ratio + '%</td>' +
            '<td><small class="text-muted">' + time + '</small></td>' +
            '</tr>';
    });
    tbody.innerHTML = html;
}

/**
 * Dapatkan warna badge Bootstrap berdasarkan tipe media
 */
function getMediaBadge(media) {
    const map = {
        'image': 'info'
    };
    return map[media] || 'secondary';
}

// =============================================
// 5. CLEAR HISTORY
// =============================================

/**
 * Hapus semua riwayat kompresi via API
 */
function clearHistory() {
    if (!confirm('Hapus semua riwayat kompresi?')) return;

    fetch('/api/history/clear', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                loadDashboardData();
            }
        })
        .catch(err => console.error('Clear history error:', err));
}
