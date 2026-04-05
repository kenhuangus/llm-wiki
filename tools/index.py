import os
import glob
from common import WIKI_DIR, parse_frontmatter, write_log

def rebuild_index():
    index_path = os.path.join(WIKI_DIR, 'index.md')
    domains = {}
    
    # Gather all markdown files in wiki except index.md and log.md
    for root, _, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith('.md') and f not in ('index.md', 'log.md'):
                filepath = os.path.join(root, f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    meta, _ = parse_frontmatter(content)
                    domain = meta.get('domain', 'uncategorized')
                    if domain not in domains:
                        domains[domain] = []
                    domains[domain].append({
                        'title': meta.get('title', f),
                        'confidence': meta.get('confidence', 0.0),
                        'status': meta.get('status', 'current'),
                        'path': os.path.relpath(filepath, WIKI_DIR).replace('\\', '/')
                    })
                    
    with open(index_path, 'w', encoding='utf-8') as index_file:
        index_file.write("# Global Knowledge Catalog\n\n")
        index_file.write("> Auto-generated index of the agentic local-first LLM wiki.\n\n")
        
        for domain, pages in sorted(domains.items()):
            index_file.write(f"## {domain.title()} ({len(pages)} pages)\n\n")
            for page in sorted(pages, key=lambda x: x['title']):
                title = page['title']
                path = page['path']
                index_file.write(f"- [[{path}]] | {title} (Status: {page['status']}, Confidence: {page['confidence']})\n")
            index_file.write("\n")
            
    write_log('index', 'rebuilt index.md', f"{sum(len(p) for p in domains.values())} pages indexed")
    print("Index rebuilt successfully.")

if __name__ == '__main__':
    rebuild_index()
