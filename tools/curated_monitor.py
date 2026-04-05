import sys
import os
import re
from datetime import datetime
from duckduckgo_search import DDGS
from common import WIKI_DIR, RAW_DIR, write_log

def get_curated_sources():
    """Parse the markdown table from curated-sources.md to get topics."""
    filepath = os.path.join(WIKI_DIR, 'synthesis', 'curated-sources.md')
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return []
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    sources = []
    # Match the table rows (skip header and separator)
    in_table = False
    for line in content.split('\n'):
        if line.startswith('|') and '---' not in line and 'Rank' not in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                source_name = parts[2]  # Index 2 is the 'Source' column
                if source_name:
                    sources.append(source_name)
    return sources

def check_curated_sources():
    sources = get_curated_sources()
    if not sources:
        print("No curated sources found to monitor.")
        return

    print(f"Checking {len(sources)} curated sources for recent updates...")
    target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'curated')
    os.makedirs(target_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    fetched = 0
    
    with DDGS() as ddgs:
        for source in sources:
            print(f"  Searching recent news for: {source}...")
            
            # Use DuckDuckGo News search for latest updates
            try:
                results = list(ddgs.news(keywords=source, max_results=2))
                for res in results:
                    # Create a safe filename
                    safe_title = "".join(c if c.isalnum() else "_" for c in res.get('title', ''))[:40]
                    safe_source = "".join(c if c.isalnum() else "_" for c in source)[:20]
                    filename = f"{date_str}_{safe_source}_{safe_title}.md"
                    target_path = os.path.join(target_dir, filename)
                    
                    if not os.path.exists(target_path):
                        content = (
                            f"Title: {res.get('title')}\n"
                            f"Source URL: {res.get('url')}\n"
                            f"Date: {res.get('date')}\n"
                            f"Curated Topic: {source}\n"
                            f"Publisher: {res.get('source')}\n\n"
                            f"## Summary\n\n{res.get('body')}\n"
                        )
                        with open(target_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        write_log('monitor', 'curated_ingest', f"Found update for {source}: {safe_title}")
                        print(f"    ✓ Fetched update: {res.get('title')[:60]}...")
                        fetched += 1
            except Exception as e:
                write_log('monitor', 'curated_error', f"{source}: {e}")
                print(f"    ! Search failed for '{source}': {e}")
                
    write_log('monitor', 'curated', f"Weekly poll complete. {fetched} updates saved.")
    print(f"Done. {fetched} curated updates saved.")

if __name__ == "__main__":
    check_curated_sources()
