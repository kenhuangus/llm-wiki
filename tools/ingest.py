import sys
import os
from common import write_log, RAW_DIR
from datetime import datetime

def ingest_source(source_type, filepath):
    # Simulates moving a manually fetched source or polling an API
    filename = os.path.basename(filepath)
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    target_dir = os.path.join(RAW_DIR, 'auto_ingest', source_type)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, f"{date_str}_{filename}")
    
    # In real tool, we copy or download. Here we just create a mockup file
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(f"Raw source from {filepath}")
        
    write_log('ingest', source_type, f"Ingested {filename}")
    print(f"Ingested {source_type}: {filename}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python ingest.py [source_type(arxiv|cve|github|rss)] [filepath]")
        sys.exit(1)
    ingest_source(sys.argv[1], sys.argv[2])
