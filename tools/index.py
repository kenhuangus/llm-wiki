"""
index.py — Rebuild wiki/index.md.

Improvements (Phase 2):
  - Per-domain coverage statistics (page count, avg confidence)
  - "Pending Human Review" section listing conflict/review-needed pages
"""
import os
import glob
from common import WIKI_DIR, parse_frontmatter, write_log


def rebuild_index():
    index_path = os.path.join(WIKI_DIR, 'index.md')
    domains = {}
    pending_review = []
    total_confidence = []

    for root, _, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md') and f not in ('index.md', 'log.md'):
                filepath = os.path.join(root, f)
                with open(filepath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                meta, _ = parse_frontmatter(content)
                domain = meta.get('domain', 'uncategorized')
                status = meta.get('status', 'current')
                confidence = meta.get('confidence', 0.0)
                rel_path = os.path.relpath(filepath, WIKI_DIR).replace('\\', '/')

                if domain not in domains:
                    domains[domain] = []
                domains[domain].append({
                    'title': meta.get('title', f),
                    'confidence': confidence,
                    'status': status,
                    'path': rel_path,
                })

                if isinstance(confidence, (int, float)):
                    total_confidence.append(float(confidence))

                if status in ('conflict', 'review-needed'):
                    pending_review.append({
                        'title': meta.get('title', f),
                        'path': rel_path,
                        'status': status,
                        'confidence': confidence,
                    })

    total_pages = sum(len(p) for p in domains.values())
    avg_conf = (sum(total_confidence) / len(total_confidence)) if total_confidence else 0.0

    with open(index_path, 'w', encoding='utf-8') as idx:
        idx.write("# Global Knowledge Catalog\n\n")
        idx.write("> Auto-generated index of the agentic local-first LLM wiki.\n\n")

        # ── Coverage summary ─────────────────────────────────────────────────
        idx.write("## Coverage Summary\n\n")
        idx.write(f"| Metric | Value |\n|--------|-------|\n")
        idx.write(f"| Total pages | {total_pages} |\n")
        idx.write(f"| Domains covered | {len(domains)} |\n")
        idx.write(f"| Average confidence | {avg_conf:.2f} |\n")
        idx.write(f"| Pending review | {len(pending_review)} |\n\n")

        # ── Pending human review ─────────────────────────────────────────────
        if pending_review:
            idx.write("## Pending Human Review\n\n")
            for page in sorted(pending_review, key=lambda x: x['status']):
                idx.write(
                    f"- [[{page['path']}]] | {page['title']} "
                    f"(Status: **{page['status']}**, Confidence: {page['confidence']})\n"
                )
            idx.write("\n")

        # ── Per-domain listings ──────────────────────────────────────────────
        for domain, pages in sorted(domains.items()):
            domain_confs = [p['confidence'] for p in pages if isinstance(p['confidence'], (int, float))]
            domain_avg = (sum(domain_confs) / len(domain_confs)) if domain_confs else 0.0
            idx.write(
                f"## {domain.replace('/', ' / ').title()} "
                f"({len(pages)} pages, avg confidence: {domain_avg:.2f})\n\n"
            )
            for page in sorted(pages, key=lambda x: x['title']):
                idx.write(
                    f"- [[{page['path']}]] | {page['title']} "
                    f"(Status: {page['status']}, Confidence: {page['confidence']})\n"
                )
            idx.write("\n")

    write_log('index', 'rebuilt index.md', f"{total_pages} pages indexed across {len(domains)} domains")
    print(f"Index rebuilt: {total_pages} pages, {len(domains)} domains, {len(pending_review)} pending review.")


if __name__ == '__main__':
    rebuild_index()
