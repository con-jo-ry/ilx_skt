import html
import re
from pathlib import Path

# Directory path
CORPUS_DIR = Path("../corpus/muktabodha")

# Regex pattern matches HTML tags and comments without touching outer text
TAG_REGEX = re.compile(r"<!--.*?-->|<[^>]+>", flags=re.DOTALL)


def strip_html_tags(text: str) -> str:
    # 1. Remove all HTML comments and tags
    cleaned = TAG_REGEX.sub("", text)
    # 2. Unescape HTML character references (e.g. &nbsp; -> space, &amp; -> &)
    cleaned = html.unescape(cleaned)
    return cleaned


def process_files():
    if not CORPUS_DIR.exists() or not CORPUS_DIR.is_dir():
        print(f"Error: Directory '{CORPUS_DIR}' does not exist.")
        return

    htm_files = list(CORPUS_DIR.glob("*.htm"))

    if not htm_files:
        print(f"No .htm files found in {CORPUS_DIR}")
        return

    print(f"Found {len(htm_files)} .htm file(s) to process...")

    for file_path in htm_files:
        # Read the file (tries UTF-8 first, falls back to Latin-1/CP1252 if needed)
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1")

        # Strip tags and preserve text
        plain_text = strip_html_tags(content)

        # Target .xml filename
        new_file_path = file_path.with_suffix(".xml")

        # Write clean text to .xml
        new_file_path.write_text(plain_text, encoding="utf-8")

        # Remove the original .htm file
        file_path.unlink()

        print(f"Converted: {file_path.name} -> {new_file_path.name}")

    print("\nAll files processed successfully.")


if __name__ == "__main__":
    process_files()
