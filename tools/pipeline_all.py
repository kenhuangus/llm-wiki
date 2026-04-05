"""
pipeline_all.py — Total Ingestion + Semantic Transformation
Runs all monitors then processes all new raw ingestion files through the LLM pipeline.

Usage:
    python tools/pipeline_all.py
"""
import os
import sys
import glob
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RAW_DIR, write_log

def run_command(cmd_list):
    print(f"RUNNING: {' '.join(cmd_list)}")
    try:
        subprocess.run(cmd_list, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAILED: {' '.join(cmd_list)} - {e}")
        return False

def main():
    print(f"\n============================================================")
    print(f"  STARTING FULL LLM WIKI PIPELINE — {datetime.now().strftime('%H:%M:%S')}")
    print(f"============================================================\n")

    # 1. Run all monitors to fetch raw data
    print("STEP 1: Polling monitors (arXiv, CVE, GitHub, RSS, Curated)...")
    monitors = ["arxiv", "cve", "github", "rss", "curated"]
    for mon in monitors:
        run_command(["python", f"tools/{mon}_monitor.py"])

    # 2. Find all un-normalized files in raw/auto_ingest/
    print("\nSTEP 2: Normalizing freshly ingested raw documents...")
    raw_files = glob.glob(os.path.join(RAW_DIR, 'auto_ingest', '**', '*.*'), recursive=True)
    # Exclude directories
    raw_files = [f for f in raw_files if os.path.isfile(f)]
    
    for rf in raw_files:
        # Determine domain from parent directory
        domain = os.path.basename(os.path.dirname(rf))
        run_command(["python", "tools/normalize.py", rf, domain])

    # 3. Process all normalized files that haven't been extracted yet
    print("\nSTEP 3: Running Semantic Extraction on new normalized files...")
    norm_files = glob.glob(os.path.join(RAW_DIR, 'normalized', '**', '*.md'), recursive=True)
    for nf in norm_files:
        json_path = nf + ".json"
        if not os.path.exists(json_path):
            run_command(["python", "tools/extract.py", nf])

    # 4. Integrate all extracted knowledge into the wiki folders
    print("\nSTEP 4: Integrating extracted knowledge into Obsidian Vault...")
    json_files = glob.glob(os.path.join(RAW_DIR, 'normalized', '**', '*.json'), recursive=True)
    for jf in json_files:
        # Avoid double integration if marked?
        # For simplicity, we just integrate. integrate.py handles deep merging.
        domain = os.path.basename(os.path.dirname(jf))
        # Simple title guessing
        title = os.path.basename(jf).replace(".md.json", "").title()
        # Fixed path_type for now: concepts or entities depending on domain
        path_type = "entities" if domain in ["github", "cve"] else "concepts"
        run_command(["python", "tools/integrate.py", jf, path_type, domain, title])

    # 5. Final Re-index
    print("\nSTEP 5: Rebuilding semantic BM25 index...")
    run_command(["python", "tools/index.py"])

    print(f"\n============================================================")
    print(f"  FULL PIPELINE COMPLETE — {datetime.now().strftime('%H:%M:%S')}")
    print(f"============================================================\n")
    write_log("pipeline_all", "complete", f"Successfully processed raw files batch.")

if __name__ == "__main__":
    main()
