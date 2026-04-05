"""
github_monitor.py — Poll GitHub releases, security advisories, and Dependabot alerts.

Improvements (Phase 2):
  - ETag / Last-Modified state file to avoid re-fetching unchanged releases
  - Dependabot alerts polling per repo
"""
import requests
import os
import json
from common import write_log, RAW_DIR, WIKI_ROOT, GITHUB_TOKEN, GITHUB_REPOS, is_already_ingested, mark_ingested
from datetime import datetime


_ETAG_FILE = os.path.join(WIKI_ROOT, 'state_github_etags.json')


def _load_etags() -> dict:
    if os.path.exists(_ETAG_FILE):
        try:
            with open(_ETAG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_etags(etags: dict):
    with open(_ETAG_FILE, 'w') as f:
        json.dump(etags, f, indent=2)


def _base_headers() -> dict:
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def _poll_releases(repo: str, etags: dict):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = _base_headers()
    etag_key = f"release:{repo}"
    if etag_key in etags:
        headers["If-None-Match"] = etags[etag_key]

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 304:
            print(f"  – No new release (304 Not Modified): {repo}")
            return

        if response.status_code == 200:
            # Store new ETag for next run
            if "ETag" in response.headers:
                etags[etag_key] = response.headers["ETag"]

            release = response.json()
            tag_name = release.get("tag_name", "unknown")
            repo_slug = repo.replace("/", "_")

            target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'github')
            os.makedirs(target_dir, exist_ok=True)

            item_id = f"{repo}@{tag_name}"
            if is_already_ingested("github_release", item_id):
                print(f"  – Already ingested (DB): {item_id}")
                return

            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}_{repo_slug}_{tag_name}.md"
            target_path = os.path.join(target_dir, filename)

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

            mark_ingested("github_release", item_id)
            write_log('monitor', 'github_ingest', f"Fetched {filename}")
            print(f"  ✓ Release: {filename}")

        elif response.status_code == 404:
            print(f"  ! No releases found for {repo}")
        elif response.status_code == 403:
            print(f"  ! Rate limited for {repo}. Set GITHUB_TOKEN in .env.")
        else:
            print(f"  ! Status {response.status_code} for {repo}")

    except Exception as e:
        write_log('monitor', 'github_error', f"{repo} (releases): {e}")
        print(f"  ! Failed releases for {repo}: {e}")


def _poll_advisories(repo: str):
    url = f"https://api.github.com/repos/{repo}/security-advisories"
    try:
        response = requests.get(url, headers=_base_headers(), timeout=10)
        if response.status_code == 200:
            advisories = response.json()
            fetched = 0
            for adv in advisories:
                ghsa_id = adv.get('ghsa_id', 'unknown')
                if is_already_ingested("github_advisory", ghsa_id):
                    continue

                target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'github')
                os.makedirs(target_dir, exist_ok=True)
                date_str = datetime.now().strftime("%Y-%m-%d")
                repo_slug = repo.replace("/", "_")
                filename = f"{date_str}_{repo_slug}_GHSA_{ghsa_id}.md"
                target_path = os.path.join(target_dir, filename)

                content = (
                    f"Title: {repo} Security Advisory {ghsa_id}\n"
                    f"URL: {adv.get('html_url', '')}\n"
                    f"GHSA ID: {ghsa_id}\n"
                    f"CVE ID: {adv.get('cve_id', '')}\n"
                    f"Severity: {adv.get('severity', '')}\n"
                    f"Published: {adv.get('published_at', '')}\n\n"
                    f"## Summary\n\n{adv.get('summary', '')}\n\n"
                    f"## Description\n\n{adv.get('description', '')}\n"
                )
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                mark_ingested("github_advisory", ghsa_id)
                write_log('monitor', 'github_ingest', f"Fetched Advisory {ghsa_id} for {repo}")
                print(f"  ✓ Advisory: {ghsa_id} ({adv.get('severity', '')})")
                fetched += 1

            if fetched == 0:
                print(f"  – No new advisories for {repo}")
        elif response.status_code == 404:
            print(f"  ! Advisories not visible for {repo}")
        else:
            print(f"  ! Status {response.status_code} on advisories for {repo}")
    except Exception as e:
        write_log('monitor', 'github_error', f"{repo} (advisories): {e}")
        print(f"  ! Failed advisories for {repo}: {e}")


def _poll_dependabot(repo: str):
    """Poll Dependabot alerts — requires GITHUB_TOKEN with security_events scope."""
    if not GITHUB_TOKEN:
        return  # Dependabot requires auth
    url = f"https://api.github.com/repos/{repo}/dependabot/alerts"
    try:
        response = requests.get(
            url, headers=_base_headers(),
            params={"state": "open", "per_page": 10},
            timeout=10
        )
        if response.status_code == 200:
            alerts = response.json()
            fetched = 0
            for alert in alerts:
                alert_num = str(alert.get("number", "unknown"))
                item_id = f"{repo}#dependabot-{alert_num}"
                if is_already_ingested("github_dependabot", item_id):
                    continue

                target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'github')
                os.makedirs(target_dir, exist_ok=True)
                date_str = datetime.now().strftime("%Y-%m-%d")
                repo_slug = repo.replace("/", "_")
                filename = f"{date_str}_{repo_slug}_dependabot_{alert_num}.md"
                target_path = os.path.join(target_dir, filename)

                advisory = alert.get("security_advisory", {})
                vuln = alert.get("security_vulnerability", {})
                content = (
                    f"Title: Dependabot Alert #{alert_num} — {repo}\n"
                    f"URL: {alert.get('html_url', '')}\n"
                    f"Package: {vuln.get('package', {}).get('name', 'unknown')}\n"
                    f"Severity: {advisory.get('severity', 'unknown')}\n"
                    f"CVE: {advisory.get('cve_id', '')}\n"
                    f"Vulnerable Range: {vuln.get('vulnerable_version_range', '')}\n"
                    f"Fixed In: {vuln.get('first_patched_version', {}).get('identifier', 'N/A')}\n\n"
                    f"## Summary\n\n{advisory.get('summary', '')}\n\n"
                    f"## Description\n\n{advisory.get('description', '')}\n"
                )
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                mark_ingested("github_dependabot", item_id)
                write_log('monitor', 'github_ingest', f"Fetched Dependabot alert #{alert_num} for {repo}")
                print(f"  ✓ Dependabot #{alert_num}: {advisory.get('summary', '')[:60]}")
                fetched += 1

            if fetched == 0:
                print(f"  – No new Dependabot alerts for {repo}")
        elif response.status_code in (403, 404):
            pass  # Token lacks scope or feature disabled — silently skip
        else:
            print(f"  ! Dependabot status {response.status_code} for {repo}")
    except Exception as e:
        write_log('monitor', 'github_error', f"{repo} (dependabot): {e}")
        print(f"  ! Failed Dependabot for {repo}: {e}")


def check_github():
    etags = _load_etags()

    for repo in GITHUB_REPOS:
        repo = repo.strip()
        if not repo:
            continue
        print(f"\nPolling GitHub: {repo}")
        _poll_releases(repo, etags)
        _poll_advisories(repo)
        _poll_dependabot(repo)
        write_log('monitor', 'github', f"Polled {repo}")

    _save_etags(etags)
    print("\nGitHub polling complete.")


if __name__ == '__main__':
    check_github()
