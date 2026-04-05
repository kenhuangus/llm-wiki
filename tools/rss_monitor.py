"""
rss_monitor.py — Poll RSS/blog feeds for new articles.

Improvements (Phase 2):
  - Expanded default feed list (NIST, CISA, MITRE, HuggingFace, Papers With Code)
  - Full article scraping for summary-only feeds via trafilatura
  - Relevance scoring pre-filter (RSS_KEYWORDS in .env)
"""
import requests
import feedparser
import os
from common import write_log, RAW_DIR, RSS_FEEDS, RSS_KEYWORDS, is_already_ingested, mark_ingested, score_relevance
from datetime import datetime


DEFAULT_FEEDS = [
    # Security
    "https://blog.trailofbits.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml",
    # AI Labs
    "https://openai.com/news/rss.xml",
    "https://www.anthropic.com/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://research.google/blog/rss/",
    # Research
    "https://huggingface.co/blog/feed.xml",
    "https://paperswithcode.com/latest.rss",
]


def _scrape_full_article(url: str) -> str:
    """Attempt to fetch full article body using trafilatura. Falls back to empty string."""
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            return text or ""
    except ImportError:
        pass  # trafilatura not installed — skip silently
    except Exception:
        pass
    return ""


def check_rss():
    feeds = RSS_FEEDS if RSS_FEEDS else DEFAULT_FEEDS
    print(f"Polling {len(feeds)} RSS feeds...")
    if RSS_KEYWORDS:
        print(f"  Relevance filter active: {RSS_KEYWORDS}")

    target_dir = os.path.join(RAW_DIR, 'auto_ingest', 'rss')
    os.makedirs(target_dir, exist_ok=True)

    total_fetched = 0
    for feed_url in feeds:
        feed_url = feed_url.strip()
        if not feed_url:
            continue
        try:
            response = requests.get(feed_url, timeout=10,
                                    headers={"User-Agent": "LLM-Wiki-Bot/1.0"})
            feed = feedparser.parse(response.content)
            feed_title = feed.feed.get("title", feed_url)
            print(f"  Feed: {feed_title}")

            for entry in feed.entries[:5]:  # top 5 per feed
                entry_id = entry.get("id", entry.get("link", entry.get("title", "")))

                # SQLite deduplication
                if is_already_ingested("rss", entry_id):
                    continue

                summary = entry.get("summary", "")
                if not summary:
                    content_list = entry.get("content", [])
                    summary = content_list[0].get("value", "") if content_list else ""

                # ── Relevance pre-filter ─────────────────────────────────────
                candidate_text = f"{entry.get('title', '')} {summary}"
                if RSS_KEYWORDS and score_relevance(candidate_text, RSS_KEYWORDS) == 0.0:
                    print(f"    – Skipped (no keyword match): {entry.get('title', '')[:60]}")
                    mark_ingested("rss", entry_id)  # mark so we don't re-check
                    continue

                # ── Full article scraping for summary-only feeds ─────────────
                article_url = entry.get("link", "")
                full_body = ""
                if article_url and len(summary) < 300:
                    full_body = _scrape_full_article(article_url)

                body_text = full_body if full_body else summary

                safe_id = "".join(c if c.isalnum() else "_" for c in entry_id)[:40]
                date_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"{date_str}_{safe_id}.md"
                target_path = os.path.join(target_dir, filename)

                content = (
                    f"Title: {entry.get('title', 'Untitled')}\n"
                    f"URL: {article_url}\n"
                    f"Feed: {feed_title}\n"
                    f"Published: {entry.get('published', '')}\n\n"
                    f"## Content\n\n{body_text}\n"
                )
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                mark_ingested("rss", entry_id)
                write_log('monitor', 'rss_ingest', f"Fetched {filename} from {feed_title}")
                print(f"    ✓ {entry.get('title', '')[:70]}")
                total_fetched += 1

        except Exception as e:
            write_log('monitor', 'rss_error', f"{feed_url}: {e}")
            print(f"  ! Failed {feed_url}: {e}")

    write_log('monitor', 'rss', f"Polled {len(feeds)} feeds — {total_fetched} new items.")
    print(f"Done. {total_fetched} new item(s) saved.")


if __name__ == '__main__':
    check_rss()
