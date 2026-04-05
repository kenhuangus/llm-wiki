import requests
import os
from common import write_log, RAW_DIR, CVE_FEED_URL, CVE_MAX_RESULTS
from datetime import datetime

def check_cve():
    print(f"Polling CVE feed: {CVE_FEED_URL} (max {CVE_MAX_RESULTS})...")
    try:
        response = requests.get(CVE_FEED_URL, timeout=10)
        if response.status_code == 200:
            cves = response.json()[:CVE_MAX_RESULTS]
            
            target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'cve')
            os.makedirs(target_dir, exist_ok=True)
            
            for item in cves:
                cve_id = item.get("id", "UNKNOWN-CVE")
                date_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"{date_str}_{cve_id}.md"
                target_path = os.path.join(target_dir, filename)
                
                if not os.path.exists(target_path):
                    content = f"Title: {cve_id}\nCVSS: {item.get('cvss', 'None')}\nSummary: {item.get('summary', '')}\n"
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    write_log('monitor', 'cve_ingest', f"Fetched {filename}")
                    print(f"Fetched new CVE: {filename}")
                    
            write_log('monitor', 'cve', "Successfully polled latest CVEs.")
        else:
            print(f"Rate limited or unavailable: Status {response.status_code}")
    except Exception as e:
        write_log('monitor', 'cve_error', str(e))
        print(f"Failed to fetch CVEs: {e}")

if __name__ == '__main__':
    check_cve()
