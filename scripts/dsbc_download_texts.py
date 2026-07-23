import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def download_dsbc_texts(csv_file="src/dsbc/texts.csv", output_dir="src/dsbc/dsbc_texts_html"):
    # Create the main output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            books = list(reader)
    except FileNotFoundError:
        print(f"Error: Could not find '{csv_file}'. Run the extraction script first.")
        return

    # Use a session to reuse the underlying TCP connection (faster and more polite to the server)
    session = requests.Session()
    # Add a standard user-agent so the server doesn't block the automated request
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    for book in books:
        book_url = book['link']
        book_title = book['title']
        
        # Extract the book ID from the URL (e.g., '95' from '.../book/95')
        book_id = book_url.rstrip('/').split('/')[-1]
        
        print(f"\nProcessing [{book_id}] {book_title}...")
        
        try:
            # 1. Fetch the landing page
            response = session.get(book_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. Find all links that point to the content pages for this specific book
            content_links = []
            target_path = f"/canon-text/content/{book_id}/"
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if target_path in href:
                    # Handle both relative and absolute URLs safely
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"https://www.dsbcproject.org{href}"
                        
                    if full_url not in content_links:
                        content_links.append(full_url)
            
            if not content_links:
                print(f"  -> No content links found for {book_title}.")
                continue
                
            # Create a specific folder for this book to keep multi-page texts organized
            # We use the book ID to ensure folder names are valid and unique
            book_dir = os.path.join(output_dir, f"book_{book_id}")
            if not os.path.exists(book_dir):
                os.makedirs(book_dir)
            
            # 3. Download each content page
            for index, content_url in enumerate(content_links, start=1):
                # Extract the specific content ID from the end of the URL
                content_id = content_url.rstrip('/').split('/')[-1]
                
                # Save it as something like 01_756.html to maintain the reading order
                filename = f"{index:02d}_{content_id}.html"
                filepath = os.path.join(book_dir, filename)
                
                # Skip if we already downloaded it (useful if the script stops and you need to restart)
                if os.path.exists(filepath):
                    print(f"  -> Already exists: {filename}")
                    continue
                
                print(f"  -> Downloading part {index}/{len(content_links)}: {content_url}")
                content_response = session.get(content_url)
                content_response.raise_for_status()
                
                with open(filepath, 'w', encoding='utf-8') as out_file:
                    out_file.write(content_response.text)
                
                # Be polite to the server — wait a second between page requests
                time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"  -> Failed to access {book_url}: {e}")

    print("\nFinished processing all texts!")

if __name__ == "__main__":
    download_dsbc_texts()
