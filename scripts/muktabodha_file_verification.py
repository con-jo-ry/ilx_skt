import csv
import sys
from pathlib import Path

def main():
    # 1. Configure Paths
    csv_path = Path("../muktabodha.csv")
    
    # Check for the source dir (handling the extra /src/ you mentioned just in case)
    src_dir = Path("../src/muktabodha_download_27_08_2026")
    if not src_dir.exists():
        src_dir = Path("../src/src/muktabodha_download_27_08_2026")
        if not src_dir.exists():
             src_dir = Path("../source/muktabodha_download_27_08_2026")
            
    corpus_mukta_dir = Path("../corpus/muktabodha")
    corpus_base_dir = Path("../corpus") # Base directory for Col J duplicates checking
    
    # Fallbacks if executed from project root
    if not csv_path.exists() and Path("./muktabodha.csv").exists():
        csv_path = Path("./muktabodha.csv")
        src_dir = Path("./src/muktabodha_download_27_08_2026")
        if not src_dir.exists():
            src_dir = Path("./source/muktabodha_download_27_08_2026")
        corpus_mukta_dir = Path("./corpus/muktabodha")
        corpus_base_dir = Path("./corpus")

    for p, name in [(csv_path, "CSV file"), (src_dir, "HTML source folder"), (corpus_mukta_dir, "Text corpus folder")]:
        if not p.exists():
            print(f"❌ Error: Could not find {name} at {p.resolve()}")
            sys.exit(1)

    # 2. Map existing files on disk for easy lookup (ignoring subdirectories for Col A/B)
    src_files_on_disk = {f.name for f in src_dir.rglob('*') if f.is_file()}
    corpus_files_on_disk = {f.name for f in corpus_mukta_dir.rglob('*') if f.is_file()}

    # 3. Read the CSV and extract all Column J values for the 'y' check
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Extract all values in Col J (Index 9) across the entire document
    all_col_j_values = set()
    for row in rows:
        if len(row) > 9:
            all_col_j_values.add(row[9].strip())

    # 4. Initialize tracking lists for reporting
    missing_col_a = []
    missing_col_b = []
    missing_best_text_ref = []
    missing_duplicate_file = []

    # 5. Process the rows
    for i, row in enumerate(rows):
        line_num = i + 1
        
        # Skip empty rows and the first 3 preamble/header rows
        if not row or line_num < 4:
            continue
            
        # Pad row to ensure we can safely check up to index 9 (Col J)
        while len(row) < 10:
            row.append("")

        val_A = row[0].strip() # Column A
        val_B = row[1].strip() # Column B
        val_I = row[8].strip().lower() # Column I (Best text indicator)
        val_J = row[9].strip() # Column J (Duplicate path)

        # Check Column A against source directory
        if val_A and val_A not in src_files_on_disk:
            missing_col_a.append((line_num, val_A))

        # Check Column B against corpus/muktabodha directory
        if val_B and val_B not in corpus_files_on_disk:
            missing_col_b.append((line_num, val_B))

        # Check Best Text / Duplicate logic
        if val_I == 'y':
            # It's the best text. We expect someone to point to it in Col J.
            if val_B:
                expected_j_val = f"muktabodha/{val_B}"
                if expected_j_val not in all_col_j_values:
                    missing_best_text_ref.append((line_num, expected_j_val))
        
        elif val_I == 'n':
            # It's a duplicate. Col J should have a path, and that file should exist in the base corpus.
            if val_J:
                target_file = corpus_base_dir / val_J
                if not target_file.is_file():
                    missing_duplicate_file.append((line_num, val_J))
            else:
                missing_duplicate_file.append((line_num, "BLANK (No file specified in Col J)"))

    # 6. Print Report
    print("=" * 70)
    print(" " * 20 + "FINAL VERIFICATION REPORT")
    print("=" * 70)

    if missing_col_a:
        print(f"\n❌ Column A: {len(missing_col_a)} file(s) missing from {src_dir.name}/")
        for line, name in missing_col_a:
            print(f"   - Row {line}: {name}")
    else:
        print("\n✅ Column A: All files present in the source folder.")

    if missing_col_b:
        print(f"\n❌ Column B: {len(missing_col_b)} file(s) missing from {corpus_mukta_dir.name}/")
        for line, name in missing_col_b:
            print(f"   - Row {line}: {name}")
    else:
        print("\n✅ Column B: All files present in the corpus folder.")

    if missing_best_text_ref:
        print(f"\n⚠️  Column I ('y'): {len(missing_best_text_ref)} best text(s) have NO references in Column J")
        for line, expected in missing_best_text_ref:
            print(f"   - Row {line}: Nobody points to '{expected}'")
    else:
        print("\n✅ Column I ('y'): All 'best texts' are referenced at least once in Column J.")

    if missing_duplicate_file:
        print(f"\n❌ Column I ('n'): {len(missing_duplicate_file)} duplicate(s) point to non-existent files in base corpus")
        for line, name in missing_duplicate_file:
            print(f"   - Row {line}: missing '{name}'")
    else:
        print("\n✅ Column I ('n'): All duplicates point to valid, existing files in the base corpus.")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
