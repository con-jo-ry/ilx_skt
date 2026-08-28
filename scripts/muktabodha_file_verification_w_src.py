import csv
import sys
from pathlib import Path

def main():
    # 1. Configure Paths
    csv_path = Path("../muktabodha.csv")
    corpus_dir = Path("../corpus/muktabodha")
    
    # Try src first, fallback to source just in case
    html_dir = Path("../src/muktabodha_download_27_08_2026")
    if not html_dir.exists():
        html_dir = Path("../source/muktabodha_download_27_08_2026")
        
    # Fallback if executed from project root
    if not csv_path.exists() and Path("./muktabodha.csv").exists():
        csv_path = Path("./muktabodha.csv")
        corpus_dir = Path("./corpus/muktabodha")
        html_dir = Path("./src/muktabodha_download_27_08_2026")
        if not html_dir.exists():
            html_dir = Path("./source/muktabodha_download_27_08_2026")

    # 2. Validate paths exist before proceeding
    missing_paths = False
    for p, name in [(csv_path, "CSV file"), (html_dir, "HTML source folder"), (corpus_dir, "Text corpus folder")]:
        if not p.exists():
            print(f"❌ Error: Could not find {name} at {p.resolve()}")
            missing_paths = True
    if missing_paths:
        sys.exit(1)

    # 3. Gather all files currently in the directories (ignoring hidden files)
    # We use dictionaries to map filenames to their full paths to handle subdirectories
    html_files_on_disk = {f.name: f for f in html_dir.rglob('*') if f.is_file() and not f.name.startswith('.')}
    text_files_on_disk = {f.name: f for f in corpus_dir.rglob('*') if f.is_file() and not f.name.startswith('.')}

    # Sets to track unaccounted files (we will remove matches from these)
    unaccounted_html = set(html_files_on_disk.keys())
    unaccounted_text = set(text_files_on_disk.keys())

    missing_html_in_dir = []
    missing_text_in_dir = []

    # 4. Read the CSV and verify
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            line_num = i + 1
            
            # Skip empty rows and the first 3 preamble/header rows
            if not row or line_num <= 3:
                continue

            # Get filenames from Column B (index 1) and Column C (index 2)
            html_filename = row[1].strip() if len(row) > 1 else ""
            text_filename = row[2].strip() if len(row) > 2 else ""

            # Check Column B (HTML files)
            if html_filename:
                if html_filename in html_files_on_disk:
                    unaccounted_html.discard(html_filename)
                else:
                    missing_html_in_dir.append((line_num, html_filename))

            # Check Column C (Text files)
            if text_filename:
                if text_filename in text_files_on_disk:
                    unaccounted_text.discard(text_filename)
                else:
                    missing_text_in_dir.append((line_num, text_filename))

    # 5. Print Report
    print("=" * 70)
    print(" " * 20 + "FILE VERIFICATION REPORT")
    print("=" * 70)

    # Missing from directories (In CSV, but not on disk)
    if missing_html_in_dir:
        print(f"\n❌ Missing HTML Files ({len(missing_html_in_dir)} found in CSV but missing from {html_dir.name}/):")
        for line, name in missing_html_in_dir:
            print(f"   - Row {line}: {name}")
    else:
        print(f"\n✅ All HTML files listed in the CSV are present in {html_dir.name}/")

    if missing_text_in_dir:
        print(f"\n❌ Missing Text Files ({len(missing_text_in_dir)} found in CSV but missing from {corpus_dir.name}/):")
        for line, name in missing_text_in_dir:
            print(f"   - Row {line}: {name}")
    else:
        print(f"\n✅ All Text files listed in the CSV are present in {corpus_dir.name}/")

    print("\n" + "-" * 70)

    # Unaccounted files on disk (On disk, but not in CSV)
    if unaccounted_html:
        print(f"\n⚠️  Unaccounted HTML Files ({len(unaccounted_html)} files in {html_dir.name}/ NOT in CSV):")
        for name in sorted(unaccounted_html):
            print(f"   - {name}")
    else:
        print(f"\n✅ No leftover/unaccounted HTML files in {html_dir.name}/")

    if unaccounted_text:
        print(f"\n⚠️  Unaccounted Text Files ({len(unaccounted_text)} files in {corpus_dir.name}/ NOT in CSV):")
        for name in sorted(unaccounted_text):
            print(f"   - {name}")
    else:
        print(f"\n✅ No leftover/unaccounted Text files in {corpus_dir.name}/")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
