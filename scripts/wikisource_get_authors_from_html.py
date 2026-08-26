import csv
import os
import re
from pathlib import Path

# Attempt to import the transliteration library
try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
except ImportError:
    print("[!] Error: The 'indic-transliteration' library is not installed.")
    print("    Please install it by running: pip install indic-transliteration")
    exit(1)

def extract_metadata():
    # 1. Setup paths
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    csv_path = project_root / 'wikisource.csv'
    html_dir = project_root / 'src' / 'wikisource'
    
    if not csv_path.exists():
        print(f"[!] Error: {csv_path} not found.")
        return
    if not html_dir.exists():
        print(f"[!] Error: HTML directory {html_dir} not found. Did you run the download script?")
        return

    # 2. Read the existing CSV
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    if len(rows) < 2:
        print("[!] Error: CSV does not have enough header rows.")
        return
        
    try:
        xml_idx = rows[0].index('xml_filename')
    except ValueError:
        print("[!] Error: Could not find 'xml_filename' column in row 1.")
        return

    # 3. Add the new 'author' and 'author_iast' headers
    rows[0].extend(['author', 'author_iast'])
    rows[1].extend(['', ''])
    
    # Regex pattern to find the author span
    author_pattern = re.compile(r'<span\s+id="ws-author"\s*>(.*?)</span>', re.IGNORECASE | re.DOTALL)
    
    # 4. Process each row
    found_count = 0
    missing_count = 0
    
    print("=== Extracting and Transliterating Authors ===")
    for i in range(2, len(rows)):
        row = rows[i]
        
        if not row or not any(row):
            continue
            
        xml_name = row[xml_idx].strip() if xml_idx < len(row) else ''
        if not xml_name:
            row.extend(['', ''])
            continue
            
        base_name = os.path.splitext(xml_name)[0]
        html_filename = f"{base_name}.html"
        html_path = html_dir / html_filename
        
        author_deva = ""
        author_iast = ""
        
        if html_path.exists():
            try:
                with open(html_path, 'r', encoding='utf-8') as hf:
                    html_content = hf.read()
                    
                match = author_pattern.search(html_content)
                if match:
                    author_deva = match.group(1).strip()
                    if author_deva:
                        # Convert Devanagari to IAST
                        author_iast = transliterate(author_deva, sanscript.DEVANAGARI, sanscript.IAST)
                        found_count += 1
                    else:
                        missing_count += 1
                else:
                    missing_count += 1
            except Exception as e:
                print(f"  [!] Error reading {html_filename}: {e}")
                missing_count += 1
        else:
            missing_count += 1
            
        # Append both the Devanagari and IAST strings to the row
        row.extend([author_deva, author_iast])

    # 5. Write the updated data back to the CSV
    with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        
    print(f"=== Complete ===")
    print(f"Successfully added 'author' and 'author_iast' columns to {csv_path}")
    print(f"Found and transliterated authors for {found_count} files.")
    print(f"No author data found for {missing_count} files.")

if __name__ == '__main__':
    extract_metadata()
