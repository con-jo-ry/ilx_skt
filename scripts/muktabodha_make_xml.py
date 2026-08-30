#!/usr/bin/env python3
import csv
import os
import re
import html
from datetime import date

# Define paths relative to the ./scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, '../muktabodha.csv')
INPUT_DIR = os.path.join(SCRIPT_DIR, '../corpus/muktabodha')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '../corpus/muktabodha_tei')

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load CSV metadata into a dictionary keyed by the actual XML filename
    metadata = {}
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row.get('filename', '').strip()
            if filename:
                metadata[filename] = row

    # Process each file in the input directory
    for filename in os.listdir(INPUT_DIR):
        input_filepath = os.path.join(INPUT_DIR, filename)
        
        # Skip directories
        if not os.path.isfile(input_filepath):
            continue
            
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse legacy header if it exists between multiple # marks
        # This regex looks for lines made entirely of # characters
        match = re.match(r'^\s*#+\s*\n(.*?)\n\s*#+\s*\n(.*)', content, re.DOTALL)
        if match:
            legacy_header = match.group(1).strip()
            main_text = match.group(2).strip()
        else:
            legacy_header = ""
            main_text = content.strip()

        # Fetch metadata for this file
        file_meta = metadata.get(filename, {})

        # Safely escape text for XML
        title = html.escape(file_meta.get('title', '').strip() or filename)
        author = html.escape(file_meta.get('author', '').strip())
        author_pid = html.escape(file_meta.get('author_pid', '').strip())
        catalog_num = html.escape(file_meta.get('catalogue_number', '').strip())
        url = html.escape(file_meta.get('etext_link', '').strip())
        legacy_header_escaped = html.escape(legacy_header)

        # Build XML components
        author_attr = f' ref="{author_pid}"' if author_pid else ""
        author_xml = f"\n        <author{author_attr}>{author}</author>" if author else ""
        
        notes_stmt_xml = ""
        if legacy_header_escaped:
            notes_stmt_xml = f"""
      <notesStmt>
        <note type="legacy_header">
{legacy_header_escaped}
        </note>
      </notesStmt>"""

        # Build bibliography components
        bibl_items = []
        if catalog_num:
            bibl_items.append(f'<idno type="muktabodha_catalog">{catalog_num}</idno>')
        if url:
            bibl_items.append(f'<ptr target="{url}"/>')
        
        bibl_content = "\n          ".join(bibl_items) if bibl_items else "Source details unavailable."

        current_date = date.today().isoformat()

        # Assemble the final TEI XML
        tei_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>{title}</title>{author_xml}
        <respStmt>
          <resp>Original digitization and data entry</resp>
          <name>Muktabodha Indological Research Institute</name>
        </respStmt>
      </titleStmt>
      <publicationStmt>
        <publisher>Muktabodha Indological Research Institute</publisher>
        <availability>
          <licence target="https://creativecommons.org/licenses/by-nc/4.0/">
            Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
          </licence>
          <p>
            The etext is provided by the Muktabodha Indological Research Institute 
            under a CC BY-NC 4.0 license.
          </p>
        </availability>
      </publicationStmt>{notes_stmt_xml}
      <sourceDesc>
        <bibl>
          {bibl_content}
        </bibl>
      </sourceDesc>
    </fileDesc>
    <revisionDesc>
      <change when="{current_date}">Mass converted to basic TEI encoding standards by the ERC-funded Intellexus project.</change>
    </revisionDesc>
  </teiHeader>
  <text>
    <body>
{main_text}
    </body>
  </text>
</TEI>
"""
        
        # Write to the output directory
        output_filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Ensure it has an .xml extension if it didn't already
        if not output_filepath.endswith('.xml'):
            output_filepath += '.xml'
            
        with open(output_filepath, 'w', encoding='utf-8') as out_f:
            out_f.write(tei_xml)
            
        print(f"Processed: {filename}")

    print(f"\nConversion complete. Files saved to: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == '__main__':
    main()
