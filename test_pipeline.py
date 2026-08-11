#!/usr/bin/env python3
"""
test_pipeline.py
Automated Verification Suite for Data Cleaning & Visualization Project.
Tests data preprocessing integrity, outlier capping limits, deduplication,
and visualization graphic outputs.
"""

import os
import json
import unittest
import pandas as pd
import numpy as np

class TestDataCleaningPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.raw_csv = os.path.join(cls.base_dir, "raw_e_commerce_data.csv")
        cls.clean_csv = os.path.join(cls.base_dir, "cleaned_e_commerce_data.csv")
        cls.metrics_json = os.path.join(cls.base_dir, "cleaning_metrics.json")
        cls.viz_dir = os.path.join(cls.base_dir, "static", "visualizations")

        # Load clean dataset
        if os.path.exists(cls.clean_csv):
            cls.df_clean = pd.read_csv(cls.clean_csv)
        else:
            cls.df_clean = None

    def test_01_files_exist(self):
        """Verify that all pipeline output files exist."""
        self.assertTrue(os.path.exists(self.raw_csv), "raw_e_commerce_data.csv missing!")
        self.assertTrue(os.path.exists(self.clean_csv), "cleaned_e_commerce_data.csv missing!")
        self.assertTrue(os.path.exists(self.metrics_json), "cleaning_metrics.json missing!")

    def test_02_deduplication(self):
        """Verify duplicate transaction IDs were removed."""
        if "transaction_id" in self.df_clean.columns:
            dups = self.df_clean.duplicated(subset=["transaction_id"]).sum()
            self.assertEqual(dups, 0, f"Found {dups} duplicate transaction IDs in cleaned data!")

    def test_03_no_missing_critical_values(self):
        """Verify key columns have no missing values after imputation."""
        critical_cols = ["age", "annual_income", "purchase_amount", "customer_rating", "product_category", "city", "customer_segment"]
        for col in critical_cols:
            if col in self.df_clean.columns:
                null_count = self.df_clean[col].isnull().sum()
                self.assertEqual(null_count, 0, f"Column '{col}' has {null_count} unhandled missing values!")

    def test_04_outlier_capping_boundaries(self):
        """Verify age and customer rating are capped within realistic domain boundaries."""
        if "age" in self.df_clean.columns:
            min_age = self.df_clean["age"].min()
            max_age = self.df_clean["age"].max()
            self.assertGreaterEqual(min_age, 18, f"Age below minimum limit 18: {min_age}")
            self.assertLessEqual(max_age, 85, f"Age above maximum limit 85: {max_age}")

        if "customer_rating" in self.df_clean.columns:
            min_rat = self.df_clean["customer_rating"].min()
            max_rat = self.df_clean["customer_rating"].max()
            self.assertGreaterEqual(min_rat, 1.0, f"Rating below 1.0: {min_rat}")
            self.assertLessEqual(max_rat, 5.0, f"Rating above 5.0: {max_rat}")

    def test_05_feature_engineering(self):
        """Verify engineered features (RFM, demographics) are generated."""
        expected_features = ["age_group", "income_bracket", "year_month", "rfm_segment"]
        for feat in expected_features:
            self.assertIn(feat, self.df_clean.columns, f"Engineered feature '{feat}' is missing!")

    def test_06_visualizations_generated(self):
        """Verify all 7 PNG charts are generated and non-empty."""
        expected_plots = [
            "01_missing_data_analysis.png",
            "02_outlier_detection_boxplots.png",
            "03_customer_demographics.png",
            "04_sales_trends_time_series.png",
            "05_category_performance.png",
            "06_correlation_heatmap.png",
            "07_rfm_customer_segmentation.png"
        ]
        for plot_name in expected_plots:
            plot_path = os.path.join(self.viz_dir, plot_name)
            self.assertTrue(os.path.exists(plot_path), f"Plot graphics missing: {plot_name}")
            self.assertGreater(os.path.getsize(plot_path), 5000, f"Plot graphic {plot_name} is empty/corrupted.")

if __name__ == "__main__":
    unittest.main()
