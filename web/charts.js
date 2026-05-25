/**
 * Garmin Coach – Chart.js (Dark Theme, Purple/Pink Accent)
 */

// Global Chart.js defaults for dark theme
Chart.defaults.color = '#9d9daa';
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.06)';
Chart.defaults.font.family = "'Outfit', sans-serif";
Chart.defaults.font.size = 11;

/**
 * Initialisiert alle Charts.
 */
function initCharts(data) {
    const gridColor = 'rgba(39, 39, 42, 0.8)';

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 20,
                    usePointStyle: true,
                    pointStyle: 'circle',
                    font: { size: 11, weight: '500' },
                    color: '#a1a1aa'
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: {
                    maxTicksLimit: 8,
                    font: { size: 10 },
                    color: '#71717a'
                }
            },
            y: {
                grid: { color: gridColor, lineWidth: 0.5 },
                ticks: { font: { size: 10 }, color: '#71717a' }
            }
        }
    };

    erstelleCtlChart(data.ctl, defaultOptions);
    erstelleKmChart(data.km, defaultOptions);
    erstelleAeChart(data.ae, defaultOptions);
    erstelleDriftChart(data.drift, defaultOptions);
    erstelleWeightChart(data.weight, defaultOptions);
    erstellePaceHfChart(data.paceHf, defaultOptions);
}

/**
 * CTL/ATL/TSB – Punkte nur an Trainingstagen sichtbar
 */
function erstelleCtlChart(daten, opts) {
    const ctx = document.getElementById('ctlChart');
    if (!ctx || !daten.labels.length) return;

    const trainingstage = daten.trainingstage || [];

    // Punkt-Radien: nur an Trainingstagen sichtbar
    const punkteCtl = trainingstage.map(t => t ? 5 : 0);
    const punkteAtl = trainingstage.map(t => t ? 4 : 0);
    const punkteTsb = trainingstage.map(t => t ? 4 : 0);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: formatiereLabels(daten.labels),
            datasets: [
                {
                    label: 'CTL (Fitness)',
                    data: daten.ctl,
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.05)',
                    borderWidth: 2.5,
                    fill: false,
                    tension: 0.4,
                    pointRadius: punkteCtl,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#a855f7',
                    pointBorderColor: '#18181b',
                    pointBorderWidth: 2
                },
                {
                    label: 'ATL (Ermüdung)',
                    data: daten.atl,
                    borderColor: '#f43f5e',
                    backgroundColor: 'rgba(244, 63, 94, 0.05)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: punkteAtl,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#f43f5e',
                    pointBorderColor: '#18181b',
                    pointBorderWidth: 2
                },
                {
                    label: 'TSB (Form)',
                    data: daten.tsb,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.04)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: punkteTsb,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#18181b',
                    pointBorderWidth: 2
                }
            ]
        },
        options: {
            ...opts,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                ...opts.plugins,
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#18181b',
                    borderColor: '#27272a',
                    borderWidth: 1,
                    titleColor: '#fafafa',
                    bodyColor: '#a1a1aa',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        afterTitle: function(items) {
                            const idx = items[0].dataIndex;
                            return trainingstage[idx] ? '● Trainingstag' : '○ Kein Training';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Wochenkilometer
 */
function erstelleKmChart(daten, opts) {
    const ctx = document.getElementById('kmChart');
    if (!ctx || !daten.labels.length) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: daten.labels,
            datasets: [{
                label: 'km',
                data: daten.werte,
                backgroundColor: 'rgba(168, 85, 247, 0.5)',
                borderColor: '#a855f7',
                borderWidth: 1,
                borderRadius: 8,
                borderSkipped: false,
                hoverBackgroundColor: 'rgba(168, 85, 247, 0.8)'
            }]
        },
        options: {
            ...opts,
            plugins: { ...opts.plugins, legend: { display: false } },
            scales: {
                ...opts.scales,
                y: {
                    ...opts.scales.y,
                    beginAtZero: true,
                    title: { display: true, text: 'km', font: { size: 10 }, color: '#71717a' }
                }
            }
        }
    });
}

/**
 * Aerobic Efficiency
 */
function erstelleAeChart(daten, opts) {
    const ctx = document.getElementById('aeChart');
    if (!ctx || !daten.labels.length) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: formatiereLabels(daten.labels),
            datasets: [{
                label: 'Effizienz',
                data: daten.werte,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.04)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#f59e0b',
                pointBorderColor: '#18181b',
                pointBorderWidth: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...opts,
            plugins: {
                ...opts.plugins,
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#18181b',
                    borderColor: '#27272a',
                    borderWidth: 1,
                    titleColor: '#fafafa',
                    bodyColor: '#a1a1aa',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: (ctx) => `${ctx.parsed.y.toFixed(3)} sek/km pro bpm`
                    }
                }
            },
            scales: {
                ...opts.scales,
                y: {
                    ...opts.scales.y,
                    reverse: true,
                    title: { display: true, text: '↓ besser', font: { size: 10 }, color: '#71717a' }
                }
            }
        }
    });
}

/**
 * Labels kürzen
 */
function formatiereLabels(labels) {
    return labels.map(l => {
        if (!l || l.length < 10) return l;
        const t = l.split('-');
        return t.length === 3 ? `${t[2]}.${t[1]}.` : l;
    });
}

/**
 * Tab-Navigation
 */
function initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            const target = document.getElementById(tab.dataset.tab);
            if (target) target.classList.add('active');
        });
    });
}

