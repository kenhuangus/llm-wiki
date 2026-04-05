import requests
import os
from common import write_log, RAW_DIR, GITHUB_TOKEN, GITHUB_REPOS
from datetime import datetime


def check_github():
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    for repo in GITHUB_REPOS:
        repo = repo.strip()
        if not repo:
            continue
        print(f"Polling GitHub releases: {repo}...")
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                release = response.json()
                tag_name = release.get("tag_name", "unknown")
                repo_slug = repo.replace("/", "_")

                target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'github')
                os.makedirs(target_dir, exist_ok=True)

                date_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"{date_str}_{repo_slug}_{tag_name}.md"
                target_path = os.path.join(target_dir, filename)

                if not os.path.exists(target_path):
                    body = release.get('body', '') or ''
                    content = (
                        f"Title: {repo} Release {tag_name}\n"
                        f"URL: {release.get('html_url', '')}\n"
                        f"Tag: {tag_name}\n"
                        f"Published: {release.get('published_at', '')}\n\n"
                        f"## Release Notes\n\n{body}\n"
                    )
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    write_log('monitor', 'github_ingest', f"Fetched {filename}")
                    print(f"  ✓ Fetched: {filename}")
                else:
                    print(f"  – Already ingested: {filename}")

            elif response.status_code == 404:
                print(f"  ! No releases found for {repo}")
            elif response.status_code == 403:
                print(f"  ! Rate limited for {repo}. Set GITHUB_TOKEN in .env to increase limits.")
            else:
                print(f"  ! Status {response.status_code} for {repo}")

            write_log('monitor', 'github', f"Polled releases for {repo}")
        except Exception as e:
            write_log('monitor', 'github_error', f"{repo} (releases): {e}")
            print(f"  ! Failed to fetch releases for {repo}: {e}")

        # Polling Security Advisories
        print(f"Polling GitHub Security Advisories: {repo}...")
        adv_url = f"https://api.github.com/repos/{repo}/security-advisories"
        try:
            adv_response = requests.get(adv_url, headers=headers, timeout=10)
            if adv_response.status_code == 200:
                advisories = adv_response.json()
                fetched_adv = 0
                for adv in advisories:
                    ghsa_id = adv.get('ghsa_id', 'unknown')
                    cve_id = adv.get('cve_id', '')
                    target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'github')
                    os.makedirs(target_dir, exist_ok=True)
                    
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    repo_slug = repo.replace("/", "_")
                    filename = f"{date_str}_{repo_slug}_GHSA_{ghsa_id}.md"
                    target_path = os.path.join(target_dir, filename)

                    if not os.path.exists(target_path):
                        content = (
                            f"Title: {repo} Security Advisory {ghsa_id}\n"
                            f"URL: {adv.get('html_url', '')}\n"
                            f"GHSA ID: {ghsa_id}\n"
                            f"CVE ID: {cve_id}\n"
                            f"Severity: {adv.get('severity', '')}\n"
                            f"Published: {adv.get('published_at', '')}\n\n"
                            f"## Summary\n\n{adv.get('summary', '')}\n\n"
                            f"## Description\n\n{adv.get('description', '')}\n"
                        )
                        with open(target_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        write_log('monitor', 'github_ingest', f"Fetched Advisory {ghsa_id} for {repo}")
                        print(f"  ✓ Fetched Advisory: {ghsa_id} ({adv.get('severity', '')})")
                        fetched_adv += 1
                if fetched_adv == 0:
                    print(f"  – No new advisories found for {repo}")
            elif adv_response.status_code == 404:
                print(f"  ! Advisories disabled or not visible for {repo}")
            else:
                print(f"  ! Status {adv_response.status_code} on advisories for {repo}")
            write_log('monitor', 'github', f"Polled advisories for {repo}")
        except Exception as e:
            write_log('monitor', 'github_error', f"{repo} (advisories): {e}")
            print(f"  ! Failed to fetch advisories for {repo}: {e}")


if __name__ == '__main__':
    check_github()
