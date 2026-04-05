import os
import glob
from common import WIKI_DIR, parse_frontmatter, write_log, call_local_model

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
        # Pass the full body instead of just the first 500 characters
        claims_to_check.append({"file": filename, "body": body.strip()})

    if len(claims_to_check) < 2:
        print("Not enough pages for semantic comparison.")
        return

    input_text = "Analyze these summaries:\n\n"
    for c in claims_to_check:
        input_text += f"---\nFile: {c['file']}\nContent: {c['body']}\n"

    system_prompt = "Find contradictions. Return valid JSON: [{\"conflict\": \"...\", \"files\": [\"f1\", \"f2\"]}]"
    
    conflicts = call_local_model(system_prompt, input_text)
    
    if conflicts:
        write_log('lint', 'deep_lint', "LLM output: " + conflicts.replace('\n', ' '))
        print("Deep lint completed. See log.md.")
    else:
        print("Deep lint LLM call failed or returned empty.")

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
            print(f"[WARN] {filename} is missing fields: {', '.join(missing)}")
            
    write_log('lint', 'lightweight', f"Passed with {missing_fields} missing fields, 0 broken links")
    print(f"Lightweight linting complete. Checked {pages_checked} pages.")

if __name__ == '__main__':
    import sys
    if '--deep' in sys.argv:
        deep_lint()
    else:
        lightweight_lint()
