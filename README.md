# Data Cleaning & Visual Analytics Studio 📊✨

An end-to-end Python data preprocessing pipeline, statistical visualization suite, and interactive web dashboard for real-world messy dataset remediation and exploratory data storytelling.

---

## 🌟 Key Features

- **Messy Dataset Synthesis**: Simulates real-world data quality flaws including missing entries, unparsed currencies, string whitespace/casing inconsistencies, extreme outliers, and duplicate transactions.
- **Robust Preprocessing Pipeline (`data_cleaner.py`)**:
  - **Deduplication**: Identifies and removes exact duplicate rows and duplicate transaction IDs.
  - **Text & Date Standardization**: Normalizes strings, strips currency symbols (`$`, `,`), and standardizes heterogeneous date formats to ISO `YYYY-MM-DD`.
  - **Imputation Engine**: Employs category-wise and segment-wise medians/modes to impute missing metrics without mean-bias.
  - **Outlier Capping**: Detects extreme non-sensical values using Interquartile Range (IQR $Q3 + 1.5 \times IQR$) limits and domain constraints.
  - **Feature Engineering**: Derives RFM (Recency, Frequency, Monetary) customer segments, age groups, income brackets, and temporal features.
- **Statistical Visualization Suite (`data_visualizer.py`)**:
  - Generates 7 high-resolution publication-quality graphics using Seaborn & Matplotlib.
- **Interactive Web Dashboard**:
  - Built with Vanilla HTML5, modern dark glassmorphic CSS3, and Chart.js.
  - Features real-time KPI metrics, interactive chart filtering, Seaborn report gallery, and searchable dataset explorer.

---

## 📂 Project Architecture

```
data_cleaning_viz_project/
├── generate_raw_data.py    # Synthesizes raw messy e-commerce dataset
├── data_cleaner.py         # Core Python DataCleaner preprocessing engine
├── data_visualizer.py      # Seaborn & Matplotlib visual report generator
├── main.py                 # Pipeline master orchestrator & web server launcher
├── test_pipeline.py        # Automated test suite & data quality assertions
├── raw_e_commerce_data.csv # Generated raw dataset with flaws
├── cleaned_e_commerce_data.csv # Fully preprocessed & cleaned dataset
├── cleaning_metrics.json   # JSON metrics tracking before/after statistics
├── raw_data.json           # JSON payload for frontend
├── cleaned_data.json       # JSON payload for frontend
├── static/
│   └── visualizations/     # 7 generated PNG statistical graphics
└── dashboard/
    ├── index.html          # Web Dashboard UI
    ├── styles.css          # Dark glassmorphism CSS theme
    └── app.js              # Chart.js & dataset table interactive logic
```

---

## 🚀 Quick Start Guide

### 1. Run full end-to-end pipeline:
```bash
python3 main.py
```

### 2. Launch the Interactive Web Dashboard server:
```bash
python3 main.py --serve
```
Open your web browser and navigate to:
`http://localhost:8080/dashboard/index.html`

### 3. Run Automated Tests & Quality Verification:
```bash
python3 -m unittest test_pipeline.py
```

---

## 📈 Visual Report Artifacts

1. `01_missing_data_analysis.png`: Missing value breakdown (Before vs After) & missingness matrix.
2. `02_outlier_detection_boxplots.png`: Raw vs winsorized boxplots for Income and Spend.
3. `03_customer_demographics.png`: Customer age distribution, income brackets, and top cities.
4. `04_sales_trends_time_series.png`: Monthly revenue trendline with 3-month moving average.
5. `05_category_performance.png`: Product category revenue, AOV, and customer rating violin plots.
6. `06_correlation_heatmap.png`: Feature correlation matrix heatmap.
7. `07_rfm_customer_segmentation.png`: Recency vs Monetary spend scatter plot by RFM segment.
