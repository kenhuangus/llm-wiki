import requests
import feedparser
import os
import io
import pypdf
from common import write_log, RAW_DIR, ARXIV_MAX_RESULTS, ARXIV_CATEGORIES
from datetime import datetime


def check_arxiv():
    categories = "+OR+".join(f"cat:{c.strip()}" for c in ARXIV_CATEGORIES)
    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query={categories}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={ARXIV_MAX_RESULTS}"
    )
    print(f"Polling arXiv [{', '.join(ARXIV_CATEGORIES)}] (max {ARXIV_MAX_RESULTS})...")

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
            safe_title = "".join(c if c.isalnum() else "_" for c in entry.title)[:50]
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}_{arxiv_id}_{safe_title}.md"
            target_path = os.path.join(target_dir, filename)

            if os.path.exists(target_path):
                print(f"  – Already ingested: {arxiv_id}")
                continue

            authors = ", ".join(a.get("name", "") for a in entry.get("authors", []))
            tags = ", ".join(t.get("term", "") for t in entry.get("tags", []))
            published = entry.get("published", "")

            pdf_url = entry.id.replace("abs", "pdf")
            pdf_text = ""
            print(f"  Fetching PDF for {arxiv_id}...")
            try:
                pdf_resp = requests.get(pdf_url, timeout=30)
                if pdf_resp.status_code == 200:
                    try:
                        reader = pypdf.PdfReader(io.BytesIO(pdf_resp.content))
                        # Extract first 5 pages to avoid massive context bloating
                        for i in range(min(len(reader.pages), 5)):
                            pdf_text += reader.pages[i].extract_text() + "\n"
                    except Exception as e:
                        print(f"  [Warning] Failed to parse PDF text: {e}")
            except Exception as e:
                print(f"  [Warning] Failed to download PDF: {e}")

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

            write_log('monitor', 'arxiv_ingest', f"Fetched {arxiv_id}: {entry.title[:60]}")
            print(f"  ✓ {arxiv_id}: {entry.title[:60]}")
            fetched += 1

        write_log('monitor', 'arxiv', f"Polled — {fetched} new papers saved.")
        print(f"Done. {fetched} new paper(s) saved.")

    except Exception as e:
        write_log('monitor', 'arxiv_error', str(e))
        print(f"Failed to fetch arXiv: {e}")


if __name__ == '__main__':
    check_arxiv()
