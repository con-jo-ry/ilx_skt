import re
import csv

def extract_dsbc_viewsource(input_file="src/dsbc/index.html", output_file="src/dsbc/texts.csv"):
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            html_content = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}'.")
        return

    # 1. Matches the actual book link
    # 2. Skips over the browser's injected clickable link logic: .*?</a>"&gt;</span>
    # 3. Grabs the title text that follows it: (.*?)
    # 4. Stops when it hits the closing tag: &lt;/a&gt;
    pattern = r'href="(https://www\.dsbcproject\.org/canon-text/book/\d+)"[^>]*>.*?</a>"&gt;</span>\s*(.*?)\s*(?:<span[^>]*>)?&lt;/a&gt;'
    
    matches = re.findall(pattern, html_content, flags=re.DOTALL)
    
    extracted_data = []
    seen_links = set()
    
    for link, raw_title in matches:
        if link not in seen_links:
            clean_title = raw_title.strip()
            
            if clean_title:
                extracted_data.append([link, clean_title])
                seen_links.add(link)

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['link', 'title'])
        writer.writerows(extracted_data)

    print(f"Success! Extracted {len(extracted_data)} unique texts and saved to {output_file}.")

if __name__ == "__main__":
    extract_dsbc_viewsource()
