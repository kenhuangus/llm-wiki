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
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:1234/api/v1/chat")
LLM_MODEL    = os.environ.get("LLM_MODEL",    "gemma-4-e2b-it")
LLM_API_KEY  = os.environ.get("LLM_API_KEY",  "lm-studio")

# ── Monitor config ────────────────────────────────────────────────────────────
ARXIV_MAX_RESULTS = int(os.environ.get("ARXIV_MAX_RESULTS", "3"))
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")
CVE_FEED_URL      = os.environ.get("CVE_FEED_URL", "https://cve.circl.lu/api/last")
CVE_MAX_RESULTS   = int(os.environ.get("CVE_MAX_RESULTS", "3"))

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
    Calls the configured local LLM endpoint.
    All connection details come from .env — nothing is hardcoded here.
    """
    payload = {
        'model': LLM_MODEL,
        'system_prompt': system_prompt,
        'input': input_text,
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LLM_API_KEY}',
    }
    try:
        response = requests.post(LLM_BASE_URL, headers=headers, json=payload, timeout=60)
        data = response.json()
        if 'output' in data and len(data['output']) > 0:
            return data['output'][0].get('content', '')
        return ''
    except Exception as e:
        print(f'LLM call failed: {e}')
        return ''
