import requests
import feedparser
import os
from common import write_log, RAW_DIR, RSS_FEEDS
from datetime import datetime


# Default security/AI blog feeds if none set in .env
DEFAULT_FEEDS = [
    "https://blog.trailofbits.com/feed/",
    "https://openai.com/news/rss.xml",
    "https://www.anthropic.com/rss.xml",
    "https://deepmind.google/blog/rss.xml",
    "https://research.google/blog/rss/",
]


def check_rss():
    feeds = RSS_FEEDS if RSS_FEEDS else DEFAULT_FEEDS
    print(f"Polling {len(feeds)} RSS feeds...")

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

            for entry in feed.entries[:3]:   # top 3 per feed
                entry_id = "".join(c if c.isalnum() else "_" for c in entry.get("id", entry.title))[:40]
                date_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"{date_str}_{entry_id}.md"
                target_path = os.path.join(target_dir, filename)

                if os.path.exists(target_path):
                    continue

                summary = entry.get("summary", entry.get("content", [{}])[0].get("value", ""))
                content = (
                    f"Title: {entry.get('title', 'Untitled')}\n"
                    f"URL: {entry.get('link', '')}\n"
                    f"Feed: {feed_title}\n"
                    f"Published: {entry.get('published', '')}\n\n"
                    f"## Summary\n\n{summary}\n"
                )
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
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
