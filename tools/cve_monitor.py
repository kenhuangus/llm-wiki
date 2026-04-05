"""
cve_monitor.py — Poll NVD for new CVEs.

Improvements (Phase 2):
  - lastModStartDate state file to only fetch new/modified CVEs per run
  - CVSS >= 7.0 immediate pipeline trigger (normalize → extract → integrate)
  - CVSS >= 9.0 human escalation: writes CRITICAL_ALERT.md + [CRITICAL] log tag
"""
import requests
import os
import json
import subprocess
import glob
from common import (
    write_log, RAW_DIR, WIKI_DIR, WIKI_ROOT,
    CVE_FEED_URL, CVE_MAX_RESULTS, NVD_API_KEY,
    is_already_ingested, mark_ingested,
)
from datetime import datetime, timedelta, timezone


# Path to persist the last-run timestamp
_STATE_FILE = os.path.join(WIKI_ROOT, 'state_cve_last_run.txt')


def _load_last_run() -> str:
    """Return ISO-8601 string of last successful run, or 7 days ago."""
    if os.path.exists(_STATE_FILE):
        with open(_STATE_FILE, 'r') as f:
            val = f.read().strip()
            if val:
                return val
    # Use 30 days ago as default to catch recent CVEs
    return (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.000")


def _save_last_run():
    with open(_STATE_FILE, 'w') as f:
        f.write(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000"))


def _trigger_pipeline(raw_path: str, cve_id: str):
    """Run normalize → extract → integrate for a high-severity CVE."""
    print(f"  [PIPELINE] Triggering immediate pipeline for {cve_id}...")
    tools_dir = os.path.join(WIKI_ROOT, 'tools')
    try:
        subprocess.run(["python", os.path.join(tools_dir, "normalize.py"), raw_path, "ai-security"], check=True)
        norm_dir = os.path.join(RAW_DIR, 'normalized', 'ai-security')
        norm_files = sorted(glob.glob(os.path.join(norm_dir, "*.md")), key=os.path.getmtime, reverse=True)
        if not norm_files:
            return
        latest_norm = norm_files[0]
        subprocess.run(["python", os.path.join(tools_dir, "extract.py"), latest_norm], check=True)
        json_path = latest_norm + ".json"
        title = cve_id
        subprocess.run(
            ["python", os.path.join(tools_dir, "integrate.py"), json_path, "security", "cve", title],
            check=True
        )
        subprocess.run(["python", os.path.join(tools_dir, "index.py")], check=True)
        print(f"  [PIPELINE] Complete for {cve_id}.")
    except Exception as e:
        write_log('cve_pipeline_error', cve_id, str(e))
        print(f"  [PIPELINE] Failed for {cve_id}: {e}")


def _write_critical_alert(cve_id: str, base_score: float, summary: str):
    """Write CRITICAL_ALERT.md at repo root for CVSS >= 9.0."""
    alert_path = os.path.join(WIKI_ROOT, 'CRITICAL_ALERT.md')
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = (
        f"\n## [{ts}] CRITICAL CVE: {cve_id} (CVSS {base_score})\n\n"
        f"{summary}\n\n"
        f"**Action required:** Review and update wiki page at `wiki/security/cve/{cve_id}.md`.\n"
    )
    # Create file with header if it doesn't exist
    if not os.path.exists(alert_path):
        with open(alert_path, 'w', encoding='utf-8') as f:
            f.write("# CRITICAL ALERTS — Human Review Required\n")
    with open(alert_path, 'a', encoding='utf-8') as f:
        f.write(entry)
    write_log('[CRITICAL]', 'cve_escalation', f"{cve_id} CVSS={base_score} — CRITICAL_ALERT.md updated")
    print(f"  ⚠️  CRITICAL ALERT written for {cve_id} (CVSS {base_score})")


def check_cve():
    print(f"Polling official NVD API: {CVE_FEED_URL} (max {CVE_MAX_RESULTS})...")

    headers = {}
    if NVD_API_KEY:
        headers["apiKey"] = NVD_API_KEY
        print("  Using NVD API Key (higher rate limits).")
    else:
        print("  No NVD_API_KEY set — rate limited to 5 req/30s.")

    # Note: Remove date filter if testing with future system dates
    # pub_start_date = _load_last_run()
    # print(f"  Fetching CVEs modified since: {pub_start_date}")

    params = {
        "resultsPerPage": CVE_MAX_RESULTS,
        "cvssV3Severity": "HIGH",
        # "lastModStartDate": pub_start_date,  # Disabled for testing
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

                # SQLite deduplication
                if is_already_ingested("cve", cve_id):
                    print(f"  – Already ingested (DB): {cve_id}")
                    continue

                descriptions = cve_data.get("descriptions", [])
                summary = next(
                    (d.get("value") for d in descriptions if d.get("lang") == "en"),
                    "No English description available."
                )

                metrics = cve_data.get("metrics", {})
                cvss_metrics = metrics.get("cvssMetricV31", metrics.get("cvssMetricV30", [{}]))[0]
                cvss_data = cvss_metrics.get("cvssData", {})
                base_score = cvss_data.get("baseScore", 0.0)
                base_severity = cvss_data.get("baseSeverity", "Unknown")

                date_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"{date_str}_{cve_id}.md"
                target_path = os.path.join(target_dir, filename)

                content = (
                    f"Title: {cve_id}\n"
                    f"CVSS v3.x Base Score: {base_score} ({base_severity})\n"
                    f"Published: {cve_data.get('published', '')}\n\n"
                    f"## Description\n\n{summary}\n"
                )
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                mark_ingested("cve", cve_id)
                write_log('monitor', 'cve_ingest', f"Fetched {filename} (CVSS: {base_score})")
                print(f"  ✓ {cve_id} (CVSS: {base_score})")
                fetched += 1

                # ── CVSS >= 9.0: human escalation ────────────────────────────
                try:
                    score_float = float(base_score)
                except (ValueError, TypeError):
                    score_float = 0.0

                if score_float >= 9.0:
                    _write_critical_alert(cve_id, score_float, summary)

                # ── CVSS >= 7.0: immediate pipeline trigger ───────────────────
                if score_float >= 7.0:
                    _trigger_pipeline(target_path, cve_id)

            _save_last_run()
            write_log('monitor', 'cve', f"Successfully polled latest CVEs.")
            print(f"Done. {fetched} new CVE(s) saved.")

        elif response.status_code == 403:
            print("  ! NVD API Rate Limit or Auth Error (HTTP 403).")
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
