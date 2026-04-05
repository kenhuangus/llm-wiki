import os
import subprocess
import time

def run_cmd(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)
    return result.stdout

def main():
    # 1. Create a dummy test file
    print("\n--- 1. Set up test file ---")
    test_file_path = "raw_test_doc.md"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("# E2E Test Document\n\nThis is a major model release concerning GPT-5 with a CVSS 9.0 context.")
    print(f"Created {test_file_path}")

    # 2. Ingest
    print("\n--- 2. Ingest ---")
    res = run_cmd(f"python tools/ingest.py manual {test_file_path}")
    
    # Normally a date string gets prepended but for simplicity we assume the latest file in the dir
    import glob
    ingested_files = glob.glob(f"raw/auto_ingest/manual/*_{test_file_path}")
    if not ingested_files:
        print("Ingestion failed to produce expected file.")
        return
    ingested_file = ingested_files[0]
    
    # 3. Normalize
    print("\n--- 3. Normalize ---")
    res = run_cmd(f"python tools/normalize.py {ingested_file} agentic-ai")
    
    # Look for the generated output via hash
    normalized_files = glob.glob(f"raw/normalized/agentic-ai/*.md")
    # find the most recently created normalized file
    latest_normalized = max(normalized_files, key=os.path.getctime)
    
    # 4. Extract
    print("\n--- 4. Extract ---")
    res = run_cmd(f"python tools/extract.py {latest_normalized}")
    json_path = f"{latest_normalized}.json"
    
    # 5. Integrate
    print("\n--- 5. Integrate ---")
    res = run_cmd(f"python tools/integrate.py {json_path} entities models GPT-5-Eval")
    
    # 6. Lint
    print("\n--- 6. Lint ---")
    run_cmd("python tools/lint.py")
    
    # 7. Index
    print("\n--- 7. Index ---")
    run_cmd("python tools/index.py")
    
    # 8. Query
    print("\n--- 8. Query ---")
    run_cmd("python tools/query.py GPT-5-Eval")

    # Clean up test source
    os.remove(test_file_path)
    print("\n--- E2E Test Complete ---")

if __name__ == "__main__":
    main()
