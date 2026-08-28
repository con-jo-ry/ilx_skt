import csv
import sys
import shutil
import re
from pathlib import Path

def main():
    # 1. Configure Paths
    csv_path = Path("../muktabodha.csv")
    corpus_dir = Path("../corpus/muktabodha")
    
    # Check src or source directory
    html_dir = Path("../src/muktabodha_download_27_08_2026")
    if not html_dir.exists():
        html_dir = Path("../source/muktabodha_download_27_08_2026")
        
    # Fallbacks if executed from project root
    if not csv_path.exists() and Path("./muktabodha.csv").exists():
        csv_path = Path("./muktabodha.csv")
        corpus_dir = Path("./corpus/muktabodha")
        html_dir = Path("./src/muktabodha_download_27_08_2026")
        if not html_dir.exists():
            html_dir = Path("./source/muktabodha_download_27_08_2026")

    for p, name in [(csv_path, "CSV file"), (html_dir, "HTML source folder"), (corpus_dir, "Text corpus folder")]:
        if not p.exists():
            print(f"❌ Error: Could not find {name} at {p.resolve()}")
            sys.exit(1)

    # 2. Map existing files on disk for easy lookup
    html_files_on_disk = {f.name: f for f in html_dir.rglob('*') if f.is_file() and not f.name.startswith('.')}
    text_files_on_disk = {f.name: f for f in corpus_dir.rglob('*') if f.is_file() and not f.name.startswith('.')}

    # 3. Read the CSV
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    new_rows = []
    renamed_count = 0
    copied_count = 0
    warnings = []

    # 4. Process the rows
    for i, row in enumerate(rows):
        line_num = i + 1
        
        # Keep entirely empty rows untouched
        if not row:
            new_rows.append(row)
            continue
            
        # Preamble rows (Lines 1-2)
        if line_num < 3:
            row.insert(2, "") # Insert blank column between B and C
            new_rows.append(row)
            continue
            
        # Header row (Line 3)
        if line_num == 3:
            row.insert(2, "filename_updated") # Insert new header
            new_rows.append(row)
            continue

        # Data rows (Line 4+)
        # Ensure row has enough columns to read index 1 and 2 safely
        while len(row) < 3:
            row.append("")

        html_filename = row[1].strip()
        txt_filename = row[2].strip() # This is the ORIGINAL Column C

        # If there's no HTML filename to base the pattern on, skip logic and insert empty col
        if not html_filename:
            row.insert(2, "")
            new_rows.append(row)
            continue

        # Pattern transformation: "M00521 - dAzarathIyatantram.htm" -> "dAzarathIyatantram_M00521"
        base_name = re.sub(r'\.html?$', '', html_filename) # Strip extension
        parts = base_name.split(' - ', 1) # Split ONLY on the first " - "
        
        if len(parts) == 2:
            cat_id = parts[0].strip()
            title = parts[1].strip().replace(' ', '_')
            new_base_filename = f"{title}_{cat_id}"
        else:
            # Fallback just in case the format varies
            new_base_filename = base_name.strip().replace(' ', '_')

        new_txt_entry = txt_filename # Default if no change occurs

        # Scenario 1: Text file exists (Original Column C is NOT blank)
        if txt_filename:
            target_xml_name = f"{new_base_filename}.xml"
            if txt_filename in text_files_on_disk:
                old_path = text_files_on_disk[txt_filename]
                new_path = old_path.with_name(target_xml_name)
                
                # Rename the file on disk
                old_path.rename(new_path)
                renamed_count += 1
                
                # Update the entry we will put in the new column
                new_txt_entry = target_xml_name
                
                # Update dictionary in case of duplicates handling
                text_files_on_disk[target_xml_name] = new_path
            else:
                warnings.append(f"Row {line_num}: '{txt_filename}' not found in corpus. Could not rename.")
        
        # Scenario 2: Text file does NOT exist (Original Column C is BLANK)
        else:
            target_htm_name = f"{new_base_filename}.htm"
            if html_filename in html_files_on_disk:
                src_path = html_files_on_disk[html_filename]
                dest_path = corpus_dir / target_htm_name
                
                # Copy file from src to corpus root
                shutil.copy2(src_path, dest_path)
                copied_count += 1
                
                # Update the entry we will put in the new column
                new_txt_entry = target_htm_name
            else:
                warnings.append(f"Row {line_num}: '{html_filename}' not found in src folder. Could not copy.")

        # Insert the newly generated filename at position 2 (Column C)
        # This automatically pushes the old Column C (and all subsequent columns) one spot to the right
        row.insert(2, new_txt_entry)
        new_rows.append(row)

    # 5. Write the updated data back to the CSV
    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    # 6. Print Report
    print("=" * 60)
    print(" " * 12 + "FILE RENAMING & CSV UPDATE REPORT")
    print("=" * 60)
    
    print(f"✅ Successfully processed '{csv_path.name}'.")
    print(f"✅ Added 'filename_updated' column at Column C.")
    print(f"🔄 Renamed {renamed_count} existing text files to .xml")
    print(f"📥 Copied and renamed {copied_count} missing .htm files into corpus")

    if warnings:
        print(f"\n⚠️  Encountered {len(warnings)} issue(s):")
        for w in warnings:
            print(f"   - {w}")
            
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
