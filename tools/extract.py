import sys
import os
import json
from common import write_log, parse_frontmatter, call_local_model

def extract_knowledge(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    meta, body = parse_frontmatter(content)
    
    system_prompt = "You are a data extractor. Output ONLY valid JSON containing 'entities' (list of {'name': str, 'type': str}) and 'claims' (list of {'text': str, 'confidence': float}). Do not output markdown code blocks."
    
    input_text = f"Extract intelligence from this text:\n\n{body}"
    
    content_out = call_local_model(system_prompt, input_text)
    
    try:
        if content_out.startswith("```json"):
            content_out = content_out.strip("```json").strip("```").strip()
        elif content_out.startswith("```"):
            content_out = content_out.strip("```").strip()
            
        extracted = json.loads(content_out)
    except Exception as e:
        print(f"Warning: JSON parsing failed ({e}). Raw Output: {content_out[:100]}...")
        extracted = {
            "entities": [{"name": "FallbackEntity", "type": "model"}],
            "claims": [{"text": "Failed parsing. See logs.", "confidence": 0.0}]
        }
        
    extracted["source_id"] = meta.get("id", "unknown")
    
    output_path = filepath + ".json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted, f, indent=2)
        
    write_log('extract', 'llm extraction', f"Extracted from {filename}")
    print(f"Extracted knowledge saved to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python extract.py [filepath]")
        sys.exit(1)
    extract_knowledge(sys.argv[1])
