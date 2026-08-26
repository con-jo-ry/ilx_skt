import csv
from pathlib import Path

def validate_corpus():
    # 1. Setup paths relative to this script's location
    # Assumes script is in `project_main/scripts/`
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    corpus_dir = project_root / 'corpus'
    
    datasets = ['gretil_sa', 'gretil_not_in_repo', 'dsbc']
    
    for dataset in datasets:
        print(f"=== Validating {dataset} ===")
        csv_path = project_root / f"{dataset}.csv"
        target_dir = corpus_dir / dataset
        
        # Check if expected files/folders exist
        if not csv_path.exists():
            print(f"[!] Error: CSV file not found at {csv_path}\n")
            continue
        if not target_dir.exists():
            print(f"[!] Error: Corpus folder not found at {target_dir}\n")
            continue
            
        csv_filenames = set()
        duplicates_to_check = set()
        
        # Read the CSV
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            
            try:
                header1 = next(reader)
                header2 = next(reader)
            except StopIteration:
                print("[!] Error: CSV file has less than 2 rows.\n")
                continue
                
            # Find the indices of our target columns in the first two rows
            xml_idx, dup_idx = -1, -1
            for header_row in [header1, header2]:
                for i, col_name in enumerate(header_row):
                    clean_name = col_name.strip()
                    if clean_name == 'xml_filename':
                        xml_idx = i
                    elif clean_name == 'duplicate_of_standard':
                        dup_idx = i
                        
            if xml_idx == -1:
                print("[!] Error: Could not find 'xml_filename' in the first two rows.\n")
                continue
                
            # Parse the rest of the CSV
            for row_num, row in enumerate(reader, start=3):
                # Skip entirely blank rows
                if not row or not any(row):
                    continue
                    
                # Extract xml_filename
                if xml_idx < len(row):
                    xml_val = row[xml_idx].strip()
                    if xml_val:
                        csv_filenames.add(xml_val)
                
                # Extract duplicate_of_standard (if the column exists)
                if dup_idx != -1 and dup_idx < len(row):
                    dup_val = row[dup_idx].strip()
                    if dup_val:
                        duplicates_to_check.add((row_num, dup_val))

        # Get actual files in the corpus subdirectory
        actual_files = {p.name for p in target_dir.iterdir() if p.is_file()}
        
        # (1) Check: Files in the folder that are missing from the CSV
        missing_in_csv = actual_files - csv_filenames
        if missing_in_csv:
            print(f"  [1] FAIL: Files in '{dataset}' folder missing from CSV:")
            for f_name in sorted(missing_in_csv):
                print(f"      - {f_name}")
        else:
            print(f"  [1] PASS: All files in '{dataset}' folder are recorded in the CSV.")

        # (2) Check: Files in the CSV that are missing from the folder
        missing_in_folder = csv_filenames - actual_files
        if missing_in_folder:
            print(f"  [2] FAIL: 'xml_filename' records in CSV missing from folder:")
            for f_name in sorted(missing_in_folder):
                print(f"      - {f_name}")
        else:
            print(f"  [2] PASS: All 'xml_filename' records in CSV exist in the folder.")
            
        # (3) Check: Validate 'duplicate_of_standard' paths
        if not duplicates_to_check:
            print(f"  [3] SKIP: No 'duplicate_of_standard' entries found.")
        else:
            missing_duplicates = []
            for row_num, dup_path in duplicates_to_check:
                # Strip leading slashes to prevent root-directory resolution issues
                safe_dup_path = dup_path.lstrip('/') 
                full_dup_path = corpus_dir / safe_dup_path
                
                if not full_dup_path.is_file():
                    missing_duplicates.append((row_num, dup_path))
                    
            if missing_duplicates:
                print(f"  [3] FAIL: Missing 'duplicate_of_standard' files:")
                for row_num, missing_path in sorted(missing_duplicates):
                    print(f"      - Row {row_num}: {missing_path}")
            else:
                print(f"  [3] PASS: All 'duplicate_of_standard' paths point to existing files.")
                
        print("\n")

if __name__ == '__main__':
    validate_corpus()
