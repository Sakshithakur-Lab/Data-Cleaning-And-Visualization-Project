/**
 * CleanData Insights - Dashboard Application Logic (Chart.js + Interactive Table)
 */

document.addEventListener('DOMContentLoaded', async () => {
    // App State
    let metricsData = null;
    let cleanedDataset = [];
    let rawDataset = [];
    let currentDataMode = 'clean'; // 'clean' or 'raw'
    let currentPage = 1;
    const itemsPerPage = 20;

    // Chart instances store
    const charts = {};

    // 1. Initialize Navigation Tabs
    initTabs();

    // 2. Fetch JSON Data payloads
    await loadData();

    // 3. Populate Dashboard
    if (metricsData && cleanedDataset.length > 0) {
        populateKPICards();
        populateSummaryStatsTable();
        populateOutliersLog();
        initOverviewCharts();
        initPreprocessingCharts();
        initInteractiveAnalyticsCharts();
        initDatasetTable();
        initGalleryModal();
        initExportCSV();
    }

    // --- NAVIGATION TABS ---
    function initTabs() {
        const tabs = document.querySelectorAll('.nav-tab');
        const panes = document.querySelectorAll('.tab-pane');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.getAttribute('data-tab');

                tabs.forEach(t => t.classList.remove('active'));
                panes.forEach(p => p.classList.remove('active'));

                tab.classList.add('active');
                document.getElementById(`tab-${targetTab}`).classList.add('active');
            });
        });
    }

    // --- DATA LOADING ---
    async function loadData() {
        try {
            const [metricsRes, cleanRes, rawRes] = await Promise.all([
                fetch('../cleaning_metrics.json'),
                fetch('../cleaned_data.json'),
                fetch('../raw_data.json')
            ]);

            metricsData = await metricsRes.json();
            cleanedDataset = await cleanRes.json();
            rawDataset = await rawRes.json();
            console.log('Successfully loaded metrics & dataset payloads.');
        } catch (err) {
            console.error('Error loading JSON data files:', err);
        }
    }

    // --- KPI CARDS POPULATION ---
    function populateKPICards() {
        document.getElementById('val-raw-rows').textContent = metricsData.raw_total_rows.toLocaleString();
        document.getElementById('val-clean-rows').textContent = metricsData.cleaned_total_rows.toLocaleString();

        // Calculate total missing handled
        const totalMissing = Object.values(metricsData.missing_values_before).reduce((a, b) => a + b, 0);
        document.getElementById('val-missing-handled').textContent = totalMissing.toLocaleString();

        // Calculate total outliers handled
        const totalOutliers = Object.values(metricsData.outliers_handled).reduce((a, b) => a + b, 0);
        document.getElementById('val-outliers').textContent = totalOutliers.toLocaleString();

        // Calculate total revenue & AOV
        const totalRev = cleanedDataset.reduce((sum, item) => sum + (parseFloat(item.purchase_amount) || 0), 0);
        const aov = totalRev / (cleanedDataset.length || 1);

        document.getElementById('val-total-revenue').textContent = `$${Math.round(totalRev).toLocaleString()}`;
        document.getElementById('val-aov').textContent = `Avg Order: $${aov.toFixed(2)}`;
    }

    // --- SUMMARY STATS TABLE ---
    function populateSummaryStatsTable() {
        const tbody = document.getElementById('summary-stats-tbody');
        tbody.innerHTML = '';

        const before = metricsData.summary_stats_before || {};
        const after = metricsData.summary_stats_after || {};

        const metricNames = {
            'annual_income': 'Annual Income ($)',
            'purchase_amount': 'Purchase Amount ($)',
            'age': 'Customer Age (Years)',
            'customer_rating': 'Customer Rating (1-5)'
        };

        for (const [key, label] of Object.entries(metricNames)) {
            const b = before[key] || { mean: 0, median: 0 };
            const a = after[key] || { mean: 0, median: 0 };

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${label}</strong></td>
                <td>$${b.mean.toLocaleString()}</td>
                <td class="text-success"><strong>$${a.mean.toLocaleString()}</strong></td>
                <td>$${b.median.toLocaleString()}</td>
                <td class="text-success"><strong>$${a.median.toLocaleString()}</strong></td>
            `;
            tbody.appendChild(tr);
        }
    }

    // --- OUTLIERS LOG CONTAINER ---
    function populateOutliersLog() {
        const container = document.getElementById('outlier-log-container');
        container.innerHTML = '';

        const outliers = metricsData.outliers_handled || {};

        const labelMap = {
            'annual_income': 'Annual Income Outliers',
            'purchase_amount': 'Purchase Amount Outliers',
            'age': 'Invalid Age Entries (<18 or >85)',
            'customer_rating': 'Invalid Ratings (<1 or >5)'
        };

        for (const [col, count] of Object.entries(outliers)) {
            const label = labelMap[col] || col;
            const box = document.createElement('div');
            box.className = 'outlier-box';
            box.innerHTML = `
                <h3>${count}</h3>
                <p>${label} Capped</p>
            `;
            container.appendChild(box);
        }
    }

    // --- CHART 1 & 2: OVERVIEW TAB CHARTS ---
    function initOverviewCharts() {
        // Category Revenue Donut Chart
        const catRevMap = {};
        cleanedDataset.forEach(item => {
            const cat = item.product_category || 'Uncategorized';
            catRevMap[cat] = (catRevMap[cat] || 0) + (parseFloat(item.purchase_amount) || 0);
        });

        const catLabels = Object.keys(catRevMap);
        const catValues = Object.values(catRevMap);

        const ctxCat = document.getElementById('chart-overview-category').getContext('2d');
        charts.overviewCat = new Chart(ctxCat, {
            type: 'doughnut',
            data: {
                labels: catLabels,
                datasets: [{
                    data: catValues,
                    backgroundColor: ['#38bdf8', '#c084fc', '#34d399', '#fbbf24', '#f87171'],
                    borderWidth: 2,
                    borderColor: '#151d30'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: '#94a3b8', font: { family: 'Outfit' } } }
                }
            }
        });

        // RFM Segment Distribution Chart
        const rfmMap = {};
        cleanedDataset.forEach(item => {
            const seg = item.rfm_segment || 'Standard';
            rfmMap[seg] = (rfmMap[seg] || 0) + 1;
        });

        const ctxRfm = document.getElementById('chart-overview-rfm').getContext('2d');
        charts.overviewRfm = new Chart(ctxRfm, {
            type: 'bar',
            data: {
                labels: Object.keys(rfmMap),
                datasets: [{
                    label: 'Customer Count',
                    data: Object.values(rfmMap),
                    backgroundColor: '#c084fc',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    // --- PREPROCESSING TAB CHARTS ---
    function initPreprocessingCharts() {
        const before = metricsData.missing_values_before || {};
        const after = metricsData.missing_values_after || {};

        const cols = Object.keys(before).filter(c => before[c] > 0 || after[c] > 0);
        const bVals = cols.map(c => before[c] || 0);
        const aVals = cols.map(c => after[c] || 0);

        const ctx = document.getElementById('chart-missing-before-after').getContext('2d');
        charts.missingChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: cols,
                datasets: [
                    { label: 'Before Cleaning (Raw)', data: bVals, backgroundColor: '#f87171', borderRadius: 6 },
                    { label: 'After Cleaning (Imputed)', data: aVals, backgroundColor: '#34d399', borderRadius: 6 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    // --- INTERACTIVE ANALYTICS TAB CHARTS ---
    function initInteractiveAnalyticsCharts() {
        renderInteractiveCharts(cleanedDataset);

        // Filter event listeners
        const catSelect = document.getElementById('filter-category');
        const segSelect = document.getElementById('filter-segment');
        const resetBtn = document.getElementById('btn-reset-filters');

        function applyFilters() {
            const cat = catSelect.value;
            const seg = segSelect.value;

            let filtered = cleanedDataset.filter(item => {
                const matchCat = (cat === 'ALL' || item.product_category === cat);
                const matchSeg = (seg === 'ALL' || item.customer_segment === seg);
                return matchCat && matchSeg;
            });

            renderInteractiveCharts(filtered);
        }

        catSelect.addEventListener('change', applyFilters);
        segSelect.addEventListener('change', applyFilters);
        resetBtn.addEventListener('click', () => {
            catSelect.value = 'ALL';
            segSelect.value = 'ALL';
            renderInteractiveCharts(cleanedDataset);
        });
    }

    function renderInteractiveCharts(data) {
        // 1. Monthly Revenue Line Chart
        const monthRev = {};
        data.forEach(item => {
            const ym = item.year_month || '2024-01';
            monthRev[ym] = (monthRev[ym] || 0) + (parseFloat(item.purchase_amount) || 0);
        });

        const sortedYm = Object.keys(monthRev).sort();
        const monthlyVals = sortedYm.map(k => Math.round(monthRev[k]));

        const ctxMonthly = document.getElementById('chart-monthly-trend').getContext('2d');
        if (charts.monthlyTrend) charts.monthlyTrend.destroy();
        charts.monthlyTrend = new Chart(ctxMonthly, {
            type: 'line',
            data: {
                labels: sortedYm,
                datasets: [{
                    label: 'Monthly Revenue ($)',
                    data: monthlyVals,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });

        // 2. Category Revenue Bar Chart
        const catMap = {};
        data.forEach(item => {
            const c = item.product_category || 'Uncategorized';
            catMap[c] = (catMap[c] || 0) + (parseFloat(item.purchase_amount) || 0);
        });

        const ctxCat = document.getElementById('chart-cat-revenue').getContext('2d');
        if (charts.catRev) charts.catRev.destroy();
        charts.catRev = new Chart(ctxCat, {
            type: 'bar',
            data: {
                labels: Object.keys(catMap),
                datasets: [{
                    label: 'Revenue ($)',
                    data: Object.values(catMap),
                    backgroundColor: '#2dd4bf',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });

        // 3. Scatter Plot Age vs Income
        const scatterData = data.slice(0, 300).map(item => ({
            x: parseFloat(item.age) || 30,
            y: parseFloat(item.annual_income) || 50000
        }));

        const ctxScatter = document.getElementById('chart-scatter-income-age').getContext('2d');
        if (charts.scatter) charts.scatter.destroy();
        charts.scatter = new Chart(ctxScatter, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Customers (Age vs Income)',
                    data: scatterData,
                    backgroundColor: 'rgba(192, 132, 252, 0.7)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: 'Age (Years)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { title: { display: true, text: 'Income ($)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });

        // 4. Ratings Bar Chart
        const ratMap = { '1-2 Stars': 0, '2-3 Stars': 0, '3-4 Stars': 0, '4-5 Stars': 0 };
        data.forEach(item => {
            const r = parseFloat(item.customer_rating) || 4.0;
            if (r < 2) ratMap['1-2 Stars']++;
            else if (r < 3) ratMap['2-3 Stars']++;
            else if (r < 4) ratMap['3-4 Stars']++;
            else ratMap['4-5 Stars']++;
        });

        const ctxRating = document.getElementById('chart-ratings-dist').getContext('2d');
        if (charts.rating) charts.rating.destroy();
        charts.rating = new Chart(ctxRating, {
            type: 'bar',
            data: {
                labels: Object.keys(ratMap),
                datasets: [{
                    label: 'Rating Count',
                    data: Object.values(ratMap),
                    backgroundColor: ['#f87171', '#fbbf24', '#38bdf8', '#34d399'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });
    }

    // --- DATASET EXPLORER TABLE ---
    function initDatasetTable() {
        const btnClean = document.getElementById('btn-mode-clean');
        const btnRaw = document.getElementById('btn-mode-raw');
        const searchInput = document.getElementById('table-search');
        const btnPrev = document.getElementById('btn-prev-page');
        const btnNext = document.getElementById('btn-next-page');

        btnClean.addEventListener('click', () => {
            currentDataMode = 'clean';
            btnClean.classList.add('active');
            btnRaw.classList.remove('active');
            currentPage = 1;
            renderTable();
        });

        btnRaw.addEventListener('click', () => {
            currentDataMode = 'raw';
            btnRaw.classList.add('active');
            btnClean.classList.remove('active');
            currentPage = 1;
            renderTable();
        });

        searchInput.addEventListener('input', () => {
            currentPage = 1;
            renderTable();
        });

        btnPrev.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderTable();
            }
        });

        btnNext.addEventListener('click', () => {
            const data = currentDataMode === 'clean' ? cleanedDataset : rawDataset;
            const filtered = filterData(data, searchInput.value);
            const totalPages = Math.ceil(filtered.length / itemsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                renderTable();
            }
        });

        renderTable();
    }

    function filterData(data, query) {
        if (!query || query.trim() === '') return data;
        const q = query.toLowerCase();
        return data.filter(row => {
            return Object.values(row).some(val => String(val).toLowerCase().includes(q));
        });
    }

    function renderTable() {
        const data = currentDataMode === 'clean' ? cleanedDataset : rawDataset;
        const searchVal = document.getElementById('table-search').value;
        const filtered = filterData(data, searchVal);

        const totalPages = Math.ceil(filtered.length / itemsPerPage) || 1;
        currentPage = Math.min(currentPage, totalPages);

        document.getElementById('current-page').textContent = currentPage;
        document.getElementById('total-pages').textContent = totalPages;
        document.getElementById('record-count-badge').textContent = `Showing ${filtered.length.toLocaleString()} records`;

        document.getElementById('btn-prev-page').disabled = (currentPage === 1);
        document.getElementById('btn-next-page').disabled = (currentPage >= totalPages);

        const startIdx = (currentPage - 1) * itemsPerPage;
        const pageData = filtered.slice(startIdx, startIdx + itemsPerPage);

        const headerTr = document.getElementById('table-headers');
        const bodyTbody = document.getElementById('table-body');

        if (pageData.length === 0) {
            headerTr.innerHTML = '<th>No Data</th>';
            bodyTbody.innerHTML = '<tr><td class="text-center p-4">No matching records found</td></tr>';
            return;
        }

        // Headers
        const cols = Object.keys(pageData[0]);
        headerTr.innerHTML = cols.map(c => `<th>${c.replace(/_/g, ' ').toUpperCase()}</th>`).join('');

        // Rows
        bodyTbody.innerHTML = pageData.map(row => {
            return `<tr>${cols.map(c => {
                let val = row[c];
                if (val === null || val === undefined) val = '<span class="text-muted">null</span>';
                return `<td>${val}</td>`;
            }).join('')}</tr>`;
        }).join('');
    }

    // --- GALLERY LIGHTBOX MODAL ---
    function initGalleryModal() {
        const modal = document.getElementById('image-modal');
        const modalImg = document.getElementById('modal-img');
        const modalCaption = document.getElementById('modal-caption');
        const closeBtn = document.querySelector('.modal-close');

        document.querySelectorAll('.gallery-item').forEach(item => {
            item.addEventListener('click', () => {
                const imgPath = item.getAttribute('data-img');
                const title = item.querySelector('h4').textContent;
                modal.style.display = 'flex';
                modalImg.src = imgPath;
                modalCaption.textContent = title;
            });
        });

        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.style.display = 'none';
        });
    }

    // --- CSV EXPORT FUNCTIONALITY ---
    function initExportCSV() {
        const btnExport = document.getElementById('btn-export-csv');
        btnExport.addEventListener('click', () => {
            if (!cleanedDataset || cleanedDataset.length === 0) return;

            const headers = Object.keys(cleanedDataset[0]);
            let csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n";

            cleanedDataset.forEach(row => {
                const line = headers.map(h => `"${String(row[h] || '').replace(/"/g, '""')}"`).join(",");
                csvContent += line + "\n";
            });

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", "cleaned_e_commerce_dataset.csv");
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }
});
