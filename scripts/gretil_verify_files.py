import csv
import sys
from pathlib import Path

def audit_gretil_corpus():
    # 1. Establish paths relative to the ./scripts launch point
    base_dir = Path("..")
    csv_path = base_dir / "metadata" / "gretil_sa.csv"
    corpus_dir = base_dir / "corpus" / "gretil_sa"

    # Validate paths exist before proceeding
    if not csv_path.exists():
        print(f"Error: Cannot find CSV at {csv_path.resolve()}")
        sys.exit(1)
    if not corpus_dir.exists():
        print(f"Error: Cannot find directory at {corpus_dir.resolve()}")
        sys.exit(1)

    # 2. Extract filenames from CSV Column A (skipping row 1 header)
    csv_files = set()
    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        try:
            next(reader)  # Skip header row
        except StopIteration:
            print("Error: CSV appears to be empty.")
            sys.exit(1)
            
        for row in reader:
            if row:  # Ensure the row isn't blank
                csv_files.add(row[0].strip())

    # 3. Extract filenames currently in the corpus directory
    corpus_files = {f.name for f in corpus_dir.iterdir() if f.is_file()}

    # 4. Perform the two-way set difference
    missing_in_corpus = csv_files - corpus_files
    missing_in_csv = corpus_files - csv_files

    # 5. Output results
    print(f"=== GRETIL File Audit ===")
    print(f"Files in CSV:    {len(csv_files)}")
    print(f"Files in Corpus: {len(corpus_files)}\n")

    if not missing_in_corpus and not missing_in_csv:
        print("✅ Perfect match! Both the directory and the CSV are perfectly synced.")
        return

    if missing_in_corpus:
        print(f"⚠️ Listed in CSV but MISSING in corpus ({len(missing_in_corpus)}):")
        for f in sorted(missing_in_corpus):
            print(f"  - {f}")
        print()

    if missing_in_csv:
        print(f"⚠️ Present in corpus but MISSING in CSV ({len(missing_in_csv)}):")
        for f in sorted(missing_in_csv):
            print(f"  - {f}")

if __name__ == "__main__":
    audit_gretil_corpus()
