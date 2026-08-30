#!/usr/bin/env python3
import csv
import os
import re
import html
from datetime import date

# Define paths relative to the ./scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, '../hamburg.csv')
INPUT_DIR = os.path.join(SCRIPT_DIR, '../corpus/hamburg')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '../corpus/hamburg_tei')

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load CSV metadata into a dictionary keyed by filename
    metadata = {}
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row.get('file', '').strip()
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

        # Parse legacy header if it exists between --- marks
        # This regex looks for --- at the start, captures the middle, and captures everything after the second ---
        match = re.match(r'^\s*---\s*\n(.*?)\n\s*---\s*\n(.*)', content, re.DOTALL)
        if match:
            legacy_header = match.group(1).strip()
            main_text = match.group(2).strip()
        else:
            legacy_header = ""
            main_text = content.strip()

        # Fetch metadata for this file (fallback to empty dict if not in CSV)
        file_meta = metadata.get(filename, {})

        # Safely escape text for XML
        title = html.escape(file_meta.get('title', '').strip() or filename)
        author = html.escape(file_meta.get('author', '').strip())
        input_by = html.escape(file_meta.get('input_by', '').strip())
        toh = html.escape(file_meta.get('tōh', '').strip())
        url = html.escape(file_meta.get('etext_src_url', '').strip())
        edition = html.escape(file_meta.get('based_on_edition', '').strip())
        legacy_header_escaped = html.escape(legacy_header)

        # Build optional XML components
        author_xml = f"\n        <author>{author}</author>" if author else ""
        
        resp_xml = ""
        if input_by:
            resp_xml = f"""
        <respStmt>
          <resp>Input by</resp>
          <name>{input_by}</name>
        </respStmt>"""

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
        if edition:
            bibl_items.append(f'<note type="edition">Based on edition: {edition}</note>')
        if toh:
            bibl_items.append(f'<idno type="tōhoku">{toh}</idno>')
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
        <title>{title}</title>{author_xml}{resp_xml}
      </titleStmt>
      <publicationStmt>
        <publisher>ERC-funded Intellexus project / Hamburg Sanskrit Etext Repository</publisher>
        <availability>
          <licence target="https://creativecommons.org/licenses/by/4.0/">
            Creative Commons Attribution 4.0 International (CC BY 4.0)
          </licence>
          <p>
            The TEI markup and metadata are provided by the Intellexus project under a CC BY 4.0 license. 
            The underlying etexts were produced by various contributors. Any original copyleft or rights 
            declarations are preserved in the legacy notes.
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
