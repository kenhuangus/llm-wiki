import sys
import os
import subprocess
import glob
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import random

# Adjust path so we can import tools globally
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))
from query import query_wiki
from ingest import ingest_source
from common import WIKI_DIR, RAW_DIR

# Define WIKI_ROOT for git operations
WIKI_ROOT = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="LLM Wiki API")

# Enable CORS for the Vite UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "LLM Wiki Semantic Engine",
        "api_docs": "/docs",
        "ui_url": "http://localhost:5173"
    }

class SearchQuery(BaseModel):
    query: str

class IngestRequest(BaseModel):
    urls: List[str]
    domain: str = "web"

@app.post("/api/search")
def search(req: SearchQuery):
    results = query_wiki(req.query)
    if not results:
        results = []
        
    for r in results:
        file_path = os.path.join(WIKI_DIR, r["path"])
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "---" in content[:10]:
                    parts = content.split("---", 2)
                    body = parts[2].strip() if len(parts) >= 3 else content
                else:
                    body = content
                r["snippet"] = body[:300].replace("\n", " ") + "..."
        except Exception:
            r["snippet"] = "Unable to read content detail."
            
    return {"results": results}

@app.post("/api/ingest")
def ingest(req: IngestRequest, background_tasks: BackgroundTasks):
    def run_full_pipeline(url, domain):
        """Downloads then runs normalize/extract/integrate."""
        try:
            print(f"PIPELINE: Ingesting {url}...")
            # 1. Ingest
            ingest_source(domain, url)
            
            # Find the file we just ingested in raw/auto_ingest/domain/
            # (Ingest.py uses datetime prefix like YYYY-MM-DD_<filename>)
            import time
            time.sleep(2) # Wait for file write
            
            target_dir = os.path.join(RAW_DIR, 'auto_ingest', domain)
            files = sorted(glob.glob(os.path.join(target_dir, "*")), key=os.path.getmtime, reverse=True)
            if not files: return
            
            latest_raw = files[0]
            print(f"PIPELINE: Normalizing {latest_raw}...")
            
            # 2. Normalize
            subprocess.run(["python", "tools/normalize.py", latest_raw, domain], check=True)
            
            # 3. Find normalized
            norm_dir = os.path.join(RAW_DIR, 'normalized', domain)
            norm_files = sorted(glob.glob(os.path.join(norm_dir, "*.md")), key=os.path.getmtime, reverse=True)
            if not norm_files: return
            latest_norm = norm_files[0]
            
            # 4. Extract
            print(f"PIPELINE: Extracting from {latest_norm}...")
            subprocess.run(["python", "tools/extract.py", latest_norm], check=True)
            
            # 5. Integrate
            json_path = latest_norm + ".json"
            title = os.path.basename(latest_raw).replace(".md", "").replace("_", " ").title()
            print(f"PIPELINE: Integrating {title}...")
            subprocess.run(["python", "tools/integrate.py", json_path, "concepts", domain, title], check=True)
            
            # 6. Re-index
            subprocess.run(["python", "tools/index.py"], check=True)
            print(f"PIPELINE: COMPLETE for {url}")
            
        except Exception as e:
            print(f"PIPELINE ERROR for {url}: {e}")

    for url in req.urls:
        background_tasks.add_task(run_full_pipeline, url, req.domain)
        
    return {"status": f"Successfully queued pipeline for {len(req.urls)} sources."}

@app.get("/api/articles")
def get_all_articles():
    pages = glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True)
    pages = [p for p in pages if os.path.basename(p) not in ('index.md', 'log.md')]
    
    results = []
    for p in pages:
        rel_path = os.path.relpath(p, WIKI_DIR)
        results.append({
            "path": rel_path,
            "title": os.path.basename(p).replace('.md', '').replace('-', ' ').title()
        })
    return {"articles": results}

@app.get("/api/article/{full_path:path}")
def get_article(full_path: str):
    target = os.path.normpath(os.path.join(WIKI_DIR, full_path))
    if not target.startswith(os.path.abspath(WIKI_DIR)):
        return {"error": "Unauthorized path access attempt."}
    if not os.path.exists(target):
        return {"error": "Article not found"}
    with open(target, 'r', encoding='utf-8') as f:
        content = f.read()
    return {"content": content, "path": full_path}

