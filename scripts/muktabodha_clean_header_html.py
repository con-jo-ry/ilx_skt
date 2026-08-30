import csv
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

CSV_FILE = os.path.join(BASE_DIR, 'muktabodha.csv')
CORPUS_DIR = os.path.join(BASE_DIR, 'corpus', 'muktabodha')

def extract_header_block(text):
    """
    Finds the first block of text bounded by lines made of #.
    Returns the header string, the start line index, and the end line index.
    """
    lines = text.splitlines(keepends=True)
    in_header = False
    header_lines = []
    start_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Look for the boundary lines
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

def remove_html(text):
    """
    Uses a regular expression to remove anything between < and >.
    """
    return re.sub(r'<[^>]+>', '', text)

def main():
    if not os.path.exists(CSV_FILE):
        print(f"CRITICAL ERROR: Could not find CSV at {CSV_FILE}")
        return

    processed_count = 0
    files_checked = 0

    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)

    print(f"Scanning {len(rows) - 3} files for HTML tags in headers...")

    for row_num, row in enumerate(rows[3:], start=4):
        if len(row) < 2:
            continue
            
        corpus_filename = row[1].strip()  # Column B (Index 1)
        
        if not corpus_filename:
            continue

        corpus_filepath = os.path.join(CORPUS_DIR, corpus_filename)

        if not os.path.exists(corpus_filepath):
            continue

        files_checked += 1

        with open(corpus_filepath, 'r', encoding='utf-8-sig') as cf:
            corpus_text = cf.read()

        corpus_header, start_idx, end_idx = extract_header_block(corpus_text)

        if corpus_header:
            # Check if there are actually HTML tags in the header before rewriting
            if '<' in corpus_header and '>' in corpus_header:
                cleaned_header = remove_html(corpus_header)
                
                # Double-check that we actually changed something
                if cleaned_header != corpus_header:
                    corpus_lines = corpus_text.splitlines(keepends=True)
                    
                    # Reconstruct the text with the cleaned header
                    new_corpus_text = "".join(corpus_lines[:start_idx]) + cleaned_header + "".join(corpus_lines[end_idx+1:])

                    # Write the cleaned text back to the file
                    with open(corpus_filepath, 'w', encoding='utf-8') as cf:
                        cf.write(new_corpus_text)
                    
                    print(f"[{corpus_filename}] Cleared HTML tags.")
                    processed_count += 1

    print("\n--- Summary ---")
    print(f"Total corpus files checked: {files_checked}")
    print(f"Total headers cleaned of HTML: {processed_count}")

if __name__ == "__main__":
    main()