document.addEventListener('DOMContentLoaded', initTabs);

/**
 * Cardiac Drift Chart
 */
function erstelleDriftChart(daten, opts) {
    const ctx = document.getElementById('driftChart');
    if (!ctx || !daten.labels || !daten.labels.length) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: formatiereLabels(daten.labels),
            datasets: [{
                label: 'Drift %',
                data: daten.werte,
                borderColor: '#f43f5e',
                backgroundColor: 'rgba(244, 63, 94, 0.05)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.3,
                pointRadius: 5,
                pointBackgroundColor: daten.werte.map(v => v < 5 ? '#10b981' : v < 10 ? '#f59e0b' : '#f43f5e'),
                pointBorderColor: '#18181b',
                pointBorderWidth: 2,
                pointHoverRadius: 7
            }]
        },
        options: {
            ...opts,
            plugins: {
                ...opts.plugins,
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#18181b',
                    borderColor: '#27272a',
                    borderWidth: 1,
                    titleColor: '#fafafa',
                    bodyColor: '#a1a1aa',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: (ctx) => {
                            const v = ctx.parsed.y;
                            const rating = v < 3 ? 'Exzellent' : v < 5 ? 'Gut' : v < 10 ? 'Moderat' : 'Hoch';
                            return `${v}% Drift (${rating})`;
                        }
                    }
                }
            },
            scales: {
                ...opts.scales,
                y: {
                    ...opts.scales.y,
                    beginAtZero: true,
                    max: 20,
                    title: { display: true, text: '% Drift', font: { size: 10 }, color: '#71717a' }
                }
            }
        }
    });
}

/**
 * Gewichts-Chart mit Ziellinie
 */
function erstelleWeightChart(daten, opts) {
    const ctx = document.getElementById('weightChart');
    if (!ctx || !daten.labels || !daten.labels.length) return;

    // Ziellinie als konstante Werte
    const zielLinie = daten.labels.map(() => daten.ziel);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: formatiereLabels(daten.labels),
            datasets: [
                {
                    label: 'Gewicht (kg)',
                    data: daten.werte,
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.05)',
                    borderWidth: 2.5,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 5,
                    pointBackgroundColor: '#a855f7',
                    pointBorderColor: '#18181b',
                    pointBorderWidth: 2
                },
                {
                    label: 'Zielgewicht',
                    data: zielLinie,
                    borderColor: '#10b981',
                    borderWidth: 1.5,
                    borderDash: [6, 4],
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }
            ]
        },
        options: {
            ...opts,
            plugins: {
                ...opts.plugins,
                tooltip: {
                    backgroundColor: '#18181b',
                    borderColor: '#27272a',
                    borderWidth: 1,
                    titleColor: '#fafafa',
                    bodyColor: '#a1a1aa',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} kg`
                    }
                }
            },
            scales: {
                ...opts.scales,
                y: {
                    ...opts.scales.y,
                    title: { display: true, text: 'kg', font: { size: 10 }, color: '#71717a' }
                }
            }
        }
    });
}

/**
 * Pace/HF Dual-Axis Chart (letzte 10 Läufe)
 */
function erstellePaceHfChart(daten, opts) {
    const ctx = document.getElementById('paceHfChart');
    if (!ctx || !daten.labels || !daten.labels.length) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: formatiereLabels(daten.labels),
            datasets: [
                {
                    label: 'Pace (sek/km)',
                    data: daten.pace,
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.05)',
                    borderWidth: 2.5,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 5,
                    pointBackgroundColor: '#a855f7',
                    pointBorderColor: '#18181b',
                    pointBorderWidth: 2,
                    yAxisID: 'y'
                },
                {
                    label: 'HF (bpm)',
                    data: daten.hf,
                    borderColor: '#f43f5e',
                    backgroundColor: 'rgba(244, 63, 94, 0.05)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: '#f43f5e',
                    pointBorderColor: '#18181b',
                    pointBorderWidth: 2,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20, usePointStyle: true, pointStyle: 'circle', font: { size: 11 }, color: '#a1a1aa' }
                },
                tooltip: {
                    backgroundColor: '#18181b',
                    borderColor: '#27272a',
                    borderWidth: 1,
                    titleColor: '#fafafa',
                    bodyColor: '#a1a1aa',
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(ctx) {
                            if (ctx.dataset.yAxisID === 'y') {
                                const min = Math.floor(ctx.parsed.y / 60);
                                const sec = Math.round(ctx.parsed.y % 60);
                                return `Pace: ${min}:${sec.toString().padStart(2, '0')}/km`;
                            }
                            return `HF: ${ctx.parsed.y} bpm`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 }, color: '#71717a' }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    reverse: true,
                    grid: { color: 'rgba(39, 39, 42, 0.5)', lineWidth: 0.5 },
                    ticks: {
                        font: { size: 10 },
                        color: '#a855f7',
                        callback: function(v) {
                            const min = Math.floor(v / 60);
                            const sec = Math.round(v % 60);
                            return `${min}:${sec.toString().padStart(2, '0')}`;
                        }
                    },
                    title: { display: true, text: 'Pace /km', font: { size: 10 }, color: '#a855f7' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    grid: { display: false },
                    ticks: { font: { size: 10 }, color: '#f43f5e' },
                    title: { display: true, text: 'HF bpm', font: { size: 10 }, color: '#f43f5e' }
                }
            }
        }
    });
}
