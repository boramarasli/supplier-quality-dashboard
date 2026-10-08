# step1_vehicle_bom.py - Process Vehicle Bill of Materials only

from pathlib import Path
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def read_csv_robust(file_path):
    """Read CSV with quote handling"""
    try:
        df = pd.read_csv(file_path, sep=';', quotechar='"', encoding='utf-8', low_memory=False)
        # Clean quotes from all columns
        df.columns = [str(col).strip().strip('"') for col in df.columns]
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip().str.strip('"')
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Setup
PROJECT_DIR = Path('.').resolve()
DATA_DIR = PROJECT_DIR / 'Data'
OUT_DIR = PROJECT_DIR / 'temp_processing'
OUT_DIR.mkdir(exist_ok=True)

print("Step 1: Processing Vehicle BOM...")

# Load vehicle BOM
veh_bom_path = DATA_DIR / 'Fahrzeug' / 'Bestandteile_Fahrzeuge_OEM1_Typ11.csv'
print(f"Loading: {veh_bom_path.name}")

vb = read_csv_robust(veh_bom_path)
if vb is None:
    raise ValueError("Could not load vehicle BOM")

print(f"Shape: {vb.shape}")
print(f"Columns: {list(vb.columns)}")

# Create vehicle-component mappings
vehicle_id_col = 'ID_Fahrzeug'
component_cols = ['ID_Karosserie', 'ID_Schaltung', 'ID_Sitze', 'ID_Motor']

print("Creating vehicle-component mappings...")
veh_long_data = []

# Process in smaller chunks to avoid memory issues
chunk_size = 50000
total_rows = len(vb)
processed = 0

for start_idx in range(0, total_rows, chunk_size):
    end_idx = min(start_idx + chunk_size, total_rows)
    chunk = vb.iloc[start_idx:end_idx]
    
    for _, row in chunk.iterrows():
        vehicle_id = str(row[vehicle_id_col]).strip()
        if not vehicle_id or vehicle_id.lower() in ['nan', '']:
            continue
        
        for comp_col in component_cols:
            comp_id = str(row[comp_col]).strip()
            if comp_id and comp_id.lower() not in ['nan', '']:
                veh_long_data.append({
                    'vehicle': vehicle_id,
                    'K_id': comp_id
                })
    
    processed += len(chunk)
    print(f"Processed: {processed:,}/{total_rows:,} vehicles")

# Save results
veh_long = pd.DataFrame(veh_long_data).drop_duplicates()
veh_long.to_csv(OUT_DIR / 'vehicle_component_mapping.csv', index=False)

print(f"Vehicle-component mappings created: {len(veh_long):,}")
print(f"Saved to: {OUT_DIR}/vehicle_component_mapping.csv")
print("Step 1 complete!")