import xml.etree.ElementTree as ET
from pathlib import Path
import re

def get_stripped_tag(tag):
    """Removes the TEI namespace from the tag name for easier matching."""
    return tag.split('}')[-1] if '}' in tag else tag

def extract_node(node):
    """
    Recursively processes an XML node according to the gretil_tags.txt rules.
    """
    tag = get_stripped_tag(node.tag)
    text_out = ""
    
    # ---------------------------------------------------------
    # RULE SET 1: REMOVE (Ignore tag and all its contents)
    # ---------------------------------------------------------
    if tag in ['link', 'ref', 'gi', 'del']:
        pass 
        
    elif tag == 'note' and node.get('type') != 'commentary':
        pass 
        
    # ---------------------------------------------------------
    # RULE SET 2: REPLACE (Transform specific tags)
    # ---------------------------------------------------------
    elif tag == 'lb':
        text_out += "\n"
        
    elif tag == 'gap':
        text_out += "..."
        
    elif tag == 'app':
        lem_node = None
        rdg_nodes = []
        for child in node:
            ctag = get_stripped_tag(child.tag)
            if ctag == 'lem':
                lem_node = child
            elif ctag == 'rdg':
                rdg_nodes.append(child)
        
        if lem_node is not None:
            text_out += extract_inner_content(lem_node)
        elif rdg_nodes:
            text_out += extract_inner_content(rdg_nodes[0])
            
    elif tag == 'choice':
        reg_node = None
        for child in node:
            if get_stripped_tag(child.tag) == 'reg':
                reg_node = child
                break
                
        if reg_node is not None:
            text_out += extract_inner_content(reg_node)
        else:
            text_out += extract_inner_content(node)

    # ---------------------------------------------------------
    # RULE SET 3: KEEP (Extract content, remove the tag)
    # ---------------------------------------------------------
    else:
        text_out += extract_inner_content(node)
        
    if node.tail:
        text_out += node.tail
        
    return text_out

def extract_inner_content(node):
    """
    Helper function to extract the text inside a node and process its children.
    """
    content = ""
    if node.text:
        content += node.text
    for child in node:
        content += extract_node(child)
    return content

def convert_corpus(input_dir, output_dir):
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    xml_files = list(in_path.rglob('*.xml'))
    if not xml_files:
        print(f"No XML files found in {in_path.resolve()}")
        return

    print(f"Found {len(xml_files)} XML files. Processing according to rules...")
    success_count = 0

    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            body_elem = None
            for elem in root.iter():
                if get_stripped_tag(elem.tag) == 'body':
                    body_elem = elem
                    break

            if body_elem is not None:
                raw_text = extract_node(body_elem)
                
                # --- NEW TEXT CLEANUP BLOCK ---
                # 1. Collapse multiple spaces and tabs into a single space
                clean_text = re.sub(r'[ \t]+', ' ', raw_text)
                # 2. Remove leading spaces on newlines
                clean_text = re.sub(r'\n ', '\n', clean_text)
                # 3. Collapse 3 or more newlines (which creates 2+ empty lines) 
                # down to exactly 2 newlines (1 empty line). Includes handling of invisible spaces.
                clean_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', clean_text).strip()

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

    print(f"\nSuccess! Converted {success_count} files.")
    print(f"Output saved to: {out_path.resolve()}")

if __name__ == "__main__":
    input_directory = "corpus/gretil_sa"
    output_directory = "corpus_txt/gretil_sa"
    convert_corpus(input_directory, output_directory)
