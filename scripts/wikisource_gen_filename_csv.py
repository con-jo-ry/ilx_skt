import csv
from pathlib import Path
import os

def extract_wikisource_files():
    # Setup paths relative to this script's location
    # Assumes script is in `project_main/scripts/`
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    wikisource_dir = project_root / 'corpus' / 'wikisource'
    output_csv = project_root / 'wikisource.csv'
    
    if not wikisource_dir.exists():
        print(f"Error: Directory not found at {wikisource_dir}")
        return

    data = []
    # Traverse the wikisource directory
    for root, _, files in os.walk(wikisource_dir):
        root_path = Path(root)
        for file_name in files:
            if file_name.startswith('.'):
                continue # Skip hidden files like .DS_Store
            
            # Get the subfolder name relative to wikisource_dir
            rel_path = root_path.relative_to(wikisource_dir)
            sub_folder = str(rel_path) if str(rel_path) != '.' else ''
            
            data.append([sub_folder, file_name])
            
    # Sort data by sub_folder then filename for clean output
    data.sort(key=lambda x: (x[0], x[1]))

    # Write to CSV
    with open(output_csv, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        # Adding two header rows to match the convention of your other CSVs
        writer.writerow(['sub_folder', 'xml_filename'])
        writer.writerow(['', ''])
        writer.writerows(data)
        
    print(f"Successfully extracted {len(data)} file records to {output_csv}")

if __name__ == '__main__':
    extract_wikisource_files()
