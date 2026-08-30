import os

# Set target directory relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
TARGET_DIR = os.path.join(BASE_DIR, 'corpus', 'wikisource')

def clean_preamble(filepath):
    # Use utf-8-sig to handle any lingering Windows BOMs seamlessly
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    text_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == 'Text:':
            text_idx = i
            break

    if text_idx != -1:
        # Start keeping lines after "Text:"
        start_idx = text_idx + 1
        
        # If the immediate next line is empty, skip it as well
        if start_idx < len(lines) and lines[start_idx].strip() == '':
            start_idx += 1

        new_lines = lines[start_idx:]

        # Write the cleaned content back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    
    return False

def main():
    if not os.path.exists(TARGET_DIR):
        print(f"CRITICAL ERROR: Directory not found -> {TARGET_DIR}")
        return

    processed_count = 0
    skipped_count = 0

    # os.walk automatically traverses all subfolders
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            # Skip hidden files like .DS_Store
            if file.startswith('.'):
                continue
                
            filepath = os.path.join(root, file)
            if clean_preamble(filepath):
                print(f"Cleaned: {os.path.relpath(filepath, BASE_DIR)}")
                processed_count += 1
            else:
                skipped_count += 1

    print("\n--- Summary ---")
    print(f"Files cleaned: {processed_count}")
    print(f"Files skipped (no 'Text:' found): {skipped_count}")

if __name__ == "__main__":
    main()
