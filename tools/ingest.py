import sys
import os
import shutil
import urllib.request
from common import write_log, RAW_DIR
from datetime import datetime


def ingest_source(source_type, source):
    """
    Ingest a source into raw/auto_ingest/<source_type>/.

    `source` can be:
      - a local file path  → copied verbatim
      - an http/https URL  → downloaded to the target directory
    """
    date_str = datetime.now().strftime("%Y-%m-%d")

    target_dir = os.path.join(RAW_DIR, 'auto_ingest', source_type)
    os.makedirs(target_dir, exist_ok=True)

    if source.startswith("http://") or source.startswith("https://"):
        # Download from URL
        filename = source.split("/")[-1].split("?")[0] or "download"
        if not filename.endswith(".md"):
            filename += ".md"
        target_path = os.path.join(target_dir, f"{date_str}_{filename}")
        if os.path.exists(target_path):
            print(f"Already ingested (URL): {filename}")
            return
        try:
            urllib.request.urlretrieve(source, target_path)
            write_log('ingest', source_type, f"Downloaded {filename} from {source}")
            print(f"Downloaded {source_type}: {filename}")
        except Exception as e:
            write_log('ingest', f"{source_type}_error", str(e))
            print(f"Failed to download {source}: {e}")
    else:
        # Local file — copy it (never move/modify the original)
        if not os.path.exists(source):
            print(f"Error: file not found: {source}")
            sys.exit(1)
        filename = os.path.basename(source)
        target_path = os.path.join(target_dir, f"{date_str}_{filename}")
        if os.path.exists(target_path):
            print(f"Already ingested (file): {filename}")
            return
        shutil.copy2(source, target_path)
        write_log('ingest', source_type, f"Copied {filename}")
        print(f"Ingested {source_type}: {filename}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python ingest.py [source_type] [filepath_or_url]")
        print("  source_type: arxiv | cve | github | rss | manual")
        sys.exit(1)
    ingest_source(sys.argv[1], sys.argv[2])
