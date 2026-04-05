"""
lint.py — Wiki consistency checks.

Improvements (Phase 2):
  - Deep lint now writes [CONFLICT] tags back to affected pages and updates status
  - Confidence propagation check: warns when Tier 3 claims have confidence > 0.6
"""
import os
import glob
import re
from common import WIKI_DIR, parse_frontmatter, serialize_frontmatter, write_log, call_local_model


_TIER3_CONFIDENCE_CEILING = 0.6  # Tier 3 sources must not exceed this


def _apply_conflict_tag(filepath: str, conflict_description: str):
    """Add [CONFLICT] tag to a page and set status to conflict."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    meta, body = parse_frontmatter(content)

    # Only update if not already marked
    if meta.get('status') == 'conflict':
        return

    meta['status'] = 'conflict'
    conflict_note = f"\n> [CONFLICT] {conflict_description}\n"

    # Insert conflict note before first ## heading, or prepend
    if '## ' in body:
        body = body.replace('## ', conflict_note + '\n## ', 1)
    else:
        body = conflict_note + body

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(serialize_frontmatter(meta, body))

    write_log('[CONFLICT]', 'lint_deep', f"Tagged conflict in {os.path.basename(filepath)}: {conflict_description[:80]}")
    print(f"  [CONFLICT] Tagged: {os.path.basename(filepath)}")


def deep_lint():
    print("Running LLM-assisted deep lint to detect claim contradictions...")
    pages = glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True)
    claims_to_check = []

    for page in pages:
        filename = os.path.basename(page)
        if filename in ('index.md', 'log.md', 'curated-sources.md'):
            continue
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()
        _, body = parse_frontmatter(content)
        claims_to_check.append({"file": filename, "path": page, "body": body.strip()})

    if len(claims_to_check) < 2:
        print("Not enough pages for semantic comparison.")
        return

    input_text = "Analyze these wiki page summaries for contradictions:\n\n"
    for c in claims_to_check:
        input_text += f"---\nFile: {c['file']}\nContent: {c['body'][:600]}\n"

    system_prompt = (
        "Find direct factual contradictions between these wiki pages. "
        "Return ONLY valid JSON array: "
        '[{"conflict": "description of contradiction", "files": ["filename1", "filename2"]}]. '
        "Return [] if no contradictions found."
    )

    raw_output = call_local_model(system_prompt, input_text)

    if not raw_output:
        print("Deep lint LLM call failed or returned empty.")
        return

    write_log('lint', 'deep_lint', "LLM output: " + raw_output.replace('\n', ' ')[:200])

    # Parse and apply conflict tags
    try:
        # Strip markdown code fences if present
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```[a-z]*\n?', '', cleaned).rstrip('`').strip()

        import json
        conflicts = json.loads(cleaned)
        if not isinstance(conflicts, list):
            conflicts = []

        # Build filename → path map
        path_map = {os.path.basename(c['path']): c['path'] for c in claims_to_check}

        applied = 0
        for conflict in conflicts:
            desc = conflict.get('conflict', '')
            for fname in conflict.get('files', []):
                if fname in path_map:
                    _apply_conflict_tag(path_map[fname], desc)
                    applied += 1

        print(f"Deep lint complete. {len(conflicts)} conflict(s) found, {applied} page(s) tagged.")

    except Exception as e:
        print(f"Deep lint: could not parse LLM JSON output ({e}). Raw: {raw_output[:100]}")


def _check_confidence_propagation(pages: list):
    """Warn when a page has confidence > TIER3_CEILING but no verified=true."""
    issues = 0
    for page in pages:
        filename = os.path.basename(page)
        if filename in ('index.md', 'log.md'):
            continue
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()
        meta, _ = parse_frontmatter(content)
        confidence = meta.get('confidence', 0.0)
        verified = meta.get('verified', False)
        try:
            conf_float = float(confidence)
        except (ValueError, TypeError):
            continue
        if conf_float > _TIER3_CONFIDENCE_CEILING and not verified:
            print(f"  [WARN] High confidence ({conf_float}) but unverified: {filename}")
            issues += 1
    return issues


def lightweight_lint():
    broken_links = 0
    missing_fields = 0
    pages_checked = 0

    pages = glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True)
    required_fields = ['id', 'title', 'domain', 'confidence', 'status', 'last_updated']

    for page in pages:
        filename = os.path.basename(page)
        if filename in ('index.md', 'log.md'):
            continue

        pages_checked += 1
        with open(page, 'r', encoding='utf-8') as f:
            content = f.read()

        meta, _ = parse_frontmatter(content)
        missing = [field for field in required_fields if field not in meta]
        if missing:
            missing_fields += 1
            print(f"  [WARN] {filename} missing fields: {', '.join(missing)}")

    conf_issues = _check_confidence_propagation(pages)

    write_log(
        'lint', 'lightweight',
        f"{missing_fields} missing fields, {broken_links} broken links, {conf_issues} confidence warnings"
    )
    print(
        f"Lightweight lint complete. {pages_checked} pages checked. "
        f"{missing_fields} missing fields, {conf_issues} confidence warnings."
    )


if __name__ == '__main__':
    import sys
    if '--deep' in sys.argv:
        deep_lint()
    else:
        lightweight_lint()
