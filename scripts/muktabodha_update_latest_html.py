import csv
import sys
import re
from pathlib import Path

def main():
    # 1. Configure Paths
    # Assuming script runs from ./scripts
    csv_path = Path("../muktabodha.csv")
    source_dir = Path("../src/muktabodha_download_27_08_2026")
    
    # Fallback if executed from project root
    if not csv_path.exists() and Path("./muktabodha.csv").exists():
        csv_path = Path("./muktabodha.csv")
        source_dir = Path("./source/muktabodha_download_27_08_2026")

    if not csv_path.exists():
        print(f"❌ Error: Could not find {csv_path.resolve()}")
        sys.exit(1)
        
    if not source_dir.exists():
        print(f"❌ Error: Could not find source directory {source_dir.resolve()}")
        sys.exit(1)

    # 2. Gather all .htm / .html files in the source directory
    # rglob('*.htm*') catches both .htm and .html extensions
    html_files = [f for f in source_dir.rglob('*.htm*') if f.is_file()]
    unmatched_files = set(f.name for f in html_files)

    # 3. Read the existing CSV
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    new_rows = []
    max_cols = 0
    
    # 4. Process rows and map filenames
    for i, row in enumerate(rows):
        line_num = i + 1 # 1-based indexing
        
        if not row:
            new_rows.append([])
            continue

        # Catalogue number is in the 3rd column (index 2) of the original layout
        original_col3 = row[2].strip() if len(row) > 2 else ""
        new_val = ""
        
        if line_num < 3:
            # Preamble rows (Lines 1-2)
            new_val = "" 
        elif line_num == 3:
            # Header row (Line 3)
            new_val = "html file name"
        else:
            # Data rows (Line 4 and onwards)
            cat_no = original_col3
            
            if cat_no:
                # Search for the catalogue number in unmatched files
                for f_name in list(unmatched_files):
                    if cat_no in f_name:
                        new_val = f_name
                        unmatched_files.remove(f_name)
                        break

        # Construct the new row: Col 1 + New Col + Remaining original columns
        new_row = row[:1] + [new_val] + row[1:]
        max_cols = max(max_cols, len(new_row))
        new_rows.append(new_row)

    # 5. Append rows for unmatched HTML files
    appended_count = len(unmatched_files)
    if unmatched_files:
        for f_name in sorted(unmatched_files):
            # Create an empty row matching the current CSV width
            appended_row = [""] * max_cols
            
            # Put the filename in Position 2 (index 1)
            appended_row[1] = f_name
            
            # Try to extract the catalogue number (e.g., E00002 or M00198) and put it in Position 4 (index 3)
            # Position 4 in the *new* layout corresponds to the original 3rd column
            cat_match = re.search(r'[A-Za-z]\d{4,5}', f_name)
            if cat_match and len(appended_row) > 3:
                appended_row[3] = cat_match.group(0)
                
            new_rows.append(appended_row)

    # 6. Write the updated data back to the CSV
    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    # 7. Print Report
    print("=" * 60)
    print(" " * 12 + "MUKTABODHA HTML UPDATE REPORT")
    print("=" * 60)
    print(f"✅ Successfully updated '{csv_path.name}' with the 'html file name' column.")
    
    if appended_count > 0:
        print(f"⚠️  Found {appended_count} .htm file(s) without a CSV match.")
        print(f"✅ Appended {appended_count} new row(s) to the end of the CSV.")
    else:
        print("✅ All .htm files in the source directory matched existing rows.")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
