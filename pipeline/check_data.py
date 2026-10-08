# check_data.py - Validate the created dataset

import pandas as pd
import numpy as np

print("Loading dataset...")
df = pd.read_csv('Final_dataset_group_09.csv')

print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

print("\n=== DATA QUALITY CHECK ===")

# Check failure data
print("\n1. Failure Data Analysis:")
failure_data = df[df['has_failure'] == True]
print(f"Records with failures: {len(failure_data):,}")
if len(failure_data) > 0:
    print("Sample failure data:")
    print(failure_data[['supplier_manu', 'km_first_fail', 'component']].head(10))
    print(f"\nFailure km statistics:")
    print(failure_data['km_first_fail'].describe())
else:
    print("No failure records found!")

# Check delivery times
print("\n2. Delivery Time Analysis:")
delivery_data = df[df['delivery_days'].notna()]
print(f"Records with delivery data: {len(delivery_data):,}")
if len(delivery_data) > 0:
    print("Sample delivery data:")
    print(delivery_data[['supplier_manu', 'delivery_days', 'component']].head(10))
    print(f"\nDelivery days statistics:")
    print(delivery_data['delivery_days'].describe())
else:
    print("No delivery records found!")

# Check suppliers
print("\n3. Supplier Analysis:")
print("Suppliers by count:")
print(df['supplier_manu'].value_counts())

# Check components
print("\n4. Component Analysis:")
print("Components by count:")
print(df['component'].value_counts())

# Check dates
print("\n5. Date Analysis:")
print("Date ranges:")
if df['month'].notna().any():
    print(f"Month range: {df['month'].min()} to {df['month'].max()}")
if df['comp_prod_date'].notna().any():
    print(f"Component production: {df['comp_prod_date'].min()} to {df['comp_prod_date'].max()}")
if df['first_reg_date'].notna().any():
    print(f"Registration: {df['first_reg_date'].min()} to {df['first_reg_date'].max()}")

# Check for JIT analysis requirements
print("\n6. JIT Analysis Check (2013-2015, Engine/Circuit):")
jit_eligible = df[
    (pd.to_datetime(df['comp_prod_date']).dt.year.between(2013, 2015)) &
    (df['delivery_days'].notna()) &
    (df['component'].isin(['Engine', 'Circuit']))
]
print(f"JIT eligible records: {len(jit_eligible):,}")
if len(jit_eligible) > 0:
    print("JIT sample:")
    print(jit_eligible[['supplier_manu', 'delivery_days', 'component', 'comp_prod_date']].head())

# Check manufacturer flags
print("\n7. Manufacturer Flag Check:")
print(f"Has manufacturer 202: {df['has_manu_202'].sum():,}")
print(f"Has manufacturer 205: {df['has_manu_205'].sum():,}")

print("\n=== SUMMARY ===")
print("Issues to address:")
issues = []

if len(failure_data) == 0:
    issues.append("- No failure data found")
elif failure_data['km_first_fail'].median() == 0:
    issues.append("- Failure mileage is 0 (data quality issue)")

if len(delivery_data) == 0:
    issues.append("- No delivery time data found")

if len(jit_eligible) == 0:
    issues.append("- No JIT analysis data (2013-2015 engines/circuits)")

if len(issues) == 0:
    print("✓ Data looks ready for dashboard!")
else:
    print("⚠ Issues found:")
    for issue in issues:
        print(issue)