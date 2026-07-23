import os
import glob
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup, Comment

def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def load_book_titles(csv_file="src/dsbc/texts.csv"):
    """Reads the CSV file and returns a dictionary mapping book directory names to their titles."""
    titles = {}
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract the ID from the URL (e.g., '800' from '.../book/800')
                book_id = row['link'].rstrip('/').split('/')[-1]
                titles[f"book_{book_id}"] = row['title']
    except FileNotFoundError:
        print(f"Warning: Could not find '{csv_file}'. Titles will default to 'Unknown Title'.")
    return titles

def extract_metadata(soup):
    """Extracts the technical details from the TEI header based on the dsbc structure."""
    metadata = {}
    
    times_list = soup.find('ul', class_='times')
    if times_list:
        for li in times_list.find_all('li'):
            week_span = li.find('span', class_='week')
            hours_div = li.find('div', class_='hours')
            
            if week_span and hours_div:
                key = week_span.get_text(strip=True).replace(':', '').strip()
                val = hours_div.get_text(strip=True)
                metadata[key] = val
                
    title_tag = soup.find('h3', class_='abour')
    if title_tag:
        metadata['Chapter_Title'] = title_tag.get_text(strip=True)
        
    return metadata

def extract_core_text(soup):
    """Extracts text handling both raw strings (older HTML) and <p> tags (newer HTML)."""
    news_section = soup.find('div', class_='news-section')
    if not news_section:
        return ""

    extracted_text = ""
    capture = False
    
    for child in news_section.children:
        if isinstance(child, Comment) and 'end of title information' in child:
            capture = True
            continue
            
        if capture:
            if isinstance(child, str):
                text = child.strip()
                if text:
                    # Append raw text with a trailing space
                    extracted_text += text + " "
            elif child.name == 'br':
                extracted_text += "\n"
            elif child.name:
                # Extract text from inside the tag
                text = child.get_text(separator=' ', strip=True)
                if text:
                    extracted_text += text
                    # Add a line break after block-level elements
                    if child.name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
                        extracted_text += "\n"
                    else:
                        extracted_text += " " # Inline tags (like <span>) just get a space
                elif child.find('br'): 
                    # Handle empty tags that just contain a break, e.g., <p><br></p>
                    extracted_text += "\n"
                    
    # Clean up the text: strip leading/trailing whitespace on EVERY individual line
    cleaned_lines = [line.strip() for line in extracted_text.split('\n')]
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Condense multiple line breaks down to double line breaks for clean paragraphs
    while '\n\n\n' in cleaned_text:
        cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
        
    return cleaned_text.strip()

def build_tei_header(tei_root, metadata, book_title, book_url):
    """Constructs the <teiHeader> based on extracted metadata and URL."""
    tei_header = ET.SubElement(tei_root, 'teiHeader')
    file_desc = ET.SubElement(tei_header, 'fileDesc')
    
    title_stmt = ET.SubElement(file_desc, 'titleStmt')
    title = ET.SubElement(title_stmt, 'title')
    title.text = book_title
    
    if 'Input Personnel' in metadata:
        resp_stmt = ET.SubElement(title_stmt, 'respStmt')
        resp = ET.SubElement(resp_stmt, 'resp')
        resp.text = 'Input Personnel'
        name = ET.SubElement(resp_stmt, 'name')
        name.text = metadata['Input Personnel']
        
    if 'Proof Reader' in metadata:
        resp_stmt2 = ET.SubElement(title_stmt, 'respStmt')
        resp2 = ET.SubElement(resp_stmt2, 'resp')
        resp2.text = 'Proof Reader'
        name2 = ET.SubElement(resp_stmt2, 'name')
        name2.text = metadata['Proof Reader']

    pub_stmt = ET.SubElement(file_desc, 'publicationStmt')
    if 'Supplier' in metadata:
        publisher = ET.SubElement(pub_stmt, 'publisher')
        publisher.text = metadata['Supplier']
    if 'Input Date' in metadata:
        date = ET.SubElement(pub_stmt, 'date')
        date.text = metadata['Input Date']
    if 'Sponsor' in metadata:
        sponsor = ET.SubElement(pub_stmt, 'sponsor')
        sponsor.text = metadata['Sponsor']

    # Add Source Description including the URL
    source_desc = ET.SubElement(file_desc, 'sourceDesc')
    
    p_version = ET.SubElement(source_desc, 'p')
    p_version.text = f"Text Version: {metadata.get('Text Version', 'Unknown')}"
    
    p_url = ET.SubElement(source_desc, 'p')
    p_url.text = f"{book_url}"

def process_books(input_dir="src/dsbc/dsbc_texts_html", output_dir="corpus/dsbc", csv_file="src/dsbc/texts.csv"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    book_titles = load_book_titles(csv_file)
    book_dirs = glob.glob(os.path.join(input_dir, "book_*"))
    
    for book_dir in book_dirs:
        book_name = os.path.basename(book_dir)
        html_files = sorted(glob.glob(os.path.join(book_dir, "*.html")))
        
        if not html_files:
            continue
            
        main_title = book_titles.get(book_name, 'Unknown Title')
        
        # Reconstruct the base URL using the book ID
        book_id = book_name.replace("book_", "")
        book_url = f"https://www.dsbcproject.org/canon-text/book/{book_id}"
        
        print(f"Processing {book_name}: {main_title} ({len(html_files)} chapters)...")
        
        tei_root = ET.Element('TEI', xmlns="http://www.tei-c.org/ns/1.0")

        with open(html_files[0], 'r', encoding='utf-8') as f:
            first_soup = BeautifulSoup(f, 'html.parser')
            book_metadata = extract_metadata(first_soup)
            build_tei_header(tei_root, book_metadata, main_title, book_url)

        text_elem = ET.SubElement(tei_root, 'text')
        body_elem = ET.SubElement(text_elem, 'body')

        for html_file in html_files:
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                
                chapter_meta = extract_metadata(soup)
                chapter_text = extract_core_text(soup)
                
                div_elem = ET.SubElement(body_elem, 'div')
                
                head_elem = ET.SubElement(div_elem, 'head')
                head_elem.text = chapter_meta.get('Chapter_Title', 'Untitled Chapter')
                
                p_elem = ET.SubElement(div_elem, 'p')
                p_elem.text = chapter_text

        output_filepath = os.path.join(output_dir, f"{book_name}.xml")
        with open(output_filepath, 'w', encoding='utf-8') as out_f:
            pretty_xml = prettify_xml(tei_root)
            out_f.write(pretty_xml)
            
    print("Success! TEI XML generation complete.")

if __name__ == "__main__":
    process_books()
