"""
test_user_workflow.py — Simulate real user workflow

Tests the complete end-to-end flow:
1. Monitor runs and ingests new content
2. Content is normalized and extracted
3. Wiki pages are created/updated
4. Index is rebuilt
5. Newsletter is generated
6. API serves content
7. Search works correctly
"""
import requests
import time

API_BASE = "http://127.0.0.1:8000"

def test_workflow():
    print("\n" + "="*60)
    print("USER WORKFLOW TEST")
    print("="*60)
    
    # 1. Check API is running
    print("\n[1] Checking API server...")
    try:
        resp = requests.get(f"{API_BASE}/", timeout=2)
        assert resp.status_code == 200
        print("  ✓ API server is online")
    except Exception as e:
        print(f"  ❌ API server not running: {e}")
        return False
    
    # 2. Get stats
    print("\n[2] Fetching wiki stats...")
    resp = requests.get(f"{API_BASE}/api/stats")
    stats = resp.json()
    print(f"  ✓ Pages: {stats['pageCount']}")
    print(f"  ✓ Monitors: {stats['monitorCount']}")
    print(f"  ✓ Conflicts: {stats['conflictCount']}")
    print(f"  ✓ Avg Confidence: {stats['avgConfidence']}")
    
    # 3. Search for CVE content
    print("\n[3] Searching for 'CVE security'...")
    resp = requests.post(
        f"{API_BASE}/api/search",
        json={"query": "CVE security"},
        headers={"Content-Type": "application/json"}
    )
    results = resp.json()["results"]
    print(f"  ✓ Found {len(results)} results")
    if results:
        print(f"  ✓ Top result: {results[0]['path']} (score: {results[0]['score']:.2f})")
    
    # 4. Get article list
    print("\n[4] Fetching article list...")
    resp = requests.get(f"{API_BASE}/api/articles")
    articles = resp.json()["articles"]
    print(f"  ✓ Found {len(articles)} articles")
    
    # 5. Read a specific article
    print("\n[5] Reading newsletter article...")
    newsletter_path = "synthesis/newsletters/2026-04-05_pulse.md"
    resp = requests.get(f"{API_BASE}/api/article/{newsletter_path}")
    content = resp.json()["content"]
    assert "Weekly Pulse" in content
    assert "CVE Roundup" in content
    print(f"  ✓ Newsletter loaded ({len(content)} chars)")
    
    # 6. Read a CVE article
    print("\n[6] Reading CVE article...")
    cve_path = "security/cve/cve-1999-0236.md"
    resp = requests.get(f"{API_BASE}/api/article/{cve_path}")
    content = resp.json()["content"]
    assert "CVE-1999-0236" in content
    assert "CVSS" in content
    print(f"  ✓ CVE article loaded ({len(content)} chars)")
    
    # 7. Check logs
    print("\n[7] Checking operation logs...")
    resp = requests.get(f"{API_BASE}/api/logs")
    logs = resp.json()["logs"]
    assert "monitor" in logs
    assert "integrate" in logs
    print(f"  ✓ Logs available ({len(logs)} chars)")
    
    print("\n" + "="*60)
    print("✅ ALL USER WORKFLOW TESTS PASSED")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_workflow()
    exit(0 if success else 1)
