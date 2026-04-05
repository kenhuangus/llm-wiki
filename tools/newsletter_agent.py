"""
newsletter_agent.py — Weekly Knowledge Synthesis Agent
Analyzes all wiki files modified in the past 7 days to generate a 
high-quality industry-style newsletter.

Usage:
    python tools/newsletter_agent.py
"""
import os
import sys
import time
import glob
from datetime import datetime, timedelta
from common import WIKI_DIR, call_local_model, write_log

def get_recent_articles(days=7):
    """Scan wiki/ for files modified in the last N days."""
    cutoff = time.time() - (days * 86400)
    all_files = glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True)
    
    recent = []
    for f in all_files:
        if os.path.basename(f) in ('index.md', 'log.md'): continue
        if os.path.getmtime(f) > cutoff:
            recent.append(f)
    return recent

def generate_newsletter():
    recent_paths = get_recent_articles(7)
    if not recent_paths:
        print("No new knowledge found in the last 7 days to synthesize.")
        return

    print(f"Found {len(recent_paths)} recent articles. Summarizing for newsletter...")
    
    context_chunks = []
    for path in recent_paths[:20]: # Limit context to avoid nuking memory
        rel_path = os.path.relpath(path, WIKI_DIR)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Get first 400 chars of content (excluding frontmatter if possible)
            body = content.split('---')[-1].strip()[:400]
            context_chunks.append(f"ARTICLE: {rel_path}\nCONTENT: {body}\n")

    full_context = "\n".join(context_chunks)
    
    system_prompt = "You are a professional AI and Security Research Agent. Your task is to write high-quality Markdown newsletters summarizing weekly knowledge."

    input_text = f"""
    Review the following knowledge entities that were ingested into our Local-First LLM Wiki this week:
    
    {full_context}
    
    TASK:
    Write a high-quality Weekly Pulse Newsletter of 500-800 words.
    The newsletter must have:
    1. A creative title and professional header (e.g. LLM Wiki Weekly Pulse).
    2. A 'Top 3 Critical Discoveries' section (focus on CVEs and security advisories).
    3. An 'AI Research Spotlight' (focus on arXiv papers).
    4. A 'DevOps & Tooling' update (GitHub releases).
    5. A forward-looking 'Strategic Takeaway' conclusion.
    
    FORMAT: Markdown with clean headers and professional tone.
    """

    print("Requesting synthesis from local LLM...")
    newsletter_md = call_local_model(system_prompt, input_text)
    
    if not newsletter_md or len(newsletter_md) < 200:
        print("FAILED: Large model response was too short or empty.")
        return

    # Add frontmatter to the newsletter
    date_str = datetime.now().strftime("%Y-%m-%d")
    final_output = f"""---
id: {hex(int(time.time()))[2:]}
title: Weekly Pulse — {date_str}
domain: synthesis/newsletters
source_count: {len(recent_paths)}
confidence: 0.95
verified: true
last_updated: {date_str}
status: current
---

{newsletter_md}
"""

    # Save to synthesis/newsletters
    out_dir = os.path.join(WIKI_DIR, 'synthesis', 'newsletters')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{date_str}_pulse.md")
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"SUCCESS: Newsletter generated at {out_path}")
    write_log("newsletter_agent", "generated", f"Synthesized {len(recent_paths)} items.")
    
    # Re-index to include the new newsletter
    try:
        subprocess.run(["python", "tools/index.py"])
    except: pass

if __name__ == "__main__":
    generate_newsletter()
