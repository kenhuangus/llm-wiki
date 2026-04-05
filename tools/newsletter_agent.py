"""
newsletter_agent.py — Weekly Knowledge Synthesis Agent

Queries all wiki/ items modified in the last 7 days and generates a
high-quality Markdown newsletter in wiki/synthesis/newsletters/.

Integrates NVD, GitHub, arXiv, and RSS findings into a "Weekly Pulse" report.

Usage:
    python tools/newsletter_agent.py [--days N]
"""
import os
import sys
import time
import glob
import subprocess
from datetime import datetime, timedelta
from common import WIKI_DIR, WIKI_ROOT, call_local_model, write_log, parse_frontmatter


def get_recent_articles(days: int = 7) -> list:
    """Scan wiki/ for files modified in the last N days, excluding meta files."""
    cutoff = time.time() - (days * 86400)
    all_files = glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True)
    return [
        f for f in all_files
        if os.path.basename(f) not in ('index.md', 'log.md')
        and os.path.getmtime(f) > cutoff
    ]


def _categorize_articles(paths: list) -> dict:
    """
    Group wiki pages by their domain/path prefix for structured newsletter sections.
    Returns dict: { 'cve': [...], 'arxiv': [...], 'github': [...], 'other': [...] }
    """
    buckets = {'cve': [], 'arxiv': [], 'github': [], 'rss': [], 'other': []}
    for path in paths:
        rel = os.path.relpath(path, WIKI_DIR).replace('\\', '/')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        meta, body = parse_frontmatter(content)
        entry = {
            'path': rel,
            'title': meta.get('title', os.path.basename(path)),
            'confidence': meta.get('confidence', 0.0),
            'status': meta.get('status', 'current'),
            'snippet': body.strip()[:400],
        }
        domain = meta.get('domain', '')
        if 'cve' in rel or 'cve' in domain:
            buckets['cve'].append(entry)
        elif 'arxiv' in rel or 'arxiv' in domain:
            buckets['arxiv'].append(entry)
        elif 'github' in rel or 'github' in domain:
            buckets['github'].append(entry)
        elif 'rss' in rel or 'rss' in domain:
            buckets['rss'].append(entry)
        else:
            buckets['other'].append(entry)
    return buckets


def _format_section_context(label: str, entries: list, max_items: int = 5) -> str:
    if not entries:
        return ""
    lines = [f"\n### {label}\n"]
    for e in entries[:max_items]:
        lines.append(f"TITLE: {e['title']}\nPATH: {e['path']}\nCONFIDENCE: {e['confidence']}\nSNIPPET: {e['snippet']}\n")
    return "\n".join(lines)


def generate_newsletter(days: int = 7):
    recent_paths = get_recent_articles(days)
    if not recent_paths:
        print(f"No wiki pages modified in the last {days} days. Nothing to synthesize.")
        return

    print(f"Found {len(recent_paths)} recently updated page(s). Building newsletter...")

    buckets = _categorize_articles(recent_paths)

    # Build structured context for the LLM
    context = ""
    context += _format_section_context("Security / CVE Findings", buckets['cve'])
    context += _format_section_context("arXiv Research Papers", buckets['arxiv'])
    context += _format_section_context("GitHub Releases & Advisories", buckets['github'])
    context += _format_section_context("Blog & RSS Highlights", buckets['rss'])
    context += _format_section_context("Other Wiki Updates", buckets['other'])

    # Stats for the header
    cve_count = len(buckets['cve'])
    arxiv_count = len(buckets['arxiv'])
    github_count = len(buckets['github'])
    rss_count = len(buckets['rss'])
    date_str = datetime.now().strftime("%Y-%m-%d")
    week_num = datetime.now().isocalendar()[1]

    system_prompt = (
        "You are a professional AI and Security Research analyst. "
        "Write high-quality, concise Markdown newsletters for a technical audience. "
        "Be specific — cite actual titles and findings from the provided context. "
        "Do not invent information not present in the context."
    )

    input_text = f"""
You are writing the Weekly Pulse newsletter for the Agentic Local-First LLM Wiki.
Date: {date_str} | Week: {week_num}
Sources this week: {cve_count} CVEs, {arxiv_count} arXiv papers, {github_count} GitHub updates, {rss_count} blog posts.

WIKI CONTENT FROM THIS WEEK:
{context}

TASK: Write a 600-900 word Weekly Pulse newsletter in Markdown with these exact sections:

## 🔒 Security & CVE Roundup
Summarize the most important CVEs and security advisories. Include CVSS scores where available.
If no CVEs: note the quiet week and mention any security-adjacent findings.

## 🧪 Research Spotlight
Highlight the most relevant arXiv papers. Explain why they matter for agentic AI or security.
If no arXiv papers: draw from blog/RSS research content.

## 🛠️ Tooling & Releases
Cover GitHub releases and framework updates. Focus on breaking changes and security patches.

## 📰 Community & Blog Highlights
Summarize notable blog posts, articles, or community discussions ingested this week.

## 🔮 Strategic Takeaway
One paragraph: what does this week's data signal about the direction of agentic AI and security?

FORMAT RULES:
- Use Obsidian wiki links [[path]] when referencing specific wiki pages
- Keep each section to 2-4 sentences or bullet points
- Professional but readable tone
- Do NOT add a title — it will be added by the system
"""

    print("Requesting synthesis from local LLM...")
    newsletter_body = call_local_model(system_prompt, input_text)

    if not newsletter_body or len(newsletter_body) < 200:
        print("FAILED: LLM response was too short or empty.")
        return

    # Build frontmatter
    hex_id = hex(int(time.time()))[2:]
    frontmatter_block = (
        f"---\n"
        f"id: {hex_id}\n"
        f"title: Weekly Pulse — {date_str}\n"
        f"domain: synthesis/newsletters\n"
        f"source_count: {len(recent_paths)}\n"
        f"confidence: 0.95\n"
        f"verified: true\n"
        f"last_updated: {date_str}\n"
        f"status: current\n"
        f"---\n\n"
    )

    title_block = (
        f"# 🧠 LLM Wiki Weekly Pulse — Week {week_num}, {date_str}\n\n"
        f"> Synthesized from {len(recent_paths)} wiki updates: "
        f"{cve_count} CVEs · {arxiv_count} arXiv papers · "
        f"{github_count} GitHub updates · {rss_count} blog posts\n\n"
        f"---\n\n"
    )

    final_output = frontmatter_block + title_block + newsletter_body

    out_dir = os.path.join(WIKI_DIR, 'synthesis', 'newsletters')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{date_str}_pulse.md")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"SUCCESS: Newsletter saved to {out_path}")
    write_log(
        'newsletter_agent', 'generated',
        f"Week {week_num} pulse: {len(recent_paths)} sources "
        f"({cve_count} CVE, {arxiv_count} arXiv, {github_count} GitHub, {rss_count} RSS)"
    )

    # Re-index to include the new newsletter
    try:
        subprocess.run(
            ["python", os.path.join(WIKI_ROOT, "tools", "index.py")],
            check=True
        )
    except Exception as e:
        print(f"  [Warning] Re-index failed: {e}")


if __name__ == "__main__":
    days = 7
    if "--days" in sys.argv:
        try:
            days = int(sys.argv[sys.argv.index("--days") + 1])
        except (IndexError, ValueError):
            pass
    generate_newsletter(days)
