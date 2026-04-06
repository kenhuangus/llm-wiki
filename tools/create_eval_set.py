"""
Create evaluation test set for prompt optimization.
Selects 50 diverse sources from normalized/ directory.
"""

import os
import json
import shutil
from pathlib import Path

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NORMALIZED_DIR = os.path.join(_REPO_ROOT, 'raw', 'normalized')
EVAL_SET_DIR = os.path.join(_REPO_ROOT, 'eval_set')
EVAL_SET_INDEX = os.path.join(_REPO_ROOT, 'eval_set_index.json')


def create_eval_set(target_count=50):
    """Create evaluation test set by copying diverse sources."""
    
    # Create eval_set directory
    os.makedirs(EVAL_SET_DIR, exist_ok=True)
    
    # Find all normalized markdown files
    all_files = []
    for root, dirs, files in os.walk(NORMALIZED_DIR):
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, NORMALIZED_DIR)
                domain = rel_path.split(os.sep)[0] if os.sep in rel_path else 'unknown'
                all_files.append({
                    'path': full_path,
                    'rel_path': rel_path,
                    'domain': domain,
                    'filename': file
                })
    
    print(f"Found {len(all_files)} normalized files")
    
    # Group by domain for diversity
    by_domain = {}
    for f in all_files:
        domain = f['domain']
        by_domain.setdefault(domain, []).append(f)
    
    print(f"Domains: {list(by_domain.keys())}")
    
    # Select files (balanced across domains)
    selected = []
    domains = list(by_domain.keys())
    per_domain = target_count // len(domains) if domains else 0
    
    for domain in domains:
        files = by_domain[domain][:per_domain]
        selected.extend(files)
    
    # Fill remaining slots from largest domain
    if len(selected) < target_count and domains:
        largest_domain = max(by_domain.keys(), key=lambda d: len(by_domain[d]))
        remaining = target_count - len(selected)
        extra = by_domain[largest_domain][per_domain:per_domain + remaining]
        selected.extend(extra)
    
    selected = selected[:target_count]
    
    print(f"Selected {len(selected)} files for evaluation set")
    
    # Copy files to eval_set directory
    eval_index = []
    for idx, file_info in enumerate(selected):
        # Create subdirectory structure
        domain_dir = os.path.join(EVAL_SET_DIR, file_info['domain'])
        os.makedirs(domain_dir, exist_ok=True)
        
        # Copy file
        dest_path = os.path.join(domain_dir, file_info['filename'])
        shutil.copy2(file_info['path'], dest_path)
        
        # Add to index
        eval_index.append({
            'id': idx + 1,
            'domain': file_info['domain'],
            'filename': file_info['filename'],
            'original_path': file_info['rel_path'],
            'eval_path': os.path.relpath(dest_path, _REPO_ROOT)
        })
        
        print(f"  [{idx+1:2d}] {file_info['domain']:15s} {file_info['filename']}")
    
    # Save index
    with open(EVAL_SET_INDEX, 'w', encoding='utf-8') as f:
        json.dump({
            'created': '2026-04-05',
            'count': len(eval_index),
            'purpose': 'Fixed evaluation set for prompt optimization',
            'files': eval_index
        }, f, indent=2)
    
    print(f"\n✓ Evaluation set created:")
    print(f"  - {len(eval_index)} files")
    print(f"  - Index: {EVAL_SET_INDEX}")
    print(f"  - Directory: {EVAL_SET_DIR}")
    
    # Domain distribution
    domain_counts = {}
    for item in eval_index:
        domain_counts[item['domain']] = domain_counts.get(item['domain'], 0) + 1
    
    print(f"\n  Domain distribution:")
    for domain, count in sorted(domain_counts.items()):
        print(f"    {domain:15s}: {count:2d} files")
    
    return eval_index


if __name__ == '__main__':
    create_eval_set(target_count=50)
