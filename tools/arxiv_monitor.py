"""
arxiv_monitor.py — Poll arXiv for new papers.

Improvements (Phase 2):
  - SQLite deduplication by arXiv ID (survives file renames)
  - Keyword relevance pre-filter (ARXIV_KEYWORDS in .env)
  - Semantic Scholar citation count filter (ARXIV_MIN_CITATIONS in .env)
"""
import requests
import feedparser
import os
import io
import pypdf
from common import (
    write_log, RAW_DIR,
    ARXIV_MAX_RESULTS, ARXIV_CATEGORIES,
    ARXIV_MIN_CITATIONS, ARXIV_KEYWORDS, S2_API_KEY,
    is_already_ingested, mark_ingested, score_relevance,
)
from datetime import datetime


def get_citation_count(arxiv_id: str) -> int:
    """Query Semantic Scholar for citation count. Returns -1 on failure."""
    if not ARXIV_MIN_CITATIONS:
        return -1  # filter disabled
    try:
        headers = {"x-api-key": S2_API_KEY} if S2_API_KEY else {}
        url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}"
        resp = requests.get(url, headers=headers, params={"fields": "citationCount"}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get("citationCount", 0)
    except Exception as e:
        print(f"  [S2] Citation lookup failed for {arxiv_id}: {e}")
    return -1


def check_arxiv():
    categories = "+OR+".join(f"cat:{c.strip()}" for c in ARXIV_CATEGORIES)
    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query={categories}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={ARXIV_MAX_RESULTS}"
    )
    print(f"Polling arXiv [{', '.join(ARXIV_CATEGORIES)}] (max {ARXIV_MAX_RESULTS})...")
    if ARXIV_KEYWORDS:
        print(f"  Keyword filter active: {ARXIV_KEYWORDS}")
    if ARXIV_MIN_CITATIONS:
        print(f"  Citation filter active: min {ARXIV_MIN_CITATIONS} citations")

    try:
        response = None
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=20)
                break
            except requests.exceptions.Timeout:
                print(f"  Timeout on attempt {attempt+1}/3, retrying...")
        if response is None:
            raise TimeoutError("All 3 attempts timed out.")
        feed = feedparser.parse(response.content)

        target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'arxiv')
        os.makedirs(target_dir, exist_ok=True)

        fetched = 0
        for entry in feed.entries:
            arxiv_id = entry.get("id", "").split("/abs/")[-1].replace("/", "_")

            # ── 1. SQLite deduplication ──────────────────────────────────────
            if is_already_ingested("arxiv", arxiv_id):
                print(f"  – Already ingested (DB): {arxiv_id}")
                continue

            # ── 2. Keyword relevance pre-filter ─────────────────────────────
            candidate_text = f"{entry.title} {entry.summary}"
            relevance = score_relevance(candidate_text, ARXIV_KEYWORDS)
            if ARXIV_KEYWORDS and relevance == 0.0:
                print(f"  – Skipped (no keyword match): {entry.title[:60]}")
                continue

            # ── 3. Citation count filter (Semantic Scholar) ──────────────────
            if ARXIV_MIN_CITATIONS:
                citations = get_citation_count(arxiv_id)
                if citations != -1 and citations < ARXIV_MIN_CITATIONS:
                    print(f"  – Skipped (citations={citations} < {ARXIV_MIN_CITATIONS}): {arxiv_id}")
                    continue

            authors = ", ".join(a.get("name", "") for a in entry.get("authors", []))
            tags = ", ".join(t.get("term", "") for t in entry.get("tags", []))
            published = entry.get("published", "")

            # ── 4. PDF download ──────────────────────────────────────────────
            pdf_url = entry.id.replace("abs", "pdf")
            pdf_text = ""
            print(f"  Fetching PDF for {arxiv_id}...")
            try:
                pdf_resp = requests.get(pdf_url, timeout=30)
                if pdf_resp.status_code == 200:
                    try:
                        reader = pypdf.PdfReader(io.BytesIO(pdf_resp.content))
                        for i in range(min(len(reader.pages), 5)):
                            pdf_text += reader.pages[i].extract_text() + "\n"
                    except Exception as e:
                        print(f"  [Warning] Failed to parse PDF text: {e}")
            except Exception as e:
                print(f"  [Warning] Failed to download PDF: {e}")

            safe_title = "".join(c if c.isalnum() else "_" for c in entry.title)[:50]
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}_{arxiv_id}_{safe_title}.md"
            target_path = os.path.join(target_dir, filename)

            content = (
                f"Title: {entry.title}\n"
                f"URL: {entry.link}\n"
                f"Authors: {authors}\n"
                f"Published: {published}\n"
                f"Categories: {tags}\n\n"
                f"## Abstract\n\n{entry.summary}\n\n"
                f"## Content (First 5 Pages)\n\n"
                f"{pdf_text.strip() or 'No PDF content extracted.'}\n"
            )

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)

            mark_ingested("arxiv", arxiv_id)
            write_log('monitor', 'arxiv_ingest', f"Fetched {arxiv_id}: {entry.title[:60]}")
            print(f"  ✓ {arxiv_id}: {entry.title[:60]}")
            fetched += 1

        write_log('monitor', 'arxiv', f"Successfully polled latest arXiv feeds.")
        print(f"Done. {fetched} new paper(s) saved.")

    except Exception as e:
        write_log('monitor', 'arxiv_error', str(e))
        print(f"Failed to fetch arXiv: {e}")


if __name__ == '__main__':
    check_arxiv()
