#!/usr/bin/env python3
import csv
import os
import re

# Define paths relative to the ./scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, '../dsbc.csv')

def generate_new_name(original_filename, title):
    # Extract the base ID, e.g., "book_85"
    book_id = original_filename.replace('.xml', '').strip()
    
    if not title:
        return f"{book_id}.xml", book_id
        
    # Lowercase, remove brackets, replace spaces with underscores
    clean_title = title.lower()
    clean_title = re.sub(r'[\[\]\(\)]', '', clean_title)
    clean_title = re.sub(r'\s+', '_', clean_title.strip())
    
    new_filename = f"{clean_title}_{book_id}.xml"
    return new_filename, book_id

def main():
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find CSV at {CSV_PATH}")
        return

    print("--- DRY RUN: Proposed File Name Changes ---")
    
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            original = row.get('xml_filename', '').strip()
            title = row.get('dsbc_title', '').strip()
            
            if original:
                new_filename, book_id = generate_new_name(original, title)
                print(f"Original: {original:<20} -> New: {new_filename:<35} (Cat No: {book_id})")

if __name__ == '__main__':
    main()
