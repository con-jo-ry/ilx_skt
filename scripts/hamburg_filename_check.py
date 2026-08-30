import csv
import sys
from pathlib import Path

def validate_corpus():
    # 1. Dynamically resolve paths relative to this script's location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    csv_path = project_root / 'hamburg.csv'
    corpus_dir = project_root / 'corpus' / 'hamburg'
    
    # Pre-flight checks
    if not csv_path.exists():
        print(f"Error: Could not find CSV at {csv_path}")
        sys.exit(1)
    if not corpus_dir.is_dir():
        print(f"Error: Could not find corpus directory at {corpus_dir}")
        sys.exit(1)

    # 2 & 3. Parse the CSV and extract filenames from Column 1 (index 0)
    csv_filenames = set()
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip the header (Row 1)
        
        for row_num, row in enumerate(reader, start=2):
            if row:  # Ignore completely empty rows
                filename = row[0].strip()
                if filename:
                    csv_filenames.add(filename)

    # 4. Extract all filenames from the corpus directory
    dir_filenames = set(
        file.name for file in corpus_dir.iterdir() if file.is_file()
    )

    # Calculate mismatches using set difference operations
    missing_in_dir = csv_filenames - dir_filenames
    missing_in_csv = dir_filenames - csv_filenames

    # Output the reconciliation report
    print(f"--- Metadata vs. Corpus Report ---")
    print(f"Total files listed in CSV: {len(csv_filenames)}")
    print(f"Total files found in Dir:  {len(dir_filenames)}")
    print("-" * 34)

    if not missing_in_dir and not missing_in_csv:
        print("✅ Perfect match! All CSV entries exist in the directory, and vice versa.")
    else:
        if missing_in_dir:
            print(f"❌ {len(missing_in_dir)} files in CSV are missing from the directory:")
            for f in sorted(missing_in_dir):
                print(f"   - {f}")
        
        if missing_in_csv:
            print(f"\n❌ {len(missing_in_csv)} files in directory are missing from the CSV:")
            for f in sorted(missing_in_csv):
                print(f"   - {f}")

if __name__ == "__main__":
    validate_corpus()
