/**
 * Admin Dashboard JavaScript
 * Handles authentication, data fetching, and chart rendering
 */

const API_BASE_URL = 'http://localhost:8000';
let authToken = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    authToken = localStorage.getItem('admin_token');
    if (authToken) {
        showDashboard();
        loadDashboardData();
    } else {
        showLogin();
    }
    
    // Setup login form
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
});

function showLogin() {
    document.getElementById('loginScreen').classList.remove('hidden');
    document.getElementById('dashboardScreen').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('loginScreen').classList.add('hidden');
    document.getElementById('dashboardScreen').classList.remove('hidden');
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('loginError');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('admin_token', authToken);
        
        showDashboard();
        loadDashboardData();
        
    } catch (error) {
        console.error('Login error:', error);
        errorEl.textContent = error.message;
        errorEl.classList.remove('hidden');
    }
}

function logout() {
    authToken = null;
    localStorage.removeItem('admin_token');
    showLogin();
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

async function loadDashboardData() {
    const loadingEl = document.getElementById('loading');
    const errorEl = document.getElementById('error');
    const contentEl = document.getElementById('dashboardContent');
    
    try {
        loadingEl.classList.remove('hidden');
        errorEl.classList.add('hidden');
        contentEl.classList.add('hidden');
        
        // Fetch dashboard data
        const [segmentsData, eventsData, rulesData, insightsData] = await Promise.all([
            fetchAPI('/api/admin/segments'),
            fetchAPI('/api/admin/events?hours=24'),
            fetchAPI('/api/admin/rules'),
            fetchAPI('/api/admin/insights')
        ]);
        
        // Update stats
        updateStats(segmentsData, eventsData, rulesData);
        
        // Render charts
        renderSegmentChart(segmentsData.distribution);
        renderEventsChart(eventsData.top_events);
        
        // Render insights
        renderInsights(insightsData.insights);
        
        loadingEl.classList.add('hidden');
        contentEl.classList.remove('hidden');
        
    } catch (error) {
        console.error('Dashboard data load error:', error);
        loadingEl.classList.add('hidden');
        errorEl.textContent = `Failed to load dashboard: ${error.message}`;
        errorEl.classList.remove('hidden');
        
        // If unauthorized, logout
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            logout();
        }
    }
}

async function fetchAPI(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
}

function updateStats(segmentsData, eventsData, rulesData) {
    document.getElementById('totalVisitors').textContent = segmentsData.total_users || 0;
    document.getElementById('totalSegments').textContent = Object.keys(segmentsData.distribution || {}).length;
    document.getElementById('totalEvents').textContent = eventsData.total_events || 0;
    document.getElementById('totalRules').textContent = rulesData.total_rules || 0;
}

let segmentChart = null;
let eventsChart = null;

function renderSegmentChart(distribution) {
    const ctx = document.getElementById('segmentChart').getContext('2d');
    
    // Destroy existing chart
    if (segmentChart) {
        segmentChart.destroy();
    }
    
    const labels = Object.keys(distribution || {});
    const data = Object.values(distribution || {});
    
    segmentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.map(l => l.replace('_', ' ')),
            datasets: [{
                data: data,
                backgroundColor: [
                    '#3b82f6', // blue
                    '#10b981', // green
                    '#f59e0b', // amber
                    '#ef4444', // red
                    '#8b5cf6'  // purple
                ],
                borderWidth: 2,
                borderColor: '#1e293b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function renderEventsChart(topEvents) {
    const ctx = document.getElementById('eventsChart').getContext('2d');
    
    // Destroy existing chart
    if (eventsChart) {
        eventsChart.destroy();
    }
    
    const labels = Object.keys(topEvents || {}).slice(0, 10);
    const data = Object.values(topEvents || {}).slice(0, 10);
    
    eventsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => l.replace('_', ' ')),
            datasets: [{
                label: 'Event Count',
                data: data,
                backgroundColor: '#3b82f6',
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            size: 11
                        },
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function renderInsights(insights) {
    const container = document.getElementById('insightsContainer');
    container.innerHTML = '';
    
    if (!insights || insights.length === 0) {
        container.innerHTML = '<p style="color: #94a3b8;">No insights available yet. Check back after more data is collected.</p>';
        return;
    }
    
    insights.forEach(insight => {
        const card = document.createElement('div');
        card.className = 'insight-card';
        
        const header = document.createElement('h4');
        header.textContent = insight.segment || 'General Insight';
        card.appendChild(header);
        
        const summary = document.createElement('p');
        summary.textContent = insight.reasoning || insight.summary;
        card.appendChild(summary);
        
        // Render xAI explanation if available
        if (insight.xai_explanation) {
            const xaiEl = document.createElement('div');
            xaiEl.className = 'xai-explanation';
            
            const sections = [
                { label: 'WHAT', key: 'what' },
                { label: 'WHY', key: 'why' },
                { label: 'SO WHAT', key: 'so_what' },
                { label: 'RECOMMENDATION', key: 'recommendation' }
            ];
            
            sections.forEach(({ label, key }) => {
                if (insight.xai_explanation[key]) {
                    const section = document.createElement('div');
                    section.className = 'xai-section';
                    
                    const labelEl = document.createElement('div');
                    labelEl.className = 'xai-label';
                    labelEl.textContent = label;
                    section.appendChild(labelEl);
                    
                    const contentEl = document.createElement('div');
                    contentEl.className = 'xai-content';
                    contentEl.textContent = insight.xai_explanation[key];
                    section.appendChild(contentEl);
                    
                    xaiEl.appendChild(section);
                }
            });
            
            card.appendChild(xaiEl);
        }
        
        container.appendChild(card);
    });
}

// Auto-refresh every 30 seconds
setInterval(() => {
    if (authToken && !document.getElementById('dashboardScreen').classList.contains('hidden')) {
        loadDashboardData();
    }
}, 30000);
