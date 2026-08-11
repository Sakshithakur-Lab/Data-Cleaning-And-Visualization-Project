#!/usr/bin/env python3
"""
data_visualizer.py
Generates publication-quality statistical visual report graphics
using Matplotlib and Seaborn for data preprocessing and EDA storytelling.
Outputs PNG files into static/visualizations/ directory.
"""

import os
import tempfile
# Ensure matplotlib has a writable config directory
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib_cache")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set global seaborn theme & aesthetic parameters
sns.set_theme(style="darkgrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['figure.autolayout'] = True
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

DARK_BG = "#0f172a"
CARD_BG = "#1e293b"
ACCENT_BLUE = "#38bdf8"
ACCENT_PURPLE = "#c084fc"
ACCENT_GREEN = "#4ade80"
ACCENT_ORANGE = "#fb923c"
ACCENT_RED = "#f87171"

class DataVisualizer:
    def __init__(self, df_raw, df_clean, output_dir):
        self.df_raw = df_raw.copy()
        self.df_clean = df_clean.copy()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _save_fig(self, fig, filename):
        filepath = os.path.join(self.output_dir, filename)
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Generated chart: {filepath}")

    def plot_missing_data_analysis(self, metrics):
        """Plot 01: Missing Data Before vs After Cleaning."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Subplot 1: Bar chart comparison
        before = metrics.get("missing_values_before", {})
        after = metrics.get("missing_values_after", {})
        
        cols = [c for c in before.keys() if before[c] > 0 or after.get(c, 0) > 0]
        if not cols:
            cols = list(before.keys())[:6]
            
        b_vals = [before.get(c, 0) for c in cols]
        a_vals = [after.get(c, 0) for c in cols]
        
        x = np.arange(len(cols))
        width = 0.35
        
        ax1.bar(x - width/2, b_vals, width, label='Before Cleaning (Raw)', color='#f87171', alpha=0.9)
        ax1.bar(x + width/2, a_vals, width, label='After Cleaning (Imputed)', color='#4ade80', alpha=0.9)
        
        ax1.set_ylabel('Missing Values Count')
        ax1.set_title('Missing Values per Feature: Before vs. After Imputation', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(cols, rotation=45, ha='right')
        ax1.legend()
        
        # Subplot 2: Heatmap matrix of missingness in raw data
        raw_nulls = self.df_raw.isnull()
        sns.heatmap(raw_nulls, cbar=False, cmap='magma', ax=ax2, yticklabels=False)
        ax2.set_title('Raw Dataset Missingness Matrix (Yellow = Missing)', fontweight='bold')
        ax2.set_xlabel('Features')
        
        plt.suptitle('Data Preprocessing Report: Missing Value Remediation', fontsize=16, fontweight='bold', y=1.02)
        self._save_fig(fig, '01_missing_data_analysis.png')

    def plot_outlier_boxplots(self):
        """Plot 02: Outlier Detection and Capping (Raw vs Cleaned)."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Income
        raw_income = pd.to_numeric(self.df_raw['Annual_Income'].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
        sns.boxplot(y=raw_income.dropna(), ax=axes[0, 0], color='#f87171')
        axes[0, 0].set_title('Raw Annual Income (Uncapped Outliers)', fontweight='bold')
        axes[0, 0].set_ylabel('Annual Income ($)')
        
        sns.boxplot(y=self.df_clean['annual_income'], ax=axes[0, 1], color='#38bdf8')
        axes[0, 1].set_title('Cleaned Annual Income (Winsorized IQR Capped)', fontweight='bold')
        axes[0, 1].set_ylabel('Annual Income ($)')

        # 2. Purchase Amount
        raw_amount = pd.to_numeric(self.df_raw['Purchase_Amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True), errors='coerce')
        sns.boxplot(y=raw_amount.dropna(), ax=axes[1, 0], color='#f87171')
        axes[1, 0].set_title('Raw Purchase Amount (Uncapped Outliers)', fontweight='bold')
        axes[1, 0].set_ylabel('Purchase Amount ($)')

        sns.boxplot(y=self.df_clean['purchase_amount'], ax=axes[1, 1], color='#c084fc')
        axes[1, 1].set_title('Cleaned Purchase Amount (IQR Capped)', fontweight='bold')
        axes[1, 1].set_ylabel('Purchase Amount ($)')
        
        plt.suptitle('Outlier Management: IQR & Percentile Boundary Capping', fontsize=16, fontweight='bold', y=1.02)
        self._save_fig(fig, '02_outlier_detection_boxplots.png')

    def plot_customer_demographics(self):
        """Plot 03: Customer Demographics Analysis."""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Age Distribution
        sns.histplot(self.df_clean['age'], kde=True, ax=axes[0], color='#38bdf8', bins=15)
        axes[0].set_title('Customer Age Distribution', fontweight='bold')
        axes[0].set_xlabel('Age (Years)')
        
        # Income Brackets
        if 'income_bracket' in self.df_clean.columns:
            sns.countplot(x='income_bracket', hue='income_bracket', data=self.df_clean, ax=axes[1], palette='crest', legend=False)
            axes[1].set_title('Customer Income Brackets', fontweight='bold')
            axes[1].set_xlabel('Income Bracket')
            axes[1].tick_params(axis='x', rotation=30)
            
        # Top Cities
        top_cities = self.df_clean['city'].value_counts().head(8)
        sns.barplot(x=top_cities.values, y=top_cities.index, hue=top_cities.index, ax=axes[2], palette='viridis', legend=False)
        axes[2].set_title('Customer Volume by Top Cities', fontweight='bold')
        axes[2].set_xlabel('Order / Customer Count')
        
        plt.suptitle('Customer Demographics & Geographic Insights', fontsize=16, fontweight='bold', y=1.03)
        self._save_fig(fig, '03_customer_demographics.png')

    def plot_sales_trends_time_series(self):
        """Plot 04: Monthly Revenue & Order Volume Time Series."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
        
        monthly_df = self.df_clean.groupby('year_month').agg(
            total_revenue=('purchase_amount', 'sum'),
            order_count=('purchase_amount', 'count')
        ).reset_index()
        
        monthly_df['revenue_3m_ma'] = monthly_df['total_revenue'].rolling(window=3, min_periods=1).mean()
        
        # Revenue trend
        ax1.plot(monthly_df['year_month'], monthly_df['total_revenue'], marker='o', color='#38bdf8', linewidth=2.5, label='Monthly Revenue ($)')
        ax1.plot(monthly_df['year_month'], monthly_df['revenue_3m_ma'], linestyle='--', color='#fb923c', linewidth=2, label='3-Month Moving Average')
        ax1.set_ylabel('Total Revenue ($)')
        ax1.set_title('Monthly Revenue Performance & Trendline', fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, linestyle=':', alpha=0.6)
        
        # Order volume
        ax2.bar(monthly_df['year_month'], monthly_df['order_count'], color='#c084fc', alpha=0.85)
        ax2.set_ylabel('Order Count')
        ax2.set_xlabel('Year-Month')
        ax2.set_title('Monthly Transaction Volume', fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.suptitle('E-Commerce Revenue & Order Growth Dynamics', fontsize=16, fontweight='bold', y=1.02)
        self._save_fig(fig, '04_sales_trends_time_series.png')

    def plot_category_performance(self):
        """Plot 05: Product Category Performance & AOV."""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        cat_stats = self.df_clean.groupby('product_category').agg(
            revenue=('purchase_amount', 'sum'),
            aov=('purchase_amount', 'mean'),
            avg_rating=('customer_rating', 'mean')
        ).reset_index().sort_values(by='revenue', ascending=False)
        
        # Revenue by Category
        sns.barplot(x='revenue', y='product_category', hue='product_category', data=cat_stats, ax=axes[0], palette='plasma', legend=False)
        axes[0].set_title('Total Revenue by Category ($)', fontweight='bold')
        axes[0].set_xlabel('Revenue ($)')
        
        # Average Order Value
        sns.barplot(x='aov', y='product_category', hue='product_category', data=cat_stats.sort_values('aov', ascending=False), ax=axes[1], palette='mako', legend=False)
        axes[1].set_title('Average Order Value (AOV)', fontweight='bold')
        axes[1].set_xlabel('AOV ($)')
        
        # Rating Distribution by Category
        sns.violinplot(x='customer_rating', y='product_category', hue='product_category', data=self.df_clean, ax=axes[2], palette='rocket', inner='quartile', legend=False)
        axes[2].set_title('Customer Rating Distribution by Category', fontweight='bold')
        axes[2].set_xlabel('Rating (1 - 5 Stars)')
        
        plt.suptitle('Product Category Financial & Satisfaction Analytics', fontsize=16, fontweight='bold', y=1.03)
        self._save_fig(fig, '05_category_performance.png')

    def plot_correlation_heatmap(self):
        """Plot 06: Correlation Heatmap of Cleaned Features."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        num_cols = ['age', 'annual_income', 'purchase_amount', 'customer_rating', 'recency_days', 'frequency_orders', 'monetary_total']
        num_cols = [c for c in num_cols if c in self.df_clean.columns]
        
        corr_matrix = self.df_clean[num_cols].corr()
        
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(
            corr_matrix,
            mask=mask,
            annot=True,
            fmt=".2f",
            cmap='coolwarm',
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title('Correlation Matrix of Customer & Financial Metrics', fontsize=15, fontweight='bold', pad=15)
        self._save_fig(fig, '06_correlation_heatmap.png')

    def plot_rfm_segmentation(self):
        """Plot 07: RFM Customer Segmentation Storytelling."""
        if 'rfm_segment' not in self.df_clean.columns:
            return
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Segment distribution bar plot
        seg_counts = self.df_clean['rfm_segment'].value_counts().reset_index()
        seg_counts.columns = ['rfm_segment', 'count']
        
        sns.barplot(x='count', y='rfm_segment', hue='rfm_segment', data=seg_counts, ax=ax1, palette='Set2', legend=False)
        ax1.set_title('Customer Count by RFM Segment', fontweight='bold')
        ax1.set_xlabel('Number of Unique Customers')
        
        # Annotate bars
        for p in ax1.patches:
            width = p.get_width()
            ax1.annotate(f'{int(width)}', (width + 5, p.get_y() + p.get_height() / 2),
                         ha='left', va='center', fontsize=10, color='white')
                         
        # 2. Scatter Recency vs Monetary Total by Segment
        unique_cust = self.df_clean.drop_duplicates(subset=['customer_id'])
        sns.scatterplot(
            x='recency_days',
            y='monetary_total',
            hue='rfm_segment',
            style='rfm_segment',
            data=unique_cust,
            s=80,
            alpha=0.85,
            palette='tab10',
            ax=ax2
        )
        ax2.set_title('Customer Value Matrix: Recency vs. Total Spend', fontweight='bold')
        ax2.set_xlabel('Recency (Days since last purchase)')
        ax2.set_ylabel('Monetary Total ($)')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.suptitle('Customer RFM Segmentation & Behavior Analysis', fontsize=16, fontweight='bold', y=1.02)
        self._save_fig(fig, '07_rfm_customer_segmentation.png')

    def generate_all_plots(self, metrics):
        """Execute all visualization plot generators."""
        print("Generating Statistical Visualizations...")
        self.plot_missing_data_analysis(metrics)
        self.plot_outlier_boxplots()
        self.plot_customer_demographics()
        self.plot_sales_trends_time_series()
        self.plot_category_performance()
        self.plot_correlation_heatmap()
        self.plot_rfm_segmentation()
        print("All visual reports generated successfully!")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_dir, "raw_e_commerce_data.csv")
    cleaned_path = os.path.join(base_dir, "cleaned_e_commerce_data.csv")
    metrics_path = os.path.join(base_dir, "cleaning_metrics.json")
    out_dir = os.path.join(base_dir, "static", "visualizations")
    
    if os.path.exists(raw_path) and os.path.exists(cleaned_path):
        df_raw = pd.read_csv(raw_path)
        df_clean = pd.read_csv(cleaned_path)
        
        metrics = {}
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
                
        viz = DataVisualizer(df_raw, df_clean, out_dir)
        viz.generate_all_plots(metrics)
    else:
        print("Required CSV files missing. Please run generate_raw_data.py and data_cleaner.py first.")
