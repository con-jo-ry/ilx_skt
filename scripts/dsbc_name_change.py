#!/usr/bin/env python3
import csv
import os
import re

# Define paths relative to the ./scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(SCRIPT_DIR, '../dsbc.csv')
OUTPUT_CSV = os.path.join(SCRIPT_DIR, '../dsbc_updated.csv')
CORPUS_DIR = os.path.join(SCRIPT_DIR, '../corpus/dsbc')

def generate_new_name(original_filename, title):
    book_id = original_filename.replace('.xml', '').strip()
    if not title:
        return f"{book_id}.xml", book_id
        
    clean_title = title.lower()
    clean_title = re.sub(r'[\[\]\(\)]', '', clean_title)
    clean_title = re.sub(r'\s+', '_', clean_title.strip())
    
    new_filename = f"{clean_title}_{book_id}.xml"
    return new_filename, book_id

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: Could not find CSV at {INPUT_CSV}")
        return

    updated_rows = []
    
    with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        # Insert "new file name" and "catalogue_no" at columns B and C (indices 1 and 2)
        new_headers = [headers[0], "new file name", "catalogue_no"] + headers[1:]
        
        for row in reader:
            original_filename = row[0].strip()
            # Title is originally at index 1 (which becomes index 3 in the new list structure, but it's index 1 in the current row list)
            title = row[1].strip() if len(row) > 1 else ""
            
            if original_filename:
                new_filename, catalog_no = generate_new_name(original_filename, title)
                
                # Construct the new row structure
                new_row = [original_filename, new_filename, catalog_no] + row[1:]
                updated_rows.append(new_row)
                
                # Rename the actual file
                old_path = os.path.join(CORPUS_DIR, original_filename)
                new_path = os.path.join(CORPUS_DIR, new_filename)
                
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    print(f"Renamed: {original_filename} -> {new_filename}")
                else:
                    print(f"Warning: File not found for renaming: {old_path}")

    # Write the updated CSV
    with open(OUTPUT_CSV, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(new_headers)
        writer.writerows(updated_rows)
        
    print(f"\nCompleted renaming files. Updated CSV saved to {os.path.abspath(OUTPUT_CSV)}")

if __name__ == '__main__':
    main()
