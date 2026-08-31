import csv
import sys
from pathlib import Path
from collections import defaultdict

def validate_corpus():
    base_dir = Path("..")
    log_file_path = base_dir / "filename_validation_log.txt"
    
    collections = [
        "dsbc",
        "gretil_extra",
        "gretil_sa",
        "hamburg",
        "muktabodha",
        "wikisource"
    ]

    # Global tracking for duplication logic
    all_csv_files = set()
    best_texts = set()
    duplicate_pointers = []
    duplicates_target = defaultdict(list)

    with open(log_file_path, "w", encoding="utf-8") as log:
        log.write("=== CORPUS FILE VALIDATION LOG ===\n\n")

        for collection in collections:
            csv_path = base_dir / "metadata" / f"{collection}.csv"
            corpus_path = base_dir / "corpus" / collection

            log.write(f"--- Validating Collection: {collection.upper()} ---\n")

            if not csv_path.exists():
                log.write(f"ERROR: CSV not found at {csv_path}\n\n")
                continue

            expected_in_corpus = set()
            actual_in_corpus = set()

            # 1. Parse CSV and build expected paths
            # using utf-8-sig safely handles potential BOMs at the start of the CSV
            with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                
                # Check if 'file' column exists to prevent KeyError
                if reader.fieldnames and 'file' not in reader.fieldnames:
                    log.write(f"ERROR: 'file' column missing in {collection}.csv. (Columns found: {reader.fieldnames})\n\n")
                    continue

                for row in reader:
                    filename = row.get("file", "").strip()
                    if not filename:
                        continue
                    
                    # Handle wikisource subfolders
                    if collection == "wikisource":
                        sub_folder = row.get("sub_folder", "").strip()
                        rel_path = f"{sub_folder}/{filename}" if sub_folder else filename
                    else:
                        rel_path = filename

                    expected_in_corpus.add(rel_path)
                    
                    # Register globally for phase 3 (format: collection/rel_path)
                    global_id = f"{collection}/{rel_path}"
                    all_csv_files.add(global_id)

                    # Extract duplication data
                    best_text = row.get("best_text", "").strip().lower()
                    dup_standard = row.get("duplicate_of_standard", "").strip()

                    if best_text == "y":
                        best_texts.add(global_id)
                    elif best_text == "n" and dup_standard:
                        duplicate_pointers.append((global_id, dup_standard))
                        duplicates_target[dup_standard].append(global_id)

            # 2. Parse Corpus Directory and build actual paths
            if corpus_path.exists():
                for file_path in corpus_path.rglob("*"):
                    if file_path.is_file():
                        # Extract relative path formatted with forward slashes
                        rel_p = file_path.relative_to(corpus_path).as_posix()
                        actual_in_corpus.add(rel_p)
            else:
                log.write(f"WARNING: Corpus directory not found at {corpus_path}\n")

            # 3. Two-way set comparisons
            missing_in_corpus = expected_in_corpus - actual_in_corpus
            missing_in_csv = actual_in_corpus - expected_in_corpus

            log.write(f"Files in CSV: {len(expected_in_corpus)}\n")
            log.write(f"Files in Dir: {len(actual_in_corpus)}\n")

            if not missing_in_corpus and not missing_in_csv:
                log.write("STATUS: Perfect Match.\n\n")
            else:
                if missing_in_corpus:
                    log.write(f"\n  [!] Missing in Corpus ({len(missing_in_corpus)}):\n")
                    for missing in sorted(missing_in_corpus):
                        log.write(f"      - {missing}\n")
                
                if missing_in_csv:
                    log.write(f"\n  [!] Missing in CSV ({len(missing_in_csv)}):\n")
                    for missing in sorted(missing_in_csv):
                        log.write(f"      - {missing}\n")
                log.write("\n")

        # 4. Global Duplication Cross-Referencing
        log.write("--- Validating Duplication Logic ---\n")
        dup_errors_found = False

        # Check: Does every 'best_text' have at least one duplicate pointing to it?
        for bt in sorted(best_texts):
            if bt not in duplicates_target or len(duplicates_target[bt]) == 0:
                log.write(f"[Warning] '{bt}' is marked as best_text='y' but no file points to it as a duplicate.\n")
                dup_errors_found = True

        # Check: Does every 'duplicate_of_standard' point to an actual file in our CSVs?
        for source, target in duplicate_pointers:
            if target not in all_csv_files:
                log.write(f"[Error] '{source}' points to a non-existent standard text: '{target}'\n")
                dup_errors_found = True
            elif target not in best_texts:
                log.write(f"[Warning] '{source}' points to '{target}', but '{target}' is not marked as best_text='y'.\n")
                dup_errors_found = True

        if not dup_errors_found:
            log.write("STATUS: Duplication logic is perfectly synced across all collections.\n")

    print(f"✅ Validation complete! Results saved to {log_file_path.resolve()}")

if __name__ == "__main__":
    validate_corpus()
