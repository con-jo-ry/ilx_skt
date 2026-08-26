import csv
import sys
from pathlib import Path

def main():
    # 1. Configure Paths
    # Since the script runs from ./scripts, we point to the parent directory (..)
    csv_path = Path("../muktabodha.csv")
    corpus_dir = Path("../corpus/muktabodha")
    
    # Fallback: just in case the script is executed from the project root instead
    if not csv_path.exists() and Path("./muktabodha.csv").exists():
        csv_path = Path("./muktabodha.csv")
        corpus_dir = Path("./corpus/muktabodha")

    if not csv_path.exists():
        print(f"❌ Error: Could not find {csv_path.resolve()}")
        sys.exit(1)
        
    if not corpus_dir.exists():
        print(f"❌ Error: Could not find corpus directory {corpus_dir.resolve()}")
        sys.exit(1)

    # 2. Gather all text files in the directory
    # Using rglob to catch files even if they are in subfolders
    corpus_files = [f for f in corpus_dir.rglob('*') if f.is_file() and not f.name.startswith('.')]
    
    # Keep a set of filenames to track which ones haven't been matched
    unmatched_files = set(f.name for f in corpus_files)

    # 3. Read the existing CSV
    with open(csv_path, mode='r', encoding='utf-8') as f:
        # We use a standard reader since we are doing structural modifications
        reader = csv.reader(f)
        rows = list(reader)

    new_rows = []
    
    # 4. Process rows and map filenames
    for i, row in enumerate(rows):
        line_num = i + 1 # 1-based indexing for easier reasoning
        
        # Handle cases where the row might be entirely empty
        if not row:
            new_rows.append([])
            continue

        # The catalogue number is currently in the 2nd column (index 1)
        original_col2 = row[1].strip() if len(row) > 1 else ""
        
        new_val = ""
        
        if line_num < 4:
            # Preambles / Title rows (Lines 1-3)
            new_val = "" 
        elif line_num == 4:
            # Header row (Line 4)
            new_val = "filename"
        else:
            # Data rows (Line 5 and onwards)
            cat_no = original_col2
            
            if cat_no:
                # Search for the catalogue number in our set of available files
                for f_name in list(unmatched_files): # Iterate over a copy so we can remove
                    if cat_no in f_name:
                        new_val = f_name
                        unmatched_files.remove(f_name)
                        break

        # Construct the new row: Col 1 + New Filename Col + Remaining original columns
        new_row = row[:1] + [new_val] + row[1:]
        new_rows.append(new_row)

    # 5. Write the updated data back to the CSV
    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    # 6. Print Report
    print("=" * 60)
    print(" " * 12 + "MUKTABODHA UPDATE REPORT")
    print("=" * 60)
    print(f"\n✅ Successfully updated '{csv_path.name}' with the 'filename' column.")

    # Report files in directory without a corresponding entry in CSV
    if unmatched_files:
        print(f"\n⚠️  Found {len(unmatched_files)} file(s) in the corpus folder WITHOUT a match in the CSV:")
        for missing in sorted(unmatched_files):
            print(f"   - {missing}")
    else:
        print("\n✅ All files in the corpus directory are accounted for in the CSV.")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
