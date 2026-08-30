import os
import csv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

CSV_FILE = os.path.join(BASE_DIR, 'wikisource.csv')
CORPUS_DIR = os.path.join(BASE_DIR, 'corpus', 'wikisource')

def main():
    if not os.path.exists(CSV_FILE):
        print(f"CRITICAL ERROR: Could not find CSV at {CSV_FILE}")
        return
    if not os.path.exists(CORPUS_DIR):
        print(f"CRITICAL ERROR: Could not find directory at {CORPUS_DIR}")
        return

    expected_files = set()
    
    # 1. Parse the CSV to build a set of expected relative paths
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sub_folder = row.get('sub_folder', '').strip()
            filename = row.get('xml_filename', '').strip()
            
            if not filename:
                continue
                
            if sub_folder:
                rel_path = os.path.join(sub_folder, filename)
            else:
                rel_path = filename
                
            # Normalize path slashes to ensure safe OS comparison
            expected_files.add(os.path.normpath(rel_path))
            
    # 2. Scan the directory to build a set of actual relative paths
    actual_files = set()
    for root, dirs, files in os.walk(CORPUS_DIR):
        for file in files:
            # Skip hidden files like .DS_Store
            if file.startswith('.'):
                continue 
            
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, CORPUS_DIR)
            
            actual_files.add(os.path.normpath(rel_path))
            
    # 3. Compute differences
    missing_in_dir = expected_files - actual_files
    missing_in_csv = actual_files - expected_files
    
    # 4. Report
    print(f"Total files listed in CSV: {len(expected_files)}")
    print(f"Total actual files found in directory: {len(actual_files)}")
    
    print("\n" + "="*50)
    print(" FILES IN CSV BUT MISSING FROM DIRECTORY ")
    print("="*50)
    if missing_in_dir:
        for f in sorted(missing_in_dir):
            print(f" [MISSING] -> {f}")
    else:
        print(" (None. All files listed in the CSV are safely in your folders.)")
        
    print("\n" + "="*50)
    print(" FILES IN DIRECTORY BUT NOT ACCOUNTED FOR IN CSV ")
    print("="*50)
    if missing_in_csv:
        for f in sorted(missing_in_csv):
            print(f" [UNACCOUNTED] -> {f}")
    else:
        print(" (None. All files in your folders have an entry in the CSV.)")

if __name__ == "__main__":
    main()
