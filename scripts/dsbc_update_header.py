#!/usr/bin/env python3
import csv
import os
import re
import html
from datetime import date

# Define paths relative to the ./scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, '../dsbc.csv')
INPUT_DIR = os.path.join(SCRIPT_DIR, '../corpus/dsbc')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '../corpus/dsbc_tei')

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load CSV metadata into a dictionary keyed by the actual XML filename
    metadata = {}
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find CSV at {CSV_PATH}")
        return

    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row.get('file_name', '').strip()
            if filename:
                metadata[filename] = row

    # Process each file in the input directory
    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith('.xml'):
            continue
            
        input_filepath = os.path.join(INPUT_DIR, filename)
        
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Extract existing <respStmt> blocks
        resp_stmts = re.findall(r'<respStmt>.*?</respStmt>', content, re.DOTALL)
        # Format them with proper indentation
        resp_stmts_xml = "\n        ".join(resp_stmts)
        if resp_stmts_xml:
            resp_stmts_xml = f"\n        {resp_stmts_xml}"

        # 2. Extract the main <text> ... </text> block
        text_match = re.search(r'<text>.*?</text>', content, re.DOTALL)
        if text_match:
            main_text_block = text_match.group(0)
        else:
            # Fallback if no <text> wrapper is found
            main_text_block = "<text>\n    <body>\n[TEXT EXTRACTION ERROR]\n    </body>\n  </text>"
            print(f"Warning: Could not isolate <text> block in {filename}")

        # Fetch metadata for this file
        file_meta = metadata.get(filename, {})
        if not file_meta:
            print(f"Warning: No CSV metadata found for {filename}. Proceeding with default values.")

        # Safely escape text for XML
        title = html.escape(file_meta.get('title', '').strip() or filename)
        author = html.escape(file_meta.get('author', '').strip())
        author_id = html.escape(file_meta.get('author_id', '').strip())
        catalog_no = html.escape(file_meta.get('catalogue_no', '').strip())
        toh = html.escape(file_meta.get('tōh.', '').strip())
        cbeta = html.escape(file_meta.get('CBETA number', '').strip())
        url = html.escape(file_meta.get('url', '').strip())
        archive_url = html.escape(file_meta.get('archive.org', '').strip())

        # Build XML components
        author_attr = f' ref="{author_id}"' if author_id else ""
        author_xml = f"\n        <author{author_attr}>{author}</author>" if author else ""
        
        bibl_items = []
        if catalog_no:
            bibl_items.append(f'<idno type="dsbc_catalog">{catalog_no}</idno>')
        if toh:
            bibl_items.append(f'<idno type="tōhoku">{toh}</idno>')
        if cbeta:
            bibl_items.append(f'<idno type="cbeta">{cbeta}</idno>')
        if url:
            bibl_items.append(f'<ptr type="dsbc_url" target="{url}"/>')
        if archive_url:
            bibl_items.append(f'<ptr type="archive_url" target="{archive_url}"/>')
        
        bibl_content = "\n          ".join(bibl_items) if bibl_items else "Source details unavailable."
        
        current_date = date.today().isoformat()

        # Assemble the final TEI XML
        tei_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>{title}</title>{author_xml}{resp_stmts_xml}
      </titleStmt>
      <publicationStmt>
        <publisher>Nagarjuna Institute of Exact Methods</publisher>
        <distributor>ERC-funded Intellexus project</distributor>
        <date>2008</date>
        <sponsor>University of the West</sponsor>
        <availability status="restricted">
          <licence target="https://www.dsbcproject.org/pages/usage-policy">
            DSBC Usage Policy
          </licence>
          <p>
            These e-texts are compiled and provided by the University of the West strictly for 
            noncommercial educational and research purposes. Rights in the compilation, indexing, 
            and transliteration are held by the University of the West. Reproduction of DSBC 
            contents without permission is prohibited.
          </p>
        </availability>
      </publicationStmt>
      <sourceDesc>
        <bibl>
          {bibl_content}
        </bibl>
        <p>Text Version: Romanized</p>
      </sourceDesc>
    </fileDesc>
    <revisionDesc>
      <change when="{current_date}">TEI header updated and augmented with catalog metadata by the ERC-funded Intellexus project.</change>
    </revisionDesc>
  </teiHeader>
  {main_text_block}
</TEI>
"""
        
        # Write to the output directory
        output_filepath = os.path.join(OUTPUT_DIR, filename)
        with open(output_filepath, 'w', encoding='utf-8') as out_f:
            out_f.write(tei_xml.strip() + "\n")
            
        print(f"Processed: {filename}")

    print(f"\nConversion complete. Files saved to: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == '__main__':
    main()
