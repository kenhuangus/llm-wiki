import os
import json
import yaml
import hashlib
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load .env from the repo root (parent of tools/)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_REPO_ROOT, '.env'))

WIKI_ROOT = _REPO_ROOT
WIKI_DIR = os.path.join(WIKI_ROOT, 'wiki')
RAW_DIR = os.path.join(WIKI_ROOT, 'raw')

# ── LLM config (all from .env) ──────────────────────────────────────────────
LLM_MAIN_URL    = os.environ.get("LLM_MAIN_URL",   "http://ken-mac.local:1234/v1/chat/completions")
LLM_MAIN_MODEL  = os.environ.get("LLM_MAIN_MODEL", "google/gemma-4-26b-a4b:3")
LLM_MAIN_KEY    = os.environ.get("LLM_MAIN_API_KEY", "lm-studio")

LLM_BACK_URL    = os.environ.get("LLM_BACKUP_URL",  "http://localhost:1234/v1/chat/completions")
LLM_BACK_MODEL  = os.environ.get("LLM_BACKUP_MODEL", "gemma-4-e2b-it")
LLM_BACK_KEY    = os.environ.get("LLM_BACKUP_API_KEY", "lm-studio")

# ── Monitor config ────────────────────────────────────────────────────────────
ARXIV_MAX_RESULTS = int(os.environ.get("ARXIV_MAX_RESULTS", "3"))
ARXIV_CATEGORIES  = os.environ.get("ARXIV_CATEGORIES", "cs.AI,cs.CR,cs.RO,cs.LG").split(",")
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPOS      = [r.strip() for r in os.environ.get("GITHUB_REPOS", "langchain-ai/langchain,openai/openai-python,anthropics/anthropic-sdk-python").split(",") if r.strip()]
CVE_FEED_URL      = os.environ.get("CVE_FEED_URL", "https://services.nvd.nist.gov/rest/json/cves/2.0")
CVE_MAX_RESULTS   = int(os.environ.get("CVE_MAX_RESULTS", "5"))
NVD_API_KEY       = os.environ.get("NVD_API_KEY", "")
RSS_FEEDS         = [r.strip() for r in os.environ.get("RSS_FEEDS", "").split(",") if r.strip()]

# ── Helpers ───────────────────────────────────────────────────────────────────

def write_log(action, description, details=""):
    log_file = os.path.join(WIKI_DIR, 'log.md')
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"## [{timestamp}] {action} | {description} | {details}\n"
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("# Operation Log\n\n")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)


def get_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:8]


def parse_frontmatter(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return metadata, body
            except yaml.YAMLError:
                pass
    return {}, content


def serialize_frontmatter(metadata, body):
    yaml_header = yaml.dump(metadata, sort_keys=False)
    return f"---\n{yaml_header}---\n\n{body}"


def call_local_model(system_prompt, input_text):
    """
    Attempts Ken-Mac (Main) then Localhost (Backup) for synthesis.
    Correctly maps to OpenAI-compatible Chat Completions payload.
    """
    targets = [
        (LLM_MAIN_URL, LLM_MAIN_MODEL, LLM_MAIN_KEY, "Ken-Mac (Main)"),
        (LLM_BACK_URL, LLM_BACK_MODEL, LLM_BACK_KEY, "Local-PC (Backup)")
    ]

    for url, model, key, label in targets:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ],
            "temperature": 0.7
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        
        try:
            print(f"PIPELINE: Attempting synthesis via {label}...")
            response = requests.post(url, headers=headers, json=payload, timeout=300)
            data = response.json()
            
            # OpenAI / LM-Studio response parsing
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"].get("content", "")
                if content: 
                   print(f"PIPELINE: {label} SUCCESS.")
                   return content
            
            # fallback case if response is empty
            print(f"[WARN] {label} returned empty choices. Trying next node.")
            
        except Exception as e:
            print(f"[FAIL] {label} unreachable: {e}")
            continue # Try next target

    print("ERROR: All LLM nodes failed.")
    return ""
