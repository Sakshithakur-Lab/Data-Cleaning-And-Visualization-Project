#!/usr/bin/env python3
"""
main.py
Data Cleaning & Visualization Orchestrator Script.
Executes dataset synthesis, preprocessing pipeline, static visualization generation,
JSON payload generation, and serves the interactive Web Dashboard.
"""

import os
import sys
import json
import http.server
import socketserver
import pandas as pd

def run_pipeline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 70)
    print("      DATA CLEANING & VISUALIZATION PIPELINE ORCHESTRATOR      ")
    print("=" * 70)
    
    # Step 1: Dataset Synthesis
    print("\n[Step 1/4] Generating raw messy dataset...")
    import generate_raw_data
    df_raw = generate_raw_data.generate_messy_dataset(num_records=1500)
    raw_csv_path = os.path.join(base_dir, "raw_e_commerce_data.csv")
    df_raw.to_csv(raw_csv_path, index=False)
    print(f"-> Generated {len(df_raw)} raw records at: {raw_csv_path}")

    # Step 2: Data Cleaning & Preprocessing
    print("\n[Step 2/4] Executing Data Preprocessing & Cleaning Engine...")
    import data_cleaner
    cleaner = data_cleaner.DataCleaner(df_raw)
    df_clean, metrics = cleaner.run_pipeline()
    
    # Save CSV & Metrics JSON
    cleaned_csv_path = os.path.join(base_dir, "cleaned_e_commerce_data.csv")
    metrics_json_path = os.path.join(base_dir, "cleaning_metrics.json")
    
    df_clean_export = df_clean.copy()
    if "transaction_date" in df_clean_export.columns:
        df_clean_export["transaction_date"] = df_clean_export["transaction_date"].dt.strftime("%Y-%m-%d")
        
    df_clean_export.to_csv(cleaned_csv_path, index=False)
    with open(metrics_json_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"-> Cleaned dataset ({len(df_clean)} records) saved to: {cleaned_csv_path}")

    # Step 3: Statistical Visualizations
    print("\n[Step 3/4] Generating Seaborn & Matplotlib Report Graphics...")
    import data_visualizer
    out_viz_dir = os.path.join(base_dir, "static", "visualizations")
    viz = data_visualizer.DataVisualizer(df_raw, df_clean_export, out_viz_dir)
    viz.generate_all_plots(metrics)

    # Step 4: JSON Payloads for Frontend Dashboard
    print("\n[Step 4/4] Creating Web Dashboard JSON Data Payloads...")
    raw_json_path = os.path.join(base_dir, "raw_data.json")
    clean_json_path = os.path.join(base_dir, "cleaned_data.json")
    
    # Fill NaN values for clean JSON output
    df_raw_filled = df_raw.fillna("N/A")
    
    # Cast categorical columns to string to prevent TypeError during fillna
    df_clean_export_str = df_clean_export.copy()
    for cat_col in df_clean_export_str.select_dtypes(include=['category']).columns:
        df_clean_export_str[cat_col] = df_clean_export_str[cat_col].astype(str)
        
    df_clean_filled = df_clean_export_str.fillna("N/A")
    
    df_raw_filled.to_json(raw_json_path, orient="records", indent=2)
    df_clean_filled.to_json(clean_json_path, orient="records", indent=2)
    print(f"-> Exported {raw_json_path} & {clean_json_path}")

    print("\n" + "=" * 70)
    print(" PIPELINE COMPLETED SUCCESSFULLY! ")
    print("=" * 70)
    return base_dir

def start_server(base_dir, port=8080):
    os.chdir(base_dir)
    socketserver.TCPServer.allow_reuse_address = True
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"\n🚀 Launching Interactive Dashboard Server...")
    print(f"👉 Access Dashboard URL: http://localhost:{port}/dashboard/index.html")
    
    try:
        with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    base_dir = run_pipeline()
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        start_server(base_dir, port=8080)
