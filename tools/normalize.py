import sys
import os
from common import write_log, RAW_DIR, get_hash, serialize_frontmatter
from datetime import datetime, timezone

def normalize_file(filepath, domain):
    filename = os.path.basename(filepath)
    content = ""
    
    # ── Binary PDF detection (pypdf) ──────────────────────────────────────────
    if filepath.lower().endswith('.pdf'):
        try:
            print(f"PIPELINE: Detected PDF source. Extracting text from {filename}...")
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            for page in reader.pages:
                content += page.extract_text() + "\n"
        except Exception as e:
            print(f"CRITICAL: Failed to extract PDF text: {e}")
            return # Skip if can't read
    else:
        # Standard text file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except: 
            print(f"CRITICAL: Failed to read text file {filename}")
            return

    if not content.strip():
        print(f"WARN: Empty content extracted from {filename}. Skipping.")
        return

    file_id = get_hash(content)
    target_dir = os.path.join(RAW_DIR, 'normalized', domain)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, f"{file_id}.md")
    
    metadata = {
        'id': file_id,
        'title': f"Normalized {filename}",
        'source_url': f"local://{filepath}",
        'source_type': 'doc',
        'domain': domain,
        'ingested_at': datetime.now(timezone.utc).isoformat(),
        'confidence': 0.8,
        'verified': False
    }
    
    normalized_content = serialize_frontmatter(metadata, content)
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(normalized_content)
        
    write_log('normalize', domain, f"Normalized {filename} -> {file_id}.md")
    print(f"Normalized: {target_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python normalize.py [filepath] [domain]")
        sys.exit(1)
    normalize_file(sys.argv[1], sys.argv[2])
