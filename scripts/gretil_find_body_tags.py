import xml.etree.ElementTree as ET
from pathlib import Path

def get_unique_body_tags(directory_path):
    folder = Path(directory_path)
    unique_tags = set()
    
    # Use rglob to catch XML files even if they are in subdirectories
    xml_files = list(folder.rglob('*.xml'))
    
    if not xml_files:
        print(f"No XML files found in {folder.resolve()}")
        return []

    print(f"Found {len(xml_files)} XML files. Scanning...")

    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Find the body tag. We check the end of the string to ignore namespaces.
            body_elem = None
            for elem in root.iter():
                if elem.tag.endswith('body'):
                    body_elem = elem
                    break

            # If a body is found, iterate through all its descendants
            if body_elem is not None:
                for elem in body_elem.iter():
                    # Strip the namespace (everything before and including '}')
                    clean_tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                    unique_tags.add(clean_tag)
                    
        except ET.ParseError as e:
            print(f"XML parsing error in {xml_file.name}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {xml_file.name}: {e}")

    return sorted(list(unique_tags))

if __name__ == "__main__":
    # Point this to your GRETIL directory
    target_directory = "corpus/gretil_sa"
    
    tags = get_unique_body_tags(target_directory)
    
    if tags:
        print("\nUnique tags found within <body> sections:")
        for tag in tags:
            print(f"<{tag}>")
