import csv
import sys
from pathlib import Path

def main():
    # 1. Configure Paths
    # Since the script runs from ./scripts, we point to the parent directory (..)
    # to access the root where wikisource.csv and corpus/ live.
    csv_path = Path("../wikisource.csv")
    corpus_dir = Path("../corpus/wikisource")
    
    # Fallback: just in case the script is executed from the project root instead
    if not csv_path.exists() and Path("./wikisource.csv").exists():
        csv_path = Path("./wikisource.csv")
        corpus_dir = Path("./corpus/wikisource")

    if not csv_path.exists():
        print(f"❌ Error: Could not find {csv_path.resolve()}")
        sys.exit(1)
        
    if not corpus_dir.exists():
        print(f"❌ Error: Could not find corpus directory {corpus_dir.resolve()}")
        sys.exit(1)

    expected_files = set()
    missing_on_disk = []

    # 2. Read CSV and check for files missing on disk
    with open(csv_path, mode='r', encoding='utf-8') as f:
        # Automatically detect if the file is comma-separated or tab-separated
        sample = f.read(1024)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            # Fallback to standard comma separated if sniffing fails
            dialect = 'excel' 
            
        reader = csv.DictReader(f, dialect=dialect)
        
        for row_num, row in enumerate(reader, start=2): # start=2 accounts for header
            sub_folder = row.get('sub_folder', '').strip()
            xml_filename = row.get('xml_filename', '').strip()
            
            if not sub_folder or not xml_filename:
                continue
                
            # Create a relative path object (e.g., darśanāni/adhikaraṇaratnamālā.txt)
            rel_path = Path(sub_folder) / xml_filename
            expected_files.add(rel_path)
            
            # Check if it exists in the corpus folder
            full_path = corpus_dir / rel_path
            if not full_path.is_file():
                missing_on_disk.append(rel_path)

    # 3. Scan directory and check for files missing in the CSV
    missing_in_csv = []
    # rglob checks all subdirectories for .txt files
    for txt_file in corpus_dir.rglob('*.txt'):
        # Get path relative to the base corpus directory
        rel_path = txt_file.relative_to(corpus_dir)
        if rel_path not in expected_files:
            missing_in_csv.append(rel_path)

    # 4. Print Report
    print("=" * 50)
    print(" " * 12 + "CORPUS VERIFICATION REPORT")
    print("=" * 50)
    
    # Report 1: Missing on Disk
    if missing_on_disk:
        print(f"\n⚠️  Found {len(missing_on_disk)} file(s) in CSV but MISSING from disk:")
        for missing in sorted(missing_on_disk):
            print(f"   - {missing}")
    else:
        print("\n✅ All files listed in the CSV are present on disk.")

    # Report 2: Missing in CSV
    if missing_in_csv:
        print(f"\n⚠️  Found {len(missing_in_csv)} file(s) on disk but MISSING from CSV:")
        for missing in sorted(missing_in_csv):
            print(f"   - {missing}")
    else:
        print("\n✅ All .txt files on disk are properly listed in the CSV.")
        
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
