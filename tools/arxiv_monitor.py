import time
import requests
import feedparser
import os
from common import write_log, RAW_DIR, ARXIV_MAX_RESULTS
from datetime import datetime

def check_arxiv():
    print(f"Polling arXiv feeds for cs.AI, cs.CR (max {ARXIV_MAX_RESULTS})...")
    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query=cat:cs.AI+OR+cat:cs.CR"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={ARXIV_MAX_RESULTS}"
    )
    try:
        response = requests.get(url, timeout=10)
        feed = feedparser.parse(response.content)
        
        target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'arxiv')
        os.makedirs(target_dir, exist_ok=True)
        
        for entry in feed.entries:
            safe_title = "".join(c if c.isalnum() else "_" for c in entry.title)[:50]
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}_{safe_title}.md"
            target_path = os.path.join(target_dir, filename)
            
            if not os.path.exists(target_path):
                content = f"Title: {entry.title}\nURL: {entry.link}\nSummary: {entry.summary}\n"
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                write_log('monitor', 'arxiv_ingest', f"Fetched {filename}")
                print(f"Fetched new arXiv: {filename}")
            else:
                print(f"Already ingested: {filename}")
                
        write_log('monitor', 'arxiv', "Successfully polled latest arXiv feeds.")
    except Exception as e:
        write_log('monitor', 'arxiv_error', str(e))
        print(f"Failed to fetch arXiv: {e}")

if __name__ == '__main__':
    check_arxiv()
