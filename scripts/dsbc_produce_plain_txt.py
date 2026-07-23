import xml.etree.ElementTree as ET
from pathlib import Path
import re

def get_stripped_tag(tag):
    """Removes the TEI namespace from the tag name for easier matching."""
    return tag.split('}')[-1] if '}' in tag else tag

def process_dsbc_corpus(input_dir, output_dir):
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    out_path.mkdir(parents=True, exist_ok=True)

    xml_files = list(in_path.rglob('*.xml'))
    if not xml_files:
        print(f"No XML files found in {in_path.resolve()}")
        return

    print(f"Found {len(xml_files)} XML files in DSBC corpus. Extracting text...")
    success_count = 0

    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # 1. Grab the main title from the TEI Header
            title_text = ""
            for elem in root.iter():
                if get_stripped_tag(elem.tag) == 'title':
                    title_text = "".join(elem.itertext()).strip()
                    break # Just grab the first title found

            # 2. Isolate the body section
            body_elem = None
            for elem in root.iter():
                if get_stripped_tag(elem.tag) == 'body':
                    body_elem = elem
                    break

            if body_elem is not None:
                # Extract all text recursively from the body
                raw_text = "".join(body_elem.itertext())
                
                # --- TEXT CLEANUP ---
                # Collapse multiple spaces and tabs into a single space
                clean_text = re.sub(r'[ \t]+', ' ', raw_text)
                # Remove leading spaces on newlines
                clean_text = re.sub(r'\n ', '\n', clean_text)
                
                # --- REMOVE TITLE ---
                # If a title was found in the header, erase it from the body text
                if title_text:
                    # Clean up the title string to ensure a match
                    clean_title = re.sub(r'\s+', ' ', title_text).strip()
                    # Remove exact string matches
                    clean_text = clean_text.replace(clean_title, "")

                # Collapse 3 or more newlines down to exactly 2 newlines (1 empty line max)
                clean_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', clean_text).strip()

                # Recreate folder structure in the output directory
                relative_path = xml_file.relative_to(in_path)
                output_file = out_path / relative_path.with_suffix('.txt')
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(clean_text)
                
                success_count += 1
            else:
                print(f"Skipping {xml_file.name}: No <body> tag found.")

        except ET.ParseError as e:
            print(f"XML parsing error in {xml_file.name}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {xml_file.name}: {e}")

    print(f"\nSuccess! Extracted plain text from {success_count} files.")
    print(f"Output saved to: {out_path.resolve()}")

if __name__ == "__main__":
    # Pointing to the parent directory since script runs in "scripts"
    base_dir = Path("..")
    
    input_directory = base_dir / "corpus/dsbc"
    output_directory = base_dir / "corpus_txt/dsbc"
    
    process_dsbc_corpus(input_directory, output_directory)
