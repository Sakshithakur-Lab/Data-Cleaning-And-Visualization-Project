#!/usr/bin/env python3
"""
generate_raw_data.py
Generates a realistic messy raw e-commerce customer transaction dataset
with missing values, outliers, duplicate records, formatting inconsistencies,
and invalid entries for data cleaning and preprocessing demonstrations.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_messy_dataset(num_records=1500, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "N/A", "Unknown", None]
    categories = ["Electronics", "Clothing", "Home & Kitchen", "Beauty", "Sports & Outdoors", " electronics ", "CLOTHING", "Home & Kitchen", "beauty", "Electronics"]
    segments = ["Basic", "Standard", "Premium", "VIP", None, "N/A"]
    
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]
    
    start_date = datetime(2023, 1, 1)
    
    data = []
    
    for i in range(1, num_records + 1):
        txn_id = f"TXN-{1000 + i}"
        cust_id = f"CUST-{random.randint(100, 400)}"
        
        # Customer Name (inconsistent casing and whitespace)
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        name_style = random.random()
        if name_style < 0.1:
            name = None  # Missing name
        elif name_style < 0.2:
            name = f"  {fn.lower()} {ln.upper()}  " # Whitespace & casing
        elif name_style < 0.3:
            name = f"{fn.upper()} {ln.lower()}"
        else:
            name = f"{fn} {ln}"
            
        # Age (18-75, plus missing and extreme outliers)
        age_rnd = random.random()
        if age_rnd < 0.08:
            age = None
        elif age_rnd < 0.10:
            age = "N/A"
        elif age_rnd < 0.12:
            age = random.choice([145, 172, -5, -12, 210]) # Outlier
        else:
            age = int(np.random.normal(38, 12))
            age = max(18, min(80, age))
            
        # Annual Income (30k - 180k, missing, dirty currency strings, extreme outliers)
        inc_rnd = random.random()
        if inc_rnd < 0.08:
            income = None
        elif inc_rnd < 0.12:
            income = "N/A"
        elif inc_rnd < 0.15:
            # Dirty string formatting
            val = round(np.random.normal(65000, 20000), 2)
            income = f" ${val:,.2f} "
        elif inc_rnd < 0.17:
            # Outliers
            income = random.choice([2500000.0, -45000.0, 1850000.0])
        else:
            income = round(float(np.random.normal(68000, 22000)), 2)
            income = max(18000.0, income)
            
        # Product Category
        cat_rnd = random.random()
        if cat_rnd < 0.06:
            category = None
        elif cat_rnd < 0.10:
            category = "N/A"
        else:
            category = random.choice(categories)
            
        # Purchase Amount ($15 - $2,500, dirty currency, missing, outliers)
        amt_rnd = random.random()
        if amt_rnd < 0.06:
            amount = None
        elif amt_rnd < 0.10:
            amount = "N/A"
        elif amt_rnd < 0.14:
            val = round(float(np.random.exponential(120) + 20), 2)
            amount = f"${val:,.2f}"
        elif amt_rnd < 0.17:
            amount = random.choice([999999.00, 450000.50, -120.00, -85.50]) # Outlier
        else:
            amount = round(float(np.random.exponential(150) + 15), 2)
            
        # Transaction Date (Inconsistent date formats, missing, invalid)
        date_rnd = random.random()
        random_days = random.randint(0, 500)
        dt = start_date + timedelta(days=random_days)
        if date_rnd < 0.05:
            tx_date = None
        elif date_rnd < 0.08:
            tx_date = "INVALID_DATE"
        elif date_rnd < 0.30:
            tx_date = dt.strftime("%Y-%m-%d")
        elif date_rnd < 0.50:
            tx_date = dt.strftime("%m/%d/%Y")
        elif date_rnd < 0.70:
            tx_date = dt.strftime("%d-%b-%Y")
        else:
            tx_date = dt.strftime("%B %d, %Y")
            
        # Rating (1.0 - 5.0, missing, outliers like 10.0 or -2.0)
        rat_rnd = random.random()
        if rat_rnd < 0.10:
            rating = None
        elif rat_rnd < 0.13:
            rating = random.choice([10.0, -1.0, 99.0])
        else:
            rating = round(float(np.clip(np.random.normal(4.1, 0.9), 1.0, 5.0)), 1)
            
        city = random.choice(cities)
        segment = random.choice(segments)
        
        data.append({
            "Transaction_ID": txn_id,
            "Customer_ID": cust_id,
            "Customer_Name": name,
            "Age": age,
            "Annual_Income": income,
            "Product_Category": category,
            "Purchase_Amount": amount,
            "Transaction_Date": tx_date,
            "Customer_Rating": rating,
            "City": city,
            "Customer_Segment": segment
        })
        
    df = pd.DataFrame(data)
    
    # Inject exact duplicate rows (~40 rows)
    dup_indices = random.sample(range(len(df)), 40)
    duplicates = df.iloc[dup_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Shuffle dataframe
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, "raw_e_commerce_data.csv")
    print(f"Generating raw messy dataset at: {output_file}")
    df_raw = generate_messy_dataset(num_records=1500)
    df_raw.to_csv(output_file, index=False)
    print(f"Successfully generated {len(df_raw)} raw records in '{output_file}'.")
