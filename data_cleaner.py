#!/usr/bin/env python3
"""
data_cleaner.py
Modular Data Preprocessing & Cleaning Engine.
Handles missing values, outliers, duplicate removal, text normalization,
datetime standardization, and feature engineering (RFM, demographics).
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

class DataCleaner:
    def __init__(self, df_raw):
        self.df_raw = df_raw.copy()
        self.df = df_raw.copy()
        self.metrics = {
            "processing_timestamp": datetime.now().isoformat(),
            "raw_total_rows": len(df_raw),
            "raw_total_columns": len(df_raw.columns),
            "duplicates_removed": 0,
            "missing_values_before": {},
            "missing_values_after": {},
            "outliers_handled": {},
            "summary_stats_before": {},
            "summary_stats_after": {}
        }
        
    def clean_column_names(self):
        """Standardize column names to clean snake_case."""
        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("[^a-z0-9_]", "", regex=True)
        )
        return self
        
    def record_initial_stats(self):
        """Record initial missing value counts and numerical stats."""
        # Replace common string placeholders with NaN for accurate counting
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].replace(["N/A", "n/a", "NA", "Unknown", "UNKNOWN", "INVALID_DATE", ""], np.nan)
                
        self.metrics["missing_values_before"] = self.df.isnull().sum().to_dict()
        return self

    def handle_duplicates(self):
        """Identify and remove duplicate rows."""
        initial_len = len(self.df)
        self.df = self.df.drop_duplicates(keep="first").reset_index(drop=True)
        # Also drop duplicates based on transaction_id if present
        if "transaction_id" in self.df.columns:
            self.df = self.df.drop_duplicates(subset=["transaction_id"], keep="first").reset_index(drop=True)
        dropped = initial_len - len(self.df)
        self.metrics["duplicates_removed"] = int(dropped)
        return self

    def clean_currency_and_numeric_strings(self):
        """Parse currency strings like '$1,250.50' into float numbers."""
        for col in ["annual_income", "purchase_amount", "age", "customer_rating"]:
            if col in self.df.columns:
                # Store pre-clean stats for numerical columns
                s_raw = pd.to_numeric(
                    self.df[col].astype(str).str.replace(r"[^\d.-]", "", regex=True),
                    errors='coerce'
                )
                if not s_raw.dropna().empty:
                    self.metrics["summary_stats_before"][col] = {
                        "mean": float(round(s_raw.mean(), 2)),
                        "median": float(round(s_raw.median(), 2)),
                        "min": float(round(s_raw.min(), 2)),
                        "max": float(round(s_raw.max(), 2)),
                        "std": float(round(s_raw.std(), 2))
                    }
                
                # Perform cleaning
                self.df[col] = self.df[col].astype(str).str.replace(r"[^\d.-]", "", regex=True)
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        return self

    def clean_text_columns(self):
        """Normalize text columns (whitespace, casing, standard placeholders)."""
        text_cols = ["customer_name", "product_category", "city", "customer_segment"]
        for col in text_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
                self.df[col] = self.df[col].replace(["nan", "None", "N/A", "n/a", "Unknown", "UNKNOWN", ""], np.nan)
                
        # Specific categorical fixes
        if "product_category" in self.df.columns:
            # Standardize category casing
            cat_map = {
                "electronics": "Electronics",
                "clothing": "Clothing",
                "home & kitchen": "Home & Kitchen",
                "home and kitchen": "Home & Kitchen",
                "beauty": "Beauty",
                "sports & outdoors": "Sports & Outdoors"
            }
            self.df["product_category"] = self.df["product_category"].str.lower().map(cat_map).fillna(self.df["product_category"].str.title())
            
        if "customer_name" in self.df.columns:
            self.df["customer_name"] = self.df["customer_name"].str.title()
            
        if "city" in self.df.columns:
            self.df["city"] = self.df["city"].str.title()
            
        return self

    def parse_datetime_columns(self):
        """Standardize date strings to ISO YYYY-MM-DD datetime objects."""
        if "transaction_date" in self.df.columns:
            self.df["transaction_date"] = pd.to_datetime(self.df["transaction_date"], errors='coerce', format='mixed')
            # Impute missing/invalid dates with median transaction date
            median_date = self.df["transaction_date"].dropna().median()
            self.df["transaction_date"] = self.df["transaction_date"].fillna(median_date)
        return self

    def handle_outliers(self):
        """Detect and cap outliers using IQR and domain rules."""
        outlier_counts = {}
        
        # 1. Age capping (Domain bounds [18, 85])
        if "age" in self.df.columns:
            invalid_age_mask = (self.df["age"] < 18) | (self.df["age"] > 85)
            outlier_counts["age"] = int(invalid_age_mask.sum())
            median_age = self.df.loc[~invalid_age_mask, "age"].median()
            self.df["age"] = np.where(invalid_age_mask, median_age, self.df["age"])
            self.df["age"] = self.df["age"].round()
            
        # 2. Customer Rating capping (Domain bounds [1.0, 5.0])
        if "customer_rating" in self.df.columns:
            invalid_rat_mask = (self.df["customer_rating"] < 1.0) | (self.df["customer_rating"] > 5.0)
            outlier_counts["customer_rating"] = int(invalid_rat_mask.sum())
            self.df["customer_rating"] = np.clip(self.df["customer_rating"], 1.0, 5.0)

        # 3. Annual Income capping (IQR method & upper percentile limit)
        if "annual_income" in self.df.columns:
            # Negative income handling
            self.df.loc[self.df["annual_income"] < 0, "annual_income"] = np.nan
            
            # IQR capping
            q1 = self.df["annual_income"].quantile(0.25)
            q3 = self.df["annual_income"].quantile(0.75)
            iqr = q3 - q1
            lower_bound = max(15000, q1 - 1.5 * iqr)
            upper_bound = q3 + 3.0 * iqr  # Cap extreme outliers like $2.5M
            
            income_outliers = (self.df["annual_income"] < lower_bound) | (self.df["annual_income"] > upper_bound)
            outlier_counts["annual_income"] = int(income_outliers.sum())
            self.df["annual_income"] = np.clip(self.df["annual_income"], lower_bound, upper_bound)

        # 4. Purchase Amount capping (IQR method)
        if "purchase_amount" in self.df.columns:
            # Negative price handling
            self.df.loc[self.df["purchase_amount"] < 0, "purchase_amount"] = np.nan
            
            q1 = self.df["purchase_amount"].quantile(0.25)
            q3 = self.df["purchase_amount"].quantile(0.75)
            iqr = q3 - q1
            upper_bound = q3 + 3.0 * iqr # Cap $999,999 outliers
            
            amount_outliers = (self.df["purchase_amount"] > upper_bound) | (self.df["purchase_amount"] < 5.0)
            outlier_counts["purchase_amount"] = int(amount_outliers.sum())
            self.df["purchase_amount"] = np.clip(self.df["purchase_amount"], 5.0, upper_bound)

        self.metrics["outliers_handled"] = outlier_counts
        return self

    def handle_missing_values(self):
        """Impute missing values using statistically sound group medians/modes."""
        # Numerical Imputations
        if "age" in self.df.columns:
            self.df["age"] = self.df["age"].fillna(self.df["age"].median())
            
        if "annual_income" in self.df.columns:
            # Impute income by customer segment median if available, else global median
            if "customer_segment" in self.df.columns:
                self.df["annual_income"] = self.df.groupby("customer_segment")["annual_income"].transform(lambda x: x.fillna(x.median()))
            self.df["annual_income"] = self.df["annual_income"].fillna(self.df["annual_income"].median())

        if "purchase_amount" in self.df.columns:
            # Impute purchase amount by category median
            if "product_category" in self.df.columns:
                self.df["purchase_amount"] = self.df.groupby("product_category")["purchase_amount"].transform(lambda x: x.fillna(x.median()))
            self.df["purchase_amount"] = self.df["purchase_amount"].fillna(self.df["purchase_amount"].median())

        if "customer_rating" in self.df.columns:
            self.df["customer_rating"] = self.df["customer_rating"].fillna(self.df["customer_rating"].median())

        # Categorical Imputations
        if "customer_name" in self.df.columns:
            self.df["customer_name"] = self.df["customer_name"].fillna("Valued Customer")

        if "product_category" in self.df.columns:
            mode_cat = self.df["product_category"].mode()[0] if not self.df["product_category"].mode().empty else "Electronics"
            self.df["product_category"] = self.df["product_category"].fillna(mode_cat)

        if "city" in self.df.columns:
            self.df["city"] = self.df["city"].fillna("Unspecified")

        if "customer_segment" in self.df.columns:
            self.df["customer_segment"] = self.df["customer_segment"].fillna("Standard")

        self.metrics["missing_values_after"] = self.df.isnull().sum().to_dict()
        return self

    def engineer_features(self):
        """Derive new demographic, temporal, and RFM analytical features."""
        # 1. Demographics
        if "age" in self.df.columns:
            bins = [0, 25, 35, 50, 65, 120]
            labels = ["18-25", "26-35", "36-50", "51-65", "65+"]
            self.df["age_group"] = pd.cut(self.df["age"], bins=bins, labels=labels, right=True)

        if "annual_income" in self.df.columns:
            inc_bins = [0, 45000, 85000, 130000, 5000000]
            inc_labels = ["Low (<$45k)", "Medium ($45k-$85k)", "High ($85k-$130k)", "Very High (>$130k)"]
            self.df["income_bracket"] = pd.cut(self.df["annual_income"], bins=inc_bins, labels=inc_labels)

        # 2. Temporal Features
        if "transaction_date" in self.df.columns:
            self.df["transaction_year"] = self.df["transaction_date"].dt.year
            self.df["transaction_month"] = self.df["transaction_date"].dt.month
            self.df["transaction_month_name"] = self.df["transaction_date"].dt.strftime("%b")
            self.df["transaction_day_name"] = self.df["transaction_date"].dt.strftime("%a")
            self.df["year_month"] = self.df["transaction_date"].dt.strftime("%Y-%m")

        # 3. RFM (Recency, Frequency, Monetary) Customer Segmentation
        if all(col in self.df.columns for col in ["customer_id", "transaction_date", "purchase_amount"]):
            max_date = self.df["transaction_date"].max()
            rfm = self.df.groupby("customer_id").agg({
                "transaction_date": lambda x: (max_date - x.max()).days,
                "customer_id": "count",
                "purchase_amount": "sum"
            }).rename(columns={
                "transaction_date": "recency_days",
                "customer_id": "frequency_orders",
                "purchase_amount": "monetary_total"
            }).reset_index()

            # RFM Scoring (1 to 4)
            rfm["r_score"] = pd.qcut(rfm["recency_days"].rank(method='first'), q=4, labels=[4, 3, 2, 1])
            rfm["f_score"] = pd.qcut(rfm["frequency_orders"].rank(method='first'), q=4, labels=[1, 2, 3, 4])
            rfm["m_score"] = pd.qcut(rfm["monetary_total"].rank(method='first'), q=4, labels=[1, 2, 3, 4])
            
            rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)
            
            def assign_rfm_segment(row):
                r, f, m = int(row["r_score"]), int(row["f_score"]), int(row["m_score"])
                if r >= 3 and f >= 3 and m >= 3:
                    return "Champions"
                elif r >= 3 and f >= 2:
                    return "Loyal Customers"
                elif r >= 3 and f == 1:
                    return "Recent Customers"
                elif r <= 2 and f >= 3:
                    return "At Risk"
                else:
                    return "Needs Attention"

            rfm["rfm_segment"] = rfm.apply(assign_rfm_segment, axis=1)

            # Merge back into main dataframe
            self.df = self.df.merge(
                rfm[["customer_id", "recency_days", "frequency_orders", "monetary_total", "rfm_segment"]],
                on="customer_id",
                how="left"
            )

        return self

    def record_final_stats(self):
        """Record final summary metrics."""
        self.metrics["cleaned_total_rows"] = len(self.df)
        self.metrics["cleaned_total_columns"] = len(self.df.columns)
        
        for col in ["annual_income", "purchase_amount", "age", "customer_rating"]:
            if col in self.df.columns:
                self.metrics["summary_stats_after"][col] = {
                    "mean": float(round(self.df[col].mean(), 2)),
                    "median": float(round(self.df[col].median(), 2)),
                    "min": float(round(self.df[col].min(), 2)),
                    "max": float(round(self.df[col].max(), 2)),
                    "std": float(round(self.df[col].std(), 2))
                }
        return self

    def run_pipeline(self):
        """Execute the full data cleaning pipeline sequentially."""
        print("Starting Data Cleaning Pipeline...")
        (
            self.clean_column_names()
            .record_initial_stats()
            .handle_duplicates()
            .clean_currency_and_numeric_strings()
            .clean_text_columns()
            .parse_datetime_columns()
            .handle_outliers()
            .handle_missing_values()
            .engineer_features()
            .record_final_stats()
        )
        print("Data Cleaning Pipeline completed successfully!")
        return self.df, self.metrics

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_dir, "raw_e_commerce_data.csv")
    cleaned_path = os.path.join(base_dir, "cleaned_e_commerce_data.csv")
    metrics_path = os.path.join(base_dir, "cleaning_metrics.json")
    
    if os.path.exists(raw_path):
        df_raw = pd.read_csv(raw_path)
        cleaner = DataCleaner(df_raw)
        df_clean, metrics = cleaner.run_pipeline()
        
        # Format transaction_date for CSV export
        if "transaction_date" in df_clean.columns:
            df_clean["transaction_date"] = df_clean["transaction_date"].dt.strftime("%Y-%m-%d")
            
        df_clean.to_csv(cleaned_path, index=False)
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
            
        print(f"Saved cleaned dataset ({len(df_clean)} rows) to: {cleaned_path}")
        print(f"Saved metrics summary to: {metrics_path}")
    else:
        print(f"Error: {raw_path} not found. Please run generate_raw_data.py first.")
