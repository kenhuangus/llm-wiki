import requests
import os
import json
from common import write_log, RAW_DIR, CVE_FEED_URL, CVE_MAX_RESULTS, NVD_API_KEY
from datetime import datetime, timedelta

def check_cve():
    print(f"Polling official NVD API: {CVE_FEED_URL} (max {CVE_MAX_RESULTS})...")
    
    headers = {}
    if NVD_API_KEY:
        headers["apiKey"] = NVD_API_KEY
        print("  Using NVD API Key (Higher rate limits unlocked).")
    else:
        print("  No NVD_API_KEY set. Rate limited to 5 req / 30s. Fetches may be delayed.")

    # Only fetch HIGH and CRITICAL vulnerabilities from the last 7 days to avoid noise
    pub_start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00.000")
    
    params = {
        "resultsPerPage": CVE_MAX_RESULTS,
        "cvssV3Severity": "HIGH",     # Targeting HIGH severity minimum
        "pubStartDate": pub_start_date
    }
    
    try:
        response = requests.get(CVE_FEED_URL, headers=headers, params=params, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            cves = data.get("vulnerabilities", [])
            
            target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'cve')
            os.makedirs(target_dir, exist_ok=True)
            
            fetched = 0
            for item in cves:
                cve_data = item.get("cve", {})
                cve_id = cve_data.get("id", "UNKNOWN-CVE")
                
                # Extract description
                descriptions = cve_data.get("descriptions", [])
                summary = next((d.get("value") for d in descriptions if d.get("lang") == "en"), "No English description available.")
                
                # Extract metrics
                metrics = cve_data.get("metrics", {})
                cvss_metrics = metrics.get("cvssMetricV31", metrics.get("cvssMetricV30", [{}]))[0]
                cvss_data = cvss_metrics.get("cvssData", {})
                base_score = cvss_data.get("baseScore", "Unknown")
                base_severity = cvss_data.get("baseSeverity", "Unknown")
                
                date_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"{date_str}_{cve_id}.md"
                target_path = os.path.join(target_dir, filename)
                
                if not os.path.exists(target_path):
                    content = (
                        f"Title: {cve_id}\n"
                        f"CVSS v3.x Base Score: {base_score} ({base_severity})\n"
                        f"Published: {cve_data.get('published', '')}\n\n"
                        f"## Description\n\n{summary}\n"
                    )
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    write_log('monitor', 'cve_ingest', f"Fetched {filename} (CVSS: {base_score})")
                    print(f"  ✓ Fetched new CVE: {filename} (CVSS: {base_score})")
                    fetched += 1
                else:
                    print(f"  - Already exists: {filename}")
                    
            write_log('monitor', 'cve', f"Successfully polled NVD. {fetched} new CVEs saved.")
            print(f"Done. {fetched} new CVE(s) saved.")
            
        elif response.status_code == 403:
            print(f"  ! NVD API Rate Limit or Auth Error (HTTP 403). Ensure NVD_API_KEY is valid.")
        else:
            print(f"  ! NVD API Error: Status {response.status_code} - {response.text[:100]}")
            
    except requests.exceptions.Timeout:
        write_log('monitor', 'cve_error', "NVD API timeout")
        print("  ! Failed to fetch CVEs: Connection timed out.")
    except Exception as e:
        write_log('monitor', 'cve_error', str(e))
        print(f"  ! Failed to fetch CVEs: {e}")

if __name__ == '__main__':
    check_cve()