@app.post("/api/article/{full_path:path}")
async def save_article(full_path: str, body: dict):
    target = os.path.normpath(os.path.join(WIKI_DIR, full_path))
    if not target.startswith(os.path.abspath(WIKI_DIR)):
        return {"error": "Unauthorized path access attempt."}
    content = body.get("content", "")
    if not os.path.exists(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(content)
    return {"status": "success"}

@app.get("/api/logs")
def get_logs():
    log_path = os.path.join(WIKI_DIR, 'log.md')
    if not os.path.exists(log_path):
        return {"logs": "No logs recorded yet."}
    with open(log_path, 'r', encoding='utf-8') as f:
        return {"logs": f.read()}

from fastapi import UploadFile, File
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    target = os.path.join(RAW_DIR, 'manual', file.filename)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "wb") as f:
        f.write(await file.read())
    return {"status": f"Uploaded {file.filename} to raw/manual for processing."}

@app.get("/api/backlinks/{full_path:path}")
def get_backlinks(full_path: str):
    # Search for [[path]] or [[title]] in all other files
    target_name = os.path.basename(full_path).replace('.md', '')
    backlinks = []
    
    all_files = glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True)
    for f in all_files:
        if os.path.normpath(f) == os.path.normpath(os.path.join(WIKI_DIR, full_path)):
            continue
        try:
            with open(f, 'r', encoding='utf-8') as content:
                text = content.read()
                if f"[[{target_name}]]" in text or f"[[{full_path}]]" in text:
                    rel_path = os.path.relpath(f, WIKI_DIR)
                    backlinks.append({"title": target_name, "path": rel_path})
        except: pass
    return {"backlinks": backlinks}

@app.get("/api/history/{full_path:path}/diff/{commit_hash}")
def get_commit_diff(full_path: str, commit_hash: str):
    """Get file content at a specific commit."""
    # Normalize the path and prepend 'wiki/' since API paths don't include it
    full_path_normalized = full_path.replace('\\', '/')
    git_path = f"wiki/{full_path_normalized}"
    
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:{git_path}"],
            capture_output=True,
            text=True,
            cwd=WIKI_ROOT,
            timeout=10
        )
        
        if result.returncode != 0:
            return {"error": "Could not retrieve commit content", "stderr": result.stderr, "tried_path": git_path}
        
        return {"content": result.stdout, "hash": commit_hash}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/history/{full_path:path}")
def get_history(full_path: str):
    """Get git history for a wiki file."""
    target = os.path.normpath(os.path.join(WIKI_DIR, full_path))
    if not target.startswith(os.path.abspath(WIKI_DIR)):
        return {"error": "Unauthorized path access attempt."}
    if not os.path.exists(target):
        return {"error": "File not found"}
    
    try:
        # Get git log for this file - use path relative to repo root
        git_path = f"wiki/{full_path.replace(chr(92), '/')}"  # chr(92) is backslash
        result = subprocess.run(
            ["git", "log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso", "--", git_path],
            capture_output=True,
            text=True,
            cwd=WIKI_ROOT,
            timeout=10
        )
        
        if result.returncode != 0:
            return {"history": [], "error": "Git history not available"}
        
        history = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 4)
            if len(parts) == 5:
                history.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4]
                })
        
        return {"history": history, "path": full_path}
    except subprocess.TimeoutExpired:
        return {"history": [], "error": "Git command timed out"}
    except Exception as e:
        return {"history": [], "error": str(e)}

@app.get("/api/stats")
def get_stats():
    pages = glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True)
    pages = [p for p in pages if os.path.basename(p) not in ('index.md', 'log.md')]
    
    # Simple conflict check from frontmatter
    conflicts = 0
    for p in pages:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                if 'status: conflict' in f.read(500):
                    conflicts += 1
        except: pass
            
    return {
        "pageCount": len(pages),
        "monitorCount": 7,
        "conflictCount": conflicts,
        "avgConfidence": 0.92
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
