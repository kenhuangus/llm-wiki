import sys
import os
import json
from datetime import datetime
from common import write_log, WIKI_DIR, serialize_frontmatter, parse_frontmatter, call_local_model
from prompts import get_integration_prompt

def integrate_knowledge(json_path, category, subcategory, title):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    target_path = os.path.join(WIKI_DIR, category, subcategory, f"{title.lower().replace(' ', '-')}.md")
    
    metadata = {
        'id': data.get('source_id', 'unknown'),
        'title': title,
        'domain': subcategory,
        'source_count': 1,
        'confidence': 0.8,
        'verified': False,
        'last_updated': datetime.now().strftime("%Y-%m-%d"),
        'status': 'current'
    }
    
    new_claims_body = "## Claims\n"
    for claim in data.get('claims', []):
        new_claims_body += f"- {claim['text']} (Confidence: {claim['confidence']}, Source: [[{data.get('source_id')}]])\n"
        
    if os.path.exists(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            exist_content = f.read()
            
        exist_meta, exist_body = parse_frontmatter(exist_content)
        metadata['id'] = exist_meta.get('id', metadata['id'])
        metadata['source_count'] = exist_meta.get('source_count', 0) + 1
        
        # Use externalized prompt from prompts.py
        system_prompt = get_integration_prompt()
        input_text = f"Old Claims:\n{exist_body}\n\nNew Claims:\n{new_claims_body}"
        
        merged_body_raw = call_local_model(system_prompt, input_text)
        
        if merged_body_raw:
            if "STATUS: CONFLICT" in merged_body_raw:
                metadata['status'] = 'conflict'
                merged_body_raw = merged_body_raw.replace("STATUS: CONFLICT", "").strip()
            merged_body = merged_body_raw
        else:
            merged_body = exist_body + "\n" + new_claims_body
    else:
        merged_body = new_claims_body
        
    merged = serialize_frontmatter(metadata, merged_body)
    
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(merged)
        
    write_log('integrate', 'merged knowledge', f"Updated {target_path} (Status: {metadata['status']})")
    print(f"Integrated into {target_path}")

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: python integrate.py [json] [cat] [subcat] [title]")
        sys.exit(1)
    integrate_knowledge(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
