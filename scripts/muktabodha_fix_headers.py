import csv
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

CSV_FILE = os.path.join(BASE_DIR, 'muktabodha.csv')
CORPUS_DIR = os.path.join(BASE_DIR, 'corpus', 'muktabodha')
SRC_DIR = os.path.join(BASE_DIR, 'src', 'muktabodha_download_27_08_2026')

def extract_header_block(text):
    lines = text.splitlines(keepends=True)
    in_header = False
    header_lines = []
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Look for any line that is primarily made of #, optionally wrapped in <> or ()
        is_boundary = bool(re.match(r'^[<(]?#+[>)]?$', stripped))
        
        if not in_header and is_boundary:
            in_header = True
            start_idx = i
            header_lines.append(line)
        elif in_header and is_boundary:
            header_lines.append(line)
            end_idx = i
            break
        elif in_header:
            header_lines.append(line)
            
    if start_idx != -1 and end_idx != -1:
        return "".join(header_lines), start_idx, end_idx
    return None, -1, -1

def main():
    print(f"Looking for CSV at: {CSV_FILE}")
    if not os.path.exists(CSV_FILE):
        print(f"CRITICAL ERROR: Could not find CSV at {CSV_FILE}")
        return

    processed_count = 0
    success_count = 0
    files_checked = 0

    # Using utf-8-sig to safely consume any Byte Order Marks (BOM)
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)

    print(f"Total rows in CSV: {len(rows)}")

    for row_num, row in enumerate(rows[3:], start=4):
        # Now we only need at least 2 columns (A and B)
        if len(row) < 2:
            print(f"Row {row_num}: Skipped (less than 2 columns)")
            continue
            
        src_filename = row[0].strip()     # Column A (Index 0)
        corpus_filename = row[1].strip()  # Column B (Index 1)
        
        if not src_filename or not corpus_filename:
            continue

        corpus_filepath = os.path.join(CORPUS_DIR, corpus_filename)
        src_filepath = os.path.join(SRC_DIR, src_filename)

        if not os.path.exists(corpus_filepath):
            print(f"Row {row_num}: MISSING CORPUS FILE -> {corpus_filepath}")
            continue

        files_checked += 1

        with open(corpus_filepath, 'r', encoding='utf-8-sig') as cf:
            corpus_text = cf.read()

        corpus_header, start_idx, end_idx = extract_header_block(corpus_text)

        # Print debug info for the very first file successfully found
        if files_checked == 1:
            print("\n--- DEBUG: First File Inspected ---")
            print(f"File: {corpus_filename}")
            if corpus_header:
                first_line = corpus_header.strip().split('\n')[0]
                print(f"Extracted First Header Line: {repr(first_line)}")
            else:
                print("Extracted Header: NONE FOUND (Regex failed to match # lines)")
            print("-----------------------------------\n")

        if corpus_header and (corpus_header.strip().startswith('<#') or corpus_header.strip().startswith('(#')):
            print(f"[{corpus_filename}] Found modified header. Attempting restore...")
            processed_count += 1
            
            if not os.path.exists(src_filepath):
                print(f"  -> Error: Source file missing {src_filepath}")
                continue

            with open(src_filepath, 'r', encoding='utf-8-sig') as sf:
                src_text = sf.read()
                
            src_header, _, _ = extract_header_block(src_text)
            
            if not src_header:
                print(f"  -> Error: Could not find original header in {src_filename}")
                continue

            corpus_lines = corpus_text.splitlines(keepends=True)
            new_corpus_text = "".join(corpus_lines[:start_idx]) + src_header + "".join(corpus_lines[end_idx+1:])

            with open(corpus_filepath, 'w', encoding='utf-8') as cf:
                cf.write(new_corpus_text)

            with open(corpus_filepath, 'r', encoding='utf-8-sig') as cf:
                verify_text = cf.read()
                
            verify_header, _, _ = extract_header_block(verify_text)
            
            if verify_header and verify_header.strip().startswith('#') and not verify_header.strip().startswith(('<', '(')):
                print(f"  -> Success: {corpus_filename} restored.")
                success_count += 1
            else:
                print(f"  -> Warning: Verification failed for {corpus_filename}.")

    print("\n--- Summary ---")
    print(f"Total corpus files successfully opened: {files_checked}")
    print(f"Total modified headers found: {processed_count}")
    print(f"Successfully restored and verified: {success_count}")

if __name__ == "__main__":
    main()
