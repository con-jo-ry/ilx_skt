# This script will (1) produce a csv file with a list of filenames in gretil_sa folder and their corresponding ".htm" references; (2) update gretil.csv to include columns for those file names, matched with the Buddha Nexus data where possible; (3) output some data on which files are missing / added in both dataets

import os
import csv
import re
import xml.etree.ElementTree as ET

# Define paths
xml_dir = 'gretil_sa'
gretil_filename_csv = 'gretil_filename.csv'
gretil_master_csv = 'gretil.csv'
updated_master_csv = 'gretil_updated.csv'

# --- STEP 1: PARSE XML FILES AND EXTRACT HTM FILENAMES ---
print("Scanning XML files in 'gretil_sa'...")
xml_data = {}  # Map: htm_filename -> xml_filename

if not os.path.exists(xml_dir):
    print(f"Error: Directory '{xml_dir}' not found.")
    exit()

# TEI files often use namespaces.
namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}

for filename in os.listdir(xml_dir):
    if filename.endswith('.xml'):
        file_path = os.path.join(xml_dir, filename)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Find <ref> inside <notesStmt>
            ref_element = None
            for elem in root.findall('.//tei:notesStmt/tei:note/tei:ref', namespaces):
                ref_element = elem
                break
            if ref_element is None:
                for elem in root.findall('.//notesStmt/note/ref'):
                    ref_element = elem
                    break
                    
            if ref_element is not None and ref_element.text:
                htm_text = ref_element.text.strip()
                if htm_text.endswith('.htm'):
                    xml_data[htm_text.lower()] = filename
        except Exception as e:
            print(f"Warning: Could not parse {filename}. Error: {e}")

# Save the extracted XML mapping to gretil_filename.csv
with open(gretil_filename_csv, mode='w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['xml filename', 'htm filename'])
    for htm, xml in sorted(xml_data.items()):
        writer.writerow([xml, htm])

print(f"Created {gretil_filename_csv} with {len(xml_data)} entries.")

# --- STEP 2: UPDATE GRETIL.CSV AND TRACK ENCOUNTERED XMLs ---
print(f"Updating {gretil_master_csv} and identifying orphaned files...")

matched_xml_counts = {}  # Track how many times an XML file gets mapped to an existing row
csv_htm_set = set()      # Track unique HTM targets identified inside the original CSV
rows_to_write = []
original_fields = []

try:
    with open(gretil_master_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        original_fields = reader.fieldnames
        new_fields = ['xml filename', 'htm filename'] + original_fields
        
        for row in reader:
            # Strategy A: Extract from URL link
            link = row.get('GRETIL/DSBC Link', '')
            htm_target = ""
            
            if link and '/' in link:
                potential_htm = link.split('/')[-1].strip().lower()
                if potential_htm.endswith('.htm'):
                    htm_target = potential_htm
            
            # Strategy B Fallback: Extract from Sanskrit Filename
            if not htm_target:
                skr_file = row.get('Sanskrit Filename', '')
                cleaned = re.sub(r'^[A-Z]\d+', '', skr_file).strip().lower()
                if cleaned:
                    htm_target = f"{cleaned}.htm"
            
            # Map back to discovered XML
            xml_match = ""
            if htm_target in xml_data:
                xml_match = xml_data[htm_target]
                matched_xml_counts[xml_match] = matched_xml_counts.get(xml_match, 0) + 1
            
            if htm_target:
                csv_htm_set.add(htm_target)
                
            # Build the updated row
            new_row = {'xml filename': xml_match, 'htm filename': htm_target}
            new_row.update(row)
            rows_to_write.append(new_row)

except FileNotFoundError:
    print(f"Error: Base file '{gretil_master_csv}' not found.")
    exit()

# --- STEP 3: APPEND EXTRA FILES TO THE BOTTOM ---
all_xml_htms = set(xml_data.keys())
# Find htm targets present in the XML folder but completely missing from the CSV mappings
added_htms = sorted([h for h in all_xml_htms if xml_data[h] not in matched_xml_counts])

print(f"Found {len(added_htms)} extra XML files not listed in the CSV. Appending them...")

for htm in added_htms:
    xml_file = xml_data[htm]
    # Initialize a row with blank metadata fields
    appended_row = {field: "" for field in new_fields}
    appended_row['xml filename'] = xml_file
    appended_row['htm filename'] = htm
    
    rows_to_write.append(appended_row)

# --- STEP 4: SAVE THE COMBINED DATA ---
with open(updated_master_csv, mode='w', encoding='utf-8', newline='') as out_f:
    writer = csv.DictWriter(out_f, fieldnames=new_fields)
    writer.writeheader()
    writer.writerows(rows_to_write)
    
print(f"Successfully compiled all data. Saved to {updated_master_csv}")

# --- STEP 5: AUDIT REPORT ---
missing_in_xml_folder = sorted([h for h in csv_htm_set if h not in all_xml_htms])

print("\n" + "="*40)
print("             AUDIT REPORT             ")
print("="*40)
print(f"Total physical XML files found:       {len(xml_data)}")
print(f"Original unique HTM rows processed:   {len(rows_to_write) - len(added_htms)}")
print(f"Extra XML rows appended to bottom:    {len(added_htms)}")
print(f"Total rows in new CSV catalog:        {len(rows_to_write)}")
print("-"*40)

print(f"\n[!] IN CSV BUT MISSING IN LOCAL FOLDER ({len(missing_in_xml_folder)} text references):")
if missing_in_xml_folder:
    for item in missing_in_xml_folder[:10]:
        print(f"  - {item}")
    if len(missing_in_xml_folder) > 10:
        print(f"  ... and {len(missing_in_xml_folder) - 10} more.")
else:
    print("  None! Every original CSV row successfully pointed to a real XML file.")

print(f"\n[+] APPENDED ROWS FROM DIRECTORY ({len(added_htms)} text files):")
if added_htms:
    for item in added_htms[:10]:
        print(f"  - {xml_data[item]} ({item})")
    if len(added_htms) > 10:
        print(f"  ... and {len(added_htms) - 10} more files appended.")
else:
    print("  None! No extra XML files were discovered in the directory.")
print("="*40)
