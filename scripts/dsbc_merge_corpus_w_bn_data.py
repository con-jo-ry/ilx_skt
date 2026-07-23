import os
import csv
import xml.etree.ElementTree as ET

def process_dsbc_collection(xml_directory, input_csv, output_csv):
    # Namespace dictionary to handle the TEI XML format
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    xml_data = []

    # 1. Run through the XML files in the specified directory
    if not os.path.exists(xml_directory):
        print(f"Directory {xml_directory} not found.")
        return

    for filename in os.listdir(xml_directory):
        if filename.endswith('.xml'):
            filepath = os.path.join(xml_directory, filename)
            try:
                tree = ET.parse(filepath)
                root = tree.getroot()

                # Extract the title
                title_elem = root.find('.//tei:titleStmt/tei:title', ns)
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""

                # Extract the source URL
                url = ""
                source_desc_ps = root.findall('.//tei:sourceDesc/tei:p', ns)
                for p in source_desc_ps:
                    # Look for the <p> tag containing the http link
                    if p.text and 'http' in p.text:
                        url = p.text.strip()
                        break

                xml_data.append({
                    'file_name': filename,
                    'title': title,
                    'url': url
                })
            except ET.ParseError:
                print(f"Error parsing XML file: {filename}")
            except Exception as e:
                print(f"Unexpected error with {filename}: {e}")

    # 2. Read the existing metadata CSV
    rows = []
    try:
        with open(input_csv, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            original_fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)
    except FileNotFoundError:
        print(f"Input CSV {input_csv} not found.")
        return

    # 3. Add the two new columns at the beginning
    new_fieldnames = ['file name', 'titls as per dsbc']
    for col in original_fieldnames:
        if col not in new_fieldnames:
            new_fieldnames.append(col)

    # 4. Match URLs and update/append rows
    for data in xml_data:
        target_url = data['url']
        match_found = False
        
        # Check if the URL exists in the 'GRETIL/DSBC Link' column
        for row in rows:
            if row.get('GRETIL/DSBC Link', '').strip() == target_url and target_url != "":
                row['file name'] = data['file_name']
                row['titls as per dsbc'] = data['title']
                match_found = True
                break # Move to the next XML file once matched
        
        # If the URL can't be found, create a new row
        if not match_found:
            new_row = {col: "" for col in new_fieldnames}
            new_row['file name'] = data['file_name']
            new_row['titls as per dsbc'] = data['title']
            new_row['GRETIL/DSBC Link'] = target_url
            rows.append(new_row)

    # 5. Write the updated data to the output CSV
    with open(output_csv, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Processing complete! Found {len(xml_data)} XML files. Output saved to {output_csv}")

# Execution
if __name__ == "__main__":
    XML_DIR = 'corpus/dsbc'
    INPUT_CSV = 'dsbc.csv'
    # Writing to a new file to prevent accidental data loss during testing
    OUTPUT_CSV = 'dsbc_updated.csv' 
    
    process_dsbc_collection(XML_DIR, INPUT_CSV, OUTPUT_CSV)
