#!/usr/bin/env python3
import csv
import os
import html
from datetime import date

# Define paths relative to the ./scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, '../wikisource.csv')
INPUT_DIR = os.path.join(SCRIPT_DIR, '../corpus/wikisource')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '../corpus/wikisource_tei')

def main():
    # Ensure output base directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Open and process the CSV
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            sub_folder = row.get('sub_folder', '').strip()
            filename = row.get('xml_filename', '').strip()
            
            if not filename:
                continue

            # Construct the input path dynamically
            input_filepath = os.path.join(INPUT_DIR, sub_folder, filename)
            
            # Check if the file actually exists
            if not os.path.isfile(input_filepath):
                print(f"Warning: File not found at {input_filepath}. Skipping.")
                continue

            # Read the main text
            with open(input_filepath, 'r', encoding='utf-8') as text_f:
                main_text = text_f.read().strip()

            # Safely escape text for XML
            title = html.escape(row.get('title', '').strip() or filename)
            author = html.escape(row.get('author', '').strip())
            link = html.escape(row.get('link', '').strip())

            # Build XML components
            author_xml = f"\n        <author>{author}</author>" if author else ""
            
            # Build bibliography components
            bibl_content = f'<ptr target="{link}"/>' if link else "Source link unavailable."

            current_date = date.today().isoformat()

            # Assemble the final TEI XML
            tei_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>{title}</title>{author_xml}
        <respStmt>
          <resp>Original digitization and proofreading</resp>
          <name>Wikisource Contributors</name>
        </respStmt>
        <respStmt>
          <resp>Compilation, IAST transliteration, and TEI encoding</resp>
          <name>ERC-funded Intellexus project</name>
        </respStmt>
      </titleStmt>
      <publicationStmt>
        <publisher>Sanskrit Wikisource / ERC-funded Intellexus project</publisher>
        <availability>
          <licence target="https://creativecommons.org/licenses/by-sa/4.0/">
            Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
          </licence>
          <p>
            The underlying etext was sourced from Sanskrit Wikisource. In accordance with 
            Wikisource's standard licensing, this derived and transliterated TEI edition is 
            distributed under a CC BY-SA 4.0 license.
          </p>
        </availability>
      </publicationStmt>
      <sourceDesc>
        <bibl>
          {bibl_content}
        </bibl>
      </sourceDesc>
    </fileDesc>
    <revisionDesc>
      <change when="{current_date}">Compiled into a single file, transliterated to IAST, and converted to basic TEI encoding by the ERC-funded Intellexus project.</change>
    </revisionDesc>
  </teiHeader>
  <text>
    <body>
{main_text}
    </body>
  </text>
</TEI>
"""
            
            # Create subdirectories in the output folder if needed
            output_sub_dir = os.path.join(OUTPUT_DIR, sub_folder)
            os.makedirs(output_sub_dir, exist_ok=True)

            # Change extension to .xml
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}.xml"
            output_filepath = os.path.join(output_sub_dir, output_filename)
            
            with open(output_filepath, 'w', encoding='utf-8') as out_f:
                out_f.write(tei_xml)
                
            print(f"Processed: {os.path.join(sub_folder, filename)} -> {output_filename}")

    print(f"\nConversion complete. Files saved to: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == '__main__':
    main()
