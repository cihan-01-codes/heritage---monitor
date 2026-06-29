async function fetchStats() {
    const res = await fetch('/api/dashboard-stats/');
    return await res.json();
}

let charts = {};

function updateLastUpdated() {
    const el = document.getElementById('last-updated');
    if (el) {
        const now = new Date();
        el.textContent = now.toLocaleTimeString();
    }
}

function makeChart(id, label, data, labels, color) {
    if (charts[id]) {
        charts[id].data.labels = labels;
        charts[id].data.datasets[0].data = data;
        charts[id].update();
        return;
    }
    charts[id] = new Chart(document.getElementById(id), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                backgroundColor: color + '22',
                tension: 0.4,
                fill: true,
                pointRadius: 3,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: true } },
            scales: { y: { beginAtZero: false } }
        }
    });
}

async function loadAdminDashboard() {
    const data = await fetchStats();
    document.getElementById('total-buildings').textContent = data.total_buildings;
    document.getElementById('total-users').textContent = data.total_users;
    document.getElementById('total-alerts').textContent = data.total_alerts;
    document.getElementById('total-readings').textContent = data.total_readings;
    makeChart('tempChart', 'Temperature °C', data.temperatures, data.labels, '#f59e0b');
    makeChart('humidChart', 'Humidity %', data.humidities, data.labels, '#3b82f6');
    makeChart('vibChart', 'Vibration', data.vibrations, data.labels, '#ef4444');
    updateLastUpdated();
    setTimeout(loadAdminDashboard, 30000);
}

async function loadAntiquitiesDashboard() {
    const data = await fetchStats();
    document.getElementById('total-buildings').textContent = data.total_buildings;
    document.getElementById('total-alerts').textContent = data.total_alerts;
    document.getElementById('total-readings').textContent = data.total_readings;
    const list = document.getElementById('alerts-list');
    list.innerHTML = data.recent_alerts.length
        ? data.recent_alerts.map(a =>
            `<div class="alert-item ${a.severity === 'Critical' ? 'alert-critical' : 'alert-warning'}">
                <strong>${a.severity}</strong>: ${a.message}
            </div>`).join('')
        : '<p class="empty-state">No active alerts</p>';
    makeChart('tempChart', 'Temperature °C', data.temperatures, data.labels, '#f59e0b');
    makeChart('humidChart', 'Humidity %', data.humidities, data.labels, '#3b82f6');
    makeChart('vibChart', 'Vibration', data.vibrations, data.labels, '#ef4444');
    updateLastUpdated();
    setTimeout(loadAntiquitiesDashboard, 30000);
}

async function loadPartnerDashboard() {
    const data = await fetchStats();
    if (charts['envChart']) {
        charts['envChart'].data.labels = data.labels;
        charts['envChart'].data.datasets[0].data = data.temperatures;
        charts['envChart'].data.datasets[1].data = data.humidities;
        charts['envChart'].data.datasets[2].data = data.vibrations;
        charts['envChart'].update();
    } else {
        charts['envChart'] = new Chart(document.getElementById('envChart'), {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    { label: 'Temperature °C', data: data.temperatures, borderColor: '#f59e0b', tension: 0.4, fill: false },
                    { label: 'Humidity %', data: data.humidities, borderColor: '#3b82f6', tension: 0.4, fill: false },
                    { label: 'Vibration', data: data.vibrations, borderColor: '#ef4444', tension: 0.4, fill: false }
                ]
            },
            options: { responsive: true }
        });
    }
    updateLastUpdated();
    setTimeout(loadPartnerDashboard, 30000);
}

async function loadOwnerDashboard() {
    const data = await fetchStats();
    document.getElementById('buildings-list').innerHTML = data.my_buildings.length
        ? data.my_buildings.map(b =>
            `<div class="building-item">🏛️ ${b.name} — ${b.location_gps}</div>`).join('')
        : '<p class="empty-state">No buildings assigned</p>';
    makeChart('tempChart', 'Temperature °C', data.temperatures, data.labels, '#f59e0b');
    makeChart('humidChart', 'Humidity %', data.humidities, data.labels, '#3b82f6');
    makeChart('ownerVibChart', 'Vibration', data.vibrations, data.labels, '#ef4444');
    updateLastUpdated();
    setTimeout(loadOwnerDashboard, 30000);
}