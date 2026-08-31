import csv
import sys
from pathlib import Path
from bs4 import BeautifulSoup

def enrich_metadata():
    base_dir = Path("..")
    input_csv_path = base_dir / "metadata" / "gretil_sa.csv"
    output_csv_path = base_dir / "metadata" / "gretil_sa_enriched.csv"
    corpus_dir = base_dir / "corpus" / "gretil_sa"

    if not input_csv_path.exists():
        print(f"Error: Cannot find CSV at {input_csv_path.resolve()}")
        sys.exit(1)

    with open(input_csv_path, mode="r", encoding="utf-8") as infile, \
         open(output_csv_path, mode="w", encoding="utf-8", newline="") as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        try:
            headers = next(reader)
        except StopIteration:
            print("Error: Input CSV is empty.")
            sys.exit(1)

        new_columns = ["tei_title", "tei_author", "legacy_url", "category", "standard_url"]
        writer.writerow(headers + new_columns)

        processed_count = 0

        for row in reader:
            if not row or not row[0].strip(): 
                continue
            
            fil_xml = row[0].strip()
            xml_path = corpus_dir / fil_xml
            
            tei_title = ""
            tei_author = ""
            legacy_url = ""
            category = ""
            
            htm_filename = fil_xml.replace(".xml", ".htm")
            standard_url = f"http://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/html/{htm_filename}"

            if xml_path.is_file():
                with open(xml_path, mode="r", encoding="utf-8") as xml_file:
                    soup = BeautifulSoup(xml_file, "xml")
                    
                    # Extract Title and Author
                    title_stmt = soup.find("titleStmt")
                    if title_stmt:
                        title_tag = title_stmt.find("title")
                        if title_tag: 
                            tei_title = title_tag.get_text(strip=True)
                        
                        author_tags = title_stmt.find_all("author")
                        authors = [a.get_text(strip=True) for a in author_tags if a.get_text(strip=True)]
                        tei_author = "; ".join(authors)

                    # Extract legacy URL and parse Category from attributes
                    notes_stmt = soup.find("notesStmt")
                    if notes_stmt:
                        ref_tag = notes_stmt.find("ref")
                        if ref_tag and ref_tag.has_attr("target"):
                            extracted_url = ref_tag["target"].strip()
                            
                            if "gretil.sub.uni-goettingen.de" in extracted_url:
                                legacy_url = extracted_url
                                
                                # Isolate the category string
                                if "1_sanskr/" in legacy_url:
                                    # Split the URL and keep everything after '1_sanskr/'
                                    tail = legacy_url.split("1_sanskr/")[1]
                                    # Split by '/' to separate folders from the filename
                                    path_parts = tail.split('/')
                                    # Rejoin all parts except the very last one (the filename)
                                    if len(path_parts) > 1:
                                        category = "/".join(path_parts[:-1])

            else:
                print(f"Warning: '{fil_xml}' is not a valid file, skipping XML extraction.")

            row.extend([tei_title, tei_author, legacy_url, category, standard_url])
            writer.writerow(row)
            processed_count += 1

    print(f"✅ Extraction complete! Processed {processed_count} files.")
    print(f"New CSV saved to: {output_csv_path.resolve()}")

if __name__ == "__main__":
    enrich_metadata()
