import csv
import os
from pathlib import Path

def merge_wikisource_index():
    # 1. Setup paths relative to this script's location
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    wikisource_csv_path = project_root / 'wikisource.csv'
    index_csv_path = project_root / 'wikisource_index.csv'
    
    if not wikisource_csv_path.exists():
        print(f"[!] Error: {wikisource_csv_path} not found.")
        return
    if not index_csv_path.exists():
        print(f"[!] Error: {index_csv_path} not found.")
        return

    # 2. Read index data into a dictionary for quick lookup
    index_map = {}
    with open(index_csv_path, mode='r', encoding='utf-8-sig') as f:
        # Using DictReader assumes row 1 contains headers: title, original_link, link, notes
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('title', '').strip()
            if not title:
                continue
                
            # Match up to the first whitespace
            match_key = title.split()[0]
            
            # Save the relevant columns (keeping the first match if duplicates exist)
            if match_key not in index_map:
                index_map[match_key] = {
                    'title': title,
                    'link': row.get('link', ''),
                    'notes': row.get('notes', '')
                }
                
    # 3. Read the existing wikisource.csv
    with open(wikisource_csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    if len(rows) < 2:
        print("[!] Error: wikisource.csv does not have the expected 2 header rows.")
        return
        
    # 4. Update headers in the first two rows
    rows[0].extend(['index_title', 'link', 'notes'])
    rows[1].extend(['', '', ''])
    
    # 5. Process data rows and append matches
    match_count = 0
    for i in range(2, len(rows)):
        row = rows[i]
        
        # Skip completely blank lines
        if not row or not any(row):
            continue
            
        # Get xml_filename (assumes it is in the second column / index 1)
        xml_filename = row[1] if len(row) > 1 else ""
        
        # Strip extension, then split by whitespace to get the match key
        base_name = os.path.splitext(xml_filename)[0]
        match_key = base_name.split()[0] if base_name else ""
        
        if match_key in index_map:
            match_data = index_map[match_key]
            row.extend([match_data['title'], match_data['link'], match_data['notes']])
            match_count += 1
        else:
            # Append empty strings if no match is found to keep columns aligned
            row.extend(['', '', ''])
            
    # 6. Write the updated data back to wikisource.csv
    with open(wikisource_csv_path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        
    # 7. Print summary
    total_files = len(rows) - 2
    print(f"=== Merge Complete ===")
    print(f"Successfully merged index data into {wikisource_csv_path}")
    print(f"Found matches for {match_count} out of {total_files} files.")

if __name__ == '__main__':
    merge_wikisource_index()
