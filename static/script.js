
document.addEventListener('DOMContentLoaded', () => {
    // --- Tabs Logic ---
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // --- Chart.js Setup ---
    const ctx = document.getElementById('efficiencyChart').getContext('2d');
    const ctxPie = document.getElementById('distributionChart').getContext('2d');
    let chart; // Global chart instance
    let pieChart; // Pie chart instance

    function initChart() {
        chart = new Chart(ctx, {
            type: 'bar', // Using bar chart to show comparison
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Target Hours',
                        data: [],
                        backgroundColor: 'rgba(59, 130, 246, 0.5)',
                        borderColor: '#3b82f6',
                        borderWidth: 1
                    },
                    {
                        label: 'Actual Hours',
                        data: [],
                        backgroundColor: 'rgba(16, 185, 129, 0.5)',
                        borderColor: '#10b981',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc' } },
                    title: { display: true, text: 'Efficiency Goals vs Actual', color: '#f8fafc' }
                }
            }
        });

        pieChart = new Chart(ctxPie, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    label: 'Actual Time (Hours)',
                    data: [],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(139, 92, 246, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(239, 68, 68, 0.7)'
                    ],
                    borderColor: 'rgba(30, 41, 59, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: '#f8fafc' } },
                    title: { display: true, text: 'Time Distribution', color: '#f8fafc' }
                }
            }
        });
    }

    // --- Data Fetching ---
    async function loadStats() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();

            updateChart(data);
            updateTextStats(data);
        } catch (err) {
            console.error('Error fetching stats:', err);
        }
    }

    function updateChart(data) {
        if (!data || data.length === 0) return;

        const labels = data.map(d => d.category);
        const targets = data.map(d => d.target_hours_per_week);
        const actuals = data.map(d => d['Actual Hours']);

        chart.data.labels = labels;
        chart.data.datasets[0].data = targets;
        chart.data.datasets[1].data = actuals;
        chart.update();

        pieChart.data.labels = labels;
        pieChart.data.datasets[0].data = actuals;
        pieChart.update();
    }

    function updateTextStats(data) {
        const container = document.getElementById('stats-text');
        container.innerHTML = '';

        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'stat-item';
            div.innerHTML = `
                <div class="stat-val">${item['Efficiency %']}%</div>
                <div class="stat-label">${item.category}</div>
            `;
            container.appendChild(div);
        });
    }

    // --- AI Prediction ---
    const activityInput = document.getElementById('activityName');
    const categoryInput = document.getElementById('category');
    const aiChip = document.getElementById('ai-suggestion');
    const suggestedCatSpan = document.getElementById('suggested-cat');
    const acceptAiBtn = document.getElementById('accept-ai');

    // Debounce listener
    let timeout = null;
    activityInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        const val = e.target.value;

        if (val.length < 3) {
            aiChip.classList.add('hidden');
            return;
        }

        timeout = setTimeout(async () => {
            const res = await fetch(`/api/predict_category?activity=${encodeURIComponent(val)}`);
            const data = await res.json();

            if (data.category) {
                suggestedCatSpan.textContent = data.category;
                aiChip.classList.remove('hidden');
            } else {
                aiChip.classList.add('hidden');
            }
        }, 500);
    });

    acceptAiBtn.addEventListener('click', () => {
        categoryInput.value = suggestedCatSpan.textContent;
        aiChip.classList.add('hidden');
    });

    // --- Form Handling ---
    async function submitForm(url, data) {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    }

    function showToast(msg) {
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.classList.remove('hidden');
        setTimeout(() => toast.classList.add('hidden'), 3000);
    }

    document.getElementById('logForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const activity = document.getElementById('activityName').value;
        const category = document.getElementById('category').value;
        const duration = document.getElementById('duration').value;

        const res = await submitForm('/api/log', { activity, category, duration });
        showToast(res.message || res.error);
        if (!res.error) {
            e.target.reset();
            loadStats(); // refresh chart
        }
    });

    document.getElementById('goalForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const category = document.getElementById('goalCategory').value;
        const hours = document.getElementById('goalHours').value;

        const res = await submitForm('/api/goal', { category, hours });
        showToast(res.message || res.error);
        if (!res.error) {
            loadStats();
        }
    });

    document.getElementById('trainBtn').addEventListener('click', async () => {
        const res = await submitForm('/api/train_model', {});
        showToast(res.message);
    });

    // --- Chat Widget Logic ---
    const chatToggle = document.getElementById('chat-toggle');
    const chatWidget = document.getElementById('chat-widget');
    const closeChatBtn = document.getElementById('close-chat');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    chatToggle.addEventListener('click', () => {
        chatWidget.classList.remove('hidden');
        chatToggle.style.display = 'none';
    });

    closeChatBtn.addEventListener('click', () => {
        chatWidget.classList.add('hidden');
        chatToggle.style.display = 'flex';
    });

    function addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msgText = chatInput.value.trim();
        if (!msgText) return;

        addMessage(msgText, 'user');
        chatInput.value = '';

        const loadingMsg = addMessage('...', 'ai');
        loadingMsg.classList.add('loading-dots');

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msgText })
            });
            const data = await res.json();
            
            chatMessages.removeChild(loadingMsg);
            if (data.error) {
                addMessage(data.error, 'ai');
            } else {
                addMessage(data.response, 'ai');
            }
        } catch (err) {
            chatMessages.removeChild(loadingMsg);
            addMessage('Error connecting to AI.', 'ai');
        }
    });

    // --- SECOND CHART: Time Distribution (Pie) ---
    const distCtx = document.getElementById('distributionChart').getContext('2d');
    let distChart;

    function initDistChart() {
        distChart = new Chart(distCtx, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    label: 'Actual Hours',
                    data: [],
                    backgroundColor: [
                        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1'
                    ],
                    borderWidth: 1,
                    borderColor: 'rgba(255,255,255,0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: '#f8fafc' } }
                }
            }
        });
    }

    // Override updateChart to also update pie chart
    const originalUpdateChart = updateChart;
    updateChart = function(data) {
        originalUpdateChart(data);
        if (!data || data.length === 0) return;

        if (distChart) {
            distChart.data.labels = data.map(d => d.category);
            distChart.data.datasets[0].data = data.map(d => d['Actual Hours']);
            distChart.update();
        }
    };

    // Init
    initChart();
    initDistChart();
    loadStats();
});
