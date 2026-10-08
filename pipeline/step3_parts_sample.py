# step3_parts_sample.py - Process just 5 parts files as a test

from pathlib import Path
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def read_mixed_file(file_path):
    """Read CSV or TXT files"""
    try:
        df = pd.read_csv(file_path, sep=';', quotechar='"', encoding='utf-8', 
                        low_memory=False, on_bad_lines='skip')
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

print("Step 3: Processing Sample Parts Data (5 files only)...")

einzelteil_dir = DATA_DIR / 'Einzelteil'
files = list(einzelteil_dir.glob('*.csv'))[:5]  # Just first 5 CSV files

parts_data = []

for file_path in files:
    print(f"Processing: {file_path.name}")
    
    df = read_mixed_file(file_path)
    if df is None:
        continue
    
    cols = list(df.columns)
    print(f"  Columns: {cols}")
    
    # Find key columns
    id_col = cols[0]  # Usually first column
    prod_date_col = cols[1] if len(cols) > 1 else None  # Usually second
    
    # Look for specific patterns
    for col in cols:
        col_lower = col.lower()
        if 'idnummer' in col_lower or col.startswith('ID_T'):
            id_col = col
        elif 'produktionsdatum' in col_lower:
            prod_date_col = col
    
    print(f"  Using ID: {id_col}, Date: {prod_date_col}")
    
    # Create basic part dataframe
    part_df = pd.DataFrame()
    part_df['T_id'] = df[id_col].astype(str).str.strip()
    part_df['T_prod_date'] = pd.to_datetime(df[prod_date_col], errors='coerce') if prod_date_col else pd.NaT
    
    # Add failure info if available
    fail_cols = [c for c in cols if 'fehlerhaft' in c.lower()]
    if fail_cols:
        part_df['T_fail'] = pd.to_numeric(df[fail_cols[0]], errors='coerce').fillna(0)
    else:
        part_df['T_fail'] = 0
    
    # Clean invalid records
    part_df = part_df[
        (part_df['T_id'] != '') & 
        (part_df['T_id'] != 'nan') & 
        (part_df['T_id'].notna())
    ]
    
    if not part_df.empty:
        parts_data.append(part_df)
        print(f"  Loaded: {len(part_df):,} records")

# Combine and save
if parts_data:
    T_catalog = pd.concat(parts_data, ignore_index=True)
    T_catalog = T_catalog.drop_duplicates(subset=['T_id'], keep='first')
    T_catalog.to_csv(OUT_DIR / 'parts_sample.csv', index=False)
    
    print(f"Combined parts data: {len(T_catalog):,}")
    print(f"Saved to: {OUT_DIR}/parts_sample.csv")
else:
    print("No parts data loaded")

print("Step 3 complete!")