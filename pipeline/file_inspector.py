# simple_file_inspector.py - Fixed version

from pathlib import Path

PROJECT_DIR = Path('.').resolve()
DATA_DIR = PROJECT_DIR / 'Data'

# Target the problematic file
problem_file = DATA_DIR / 'Fahrzeug' / 'Bestandteile_Fahrzeuge_OEM1_Typ11.csv'

print(f"Inspecting: {problem_file}")
print(f"File exists: {problem_file.exists()}")

if problem_file.exists():
    print(f"File size: {problem_file.stat().st_size} bytes")
else:
    print("File size: N/A (file doesn't exist)")

if problem_file.exists():
    # Read first few lines as raw text
    try:
        with open(problem_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
        print(f"\n=== First 10 lines (UTF-8) ===")
        for i, line in enumerate(lines):
            print(f"Line {i}: {repr(line)}")
    except:
        print("UTF-8 failed, trying latin-1...")
        try:
            with open(problem_file, 'r', encoding='latin-1') as f:
                lines = f.readlines()[:10]
            print(f"\n=== First 10 lines (Latin-1) ===")
            for i, line in enumerate(lines):
                print(f"Line {i}: {repr(line)}")
        except Exception as e:
            print(f"Both encodings failed: {e}")
    
    # Check for common issues
    try:
        with open(problem_file, 'rb') as f:
            raw_bytes = f.read(1000)
        
        print(f"\n=== File Analysis ===")
        print(f"Contains semicolons: {';' in raw_bytes.decode('utf-8', errors='ignore')}")
        print(f"Contains commas: {',' in raw_bytes.decode('utf-8', errors='ignore')}")
        text = raw_bytes.decode('utf-8', errors='ignore')
        print(f"Contains tabs: {chr(9) in text}")
        print(f"Contains double quotes: {chr(34) in text}")
        print(f"Contains single quotes: {chr(39) in raw_bytes.decode('utf-8', errors='ignore')}")
        print(f"Contains null bytes: {0 in raw_bytes}")
        
        # Look for BOM
        if raw_bytes.startswith(b'\xef\xbb\xbf'):
            print("Has UTF-8 BOM")
        elif raw_bytes.startswith(b'\xff\xfe'):
            print("Has UTF-16 LE BOM")
        elif raw_bytes.startswith(b'\xfe\xff'):
            print("Has UTF-16 BE BOM")
            
    except Exception as e:
        print(f"Byte analysis failed: {e}")

# Check what files are actually available
print(f"\n=== Available Vehicle Files ===")
vehicle_dir = DATA_DIR / 'Fahrzeug'
if vehicle_dir.exists():
    for file in vehicle_dir.iterdir():
        if file.is_file():
            print(f"  {file.name} ({file.stat().st_size} bytes)")
else:
    print("Vehicle directory not found!")

print(f"\n=== All Data Directories ===")
if DATA_DIR.exists():
    for item in DATA_DIR.iterdir():
        if item.is_dir():
            file_count = len(list(item.glob('*')))
            print(f"  {item.name}/ ({file_count} files)")
else:
    print("Data directory not found!")