import os
import csv
import xml.etree.ElementTree as ET

# Define paths
xml_dir = 'gretil_sa'
gretil_master_csv = 'gretil_updated.csv'  # Building on top of our previous script's output
final_master_csv = 'gretil_final.csv'

# --- STEP 1: SCAN XML FILES FOR DSBC PROVENANCE ---
print("Scanning XML headers for DSBC input project signatures...")
dsbc_xml_files = set()

if not os.path.exists(xml_dir):
    print(f"Error: Directory '{xml_dir}' not found.")
    exit()

# Handle TEI namespace mapping
namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}

# Target phrases to identify DSBC source material
target_resp = "data entry"
target_name = "members of the digital sanskrit buddhist canon input project"

for filename in os.listdir(xml_dir):
    if filename.endswith('.xml'):
        file_path = os.path.join(xml_dir, filename)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find all <respStmt> elements anywhere in the tree
            resp_stmts = root.findall('.//tei:respStmt', namespaces) or root.findall('.//respStmt')
            
            for stmt in resp_stmts:
                # Find <resp> and <name> within this specific <respStmt>
                resp_elem = stmt.find('tei:resp', namespaces) if stmt.find('tei:resp', namespaces) is not None else stmt.find('resp')
                name_elem = stmt.find('tei:name', namespaces) if stmt.find('tei:name', namespaces) is not None else stmt.find('name')
                
                if resp_elem is not None and name_elem is not None:
                    resp_text = "".join(resp_elem.itertext()).strip().lower()
                    name_text = "".join(name_elem.itertext()).strip().lower()
                    
                    # Check if the signature matches our DSBC project definitions
                    if target_resp in resp_text and target_name in name_text:
                        dsbc_xml_files.add(filename)
                        break  # No need to check more statements in this file
                        
        except Exception as e:
            print(f"Warning: Could not parse {filename} header. Error: {e}")

print(f"Analysis complete. Identified {len(dsbc_xml_files)} files originally sourced from DSBC.")

# --- STEP 2: UPDATE CSV WITH THE 'DSBC' COLUMN ---
print(f"Appending provenance flags to {gretil_master_csv}...")

try:
    with open(gretil_master_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        original_fields = reader.fieldnames
        
        # Add 'DSBC' as the final column header
        new_fields = original_fields + ['DSBC']
        
        rows_to_write = []
        dsbc_flagged_count = 0
        
        for row in reader:
            xml_file = row.get('xml filename', '')
            
            # If this row's matched XML file was flagged as DSBC origin, mark it
            if xml_file in dsbc_xml_files:
                row['DSBC'] = 'y'
                dsbc_flagged_count += 1
            else:
                row['DSBC'] = ''
                
            rows_to_write.append(row)

    # Save out the structural changes to a clean master file
    with open(final_master_csv, mode='w', encoding='utf-8', newline='') as out_f:
        writer = csv.DictWriter(out_f, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows_to_write)
        
    print(f"Successfully processed master catalog. Saved to {final_master_csv}")

except FileNotFoundError:
    print(f"Error: Base file '{gretil_master_csv}' not found. Please run the matching script first.")
    exit()

# --- STEP 3: PROVENANCE AUDIT REPORT ---
print("\n" + "="*40)
print("          PROVENANCE REPORT           ")
print("="*40)
print(f"Total physical DSBC XMLs detected:    {len(dsbc_xml_files)}")
print(f"CSV Catalog rows successfully tagged: {dsbc_flagged_count}")

# Check for anomalies: XML files flagged as DSBC but missing from the catalog mapping entirely
unmapped_dsbc = sorted([f for f in dsbc_xml_files if not any(r['xml filename'] == f for r in rows_to_write)])
if unmapped_dsbc:
    print(f"\n[!] Note: Found {len(unmapped_dsbc)} physical DSBC files that did not match any entry in the CSV:")
    for item in unmapped_dsbc[:5]:
        print(f"  - {item}")
    if len(unmapped_dsbc) > 5:
        print(f"  ... and {len(unmapped_dsbc) - 5} more.")
else:
    print("\n✓ Perfect coverage: All identified DSBC files are mapped cleanly inside the master catalog.")
print("="*40)
