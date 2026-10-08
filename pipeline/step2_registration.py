# step2_registration.py - Process registration data

from pathlib import Path
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def read_csv_robust(file_path):
    """Read CSV with quote handling"""
    try:
        df = pd.read_csv(file_path, sep=';', quotechar='"', encoding='utf-8', low_memory=False)
        df.columns = [str(col).strip().strip('"') for col in df.columns]
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip().str.strip('"')
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

# Setup
PROJECT_DIR = Path('.').resolve()
DATA_DIR = PROJECT_DIR / 'Data'
OUT_DIR = PROJECT_DIR / 'temp_processing'

print("Step 2: Processing Registration Data...")

# Load registration data
zul_path = DATA_DIR / 'Zulassungen' / 'Zulassungen_alle_Fahrzeuge.csv'
print(f"Loading: {zul_path.name}")

zul_df = read_csv_robust(zul_path)
if zul_df is None:
    print("Could not load registration data")
    exit()

print(f"Shape: {zul_df.shape}")
print(f"Columns: {list(zul_df.columns)}")

# Find vehicle and date columns
cols = list(zul_df.columns)
vehicle_col = cols[0]  # Usually first column
date_col = cols[1] if len(cols) > 1 else None  # Usually second column

print(f"Using vehicle column: {vehicle_col}")
print(f"Using date column: {date_col}")

# Clean and process
zul_clean = zul_df[[vehicle_col, date_col]].copy()
zul_clean.columns = ['vehicle', 'reg_date']
zul_clean['vehicle'] = zul_clean['vehicle'].astype(str).str.strip()
zul_clean['reg_date'] = pd.to_datetime(zul_clean['reg_date'], errors='coerce')

print("Processing registrations...")

# Get earliest registration per vehicle (process in chunks)
chunk_size = 100000
results = []
total_rows = len(zul_clean)

for start_idx in range(0, total_rows, chunk_size):
    end_idx = min(start_idx + chunk_size, total_rows)
    chunk = zul_clean.iloc[start_idx:end_idx]
    
    chunk_result = (chunk.dropna(subset=['reg_date'])
                   .sort_values(['vehicle', 'reg_date'])
                   .groupby('vehicle', as_index=False)
                   .first())
    
    results.append(chunk_result)
    print(f"Processed: {end_idx:,}/{total_rows:,} registrations")

# Combine results
first_reg = pd.concat(results, ignore_index=True)
first_reg = first_reg.groupby('vehicle', as_index=False).first()  # Final deduplication

# Save
first_reg.to_csv(OUT_DIR / 'vehicle_registration.csv', index=False)

print(f"Registration records: {len(first_reg):,}")
print(f"Date range: {first_reg['reg_date'].min()} to {first_reg['reg_date'].max()}")
print(f"Saved to: {OUT_DIR}/vehicle_registration.csv")
print("Step 2 complete!")