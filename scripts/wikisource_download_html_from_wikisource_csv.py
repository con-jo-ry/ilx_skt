import csv
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

def download_html_pages():
    # 1. Setup paths relative to this script's location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    csv_path = project_root / 'wikisource.csv'
    out_dir = project_root / 'src' / 'wikisource'
    
    if not csv_path.exists():
        print(f"[!] Error: {csv_path} not found.")
        return
        
    # Create the target directory if it doesn't exist
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Read the CSV to get the links and filenames
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
            _ = next(reader)  # Skip the blank second row
        except StopIteration:
            print("[!] Error: CSV file does not have enough header rows.")
            return
            
        try:
            link_idx = headers.index('link')
            xml_idx = headers.index('xml_filename')
        except ValueError:
            print("[!] Error: Could not find 'link' or 'xml_filename' columns in row 1.")
            return
            
        rows = list(reader)
        
    # 3. Set a User-Agent header (required by Wikimedia servers for automated requests)
    req_headers = {
        'User-Agent': 'Mozilla/5.0 (SanskritMetadataBot/1.0) Python/urllib'
    }
    
    # 4. Process downloads
    download_count = 0
    print(f"=== Starting Downloads to src/wikisource/ ===")
    
    for row_num, row in enumerate(rows, start=3):
        # Skip completely blank lines
        if not row or not any(row):
            continue
            
        link = row[link_idx].strip() if link_idx < len(row) else ''
        xml_name = row[xml_idx].strip() if xml_idx < len(row) else ''
        
        if not link or not xml_name:
            continue
            
        # Swap the extension to .html to match the XML filename
        base_name = os.path.splitext(xml_name)[0]
        html_filename = f"{base_name}.html"
        html_path = out_dir / html_filename
        
        if html_path.exists():
            print(f"[-] Skipping {html_filename} (already exists)")
            continue
            
        print(f"[*] Downloading: {link} -> {html_filename}")
        
        # Prepare the request
        req = urllib.request.Request(link, headers=req_headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                html_content = response.read()
                
            with open(html_path, 'wb') as out_f:
                out_f.write(html_content)
                
            download_count += 1
            
            # Polite delay to avoid hammering the Wikisource servers
            time.sleep(1) 
            
        except urllib.error.URLError as e:
            print(f"    [!] Failed to download {link}: {e}")
            
    print(f"\n=== Complete: Downloaded {download_count} new files ===")

if __name__ == '__main__':
    download_html_pages()
