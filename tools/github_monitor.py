import requests
import os
from common import write_log, RAW_DIR, GITHUB_TOKEN
from datetime import datetime

def check_github():
    print("Polling target GitHub repos (langchain-ai/langchain)...")
    url = "https://api.github.com/repos/langchain-ai/langchain/releases/latest"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            release = response.json()
            tag_name = release.get("tag_name", "unknown")
            
            target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'github')
            os.makedirs(target_dir, exist_ok=True)
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}_langchain_{tag_name}.md"
            target_path = os.path.join(target_dir, filename)
            
            if not os.path.exists(target_path):
                content = f"Title: LangChain Release {tag_name}\nURL: {release.get('html_url')}\nBody: {release.get('body', '')[:500]}...\n"
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                write_log('monitor', 'github_ingest', f"Fetched {filename}")
                print(f"Fetched new GitHub release: {filename}")
            else:
                print(f"Already ingested: {filename}")
                
        write_log('monitor', 'github', "Successfully polled GitHub releases.")
    except Exception as e:
        write_log('monitor', 'github_error', str(e))
        print(f"Failed to fetch GitHub: {e}")

if __name__ == '__main__':
    check_github()
