"""
watchdog_monitor.py — Auto-trigger normalize + extract + integrate
whenever a new file appears in raw/manual/.

Usage:
    python tools/watchdog_monitor.py

Requires: pip install watchdog
"""
import sys
import os
import time
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write_log, RAW_DIR, WIKI_ROOT

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Missing dependency. Run: pip install watchdog")
    sys.exit(1)

MANUAL_DIR = os.path.join(RAW_DIR, "manual")
TOOLS_DIR = os.path.join(WIKI_ROOT, "tools")

# Default domain for manually dropped files unless overridden
DEFAULT_DOMAIN = "agentic-ai"


def run_pipeline(filepath):
    """Run normalize → extract → integrate for a dropped file."""
    filename = os.path.basename(filepath)
    print(f"\n[watchdog] New file detected: {filename}")
    write_log("watchdog", "detected", filepath)

    def run(cmd):
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=WIKI_ROOT)
        if result.returncode != 0:
            print(f"  [ERROR] {' '.join(cmd)}: {result.stderr.strip()}")
            write_log("watchdog_error", cmd[-1], result.stderr.strip()[:200])
        else:
            print(f"  [OK] {' '.join(cmd[-2:])}")
        return result.returncode == 0

    # Step 1: Normalize
    normalized_dir = os.path.join(RAW_DIR, "normalized", DEFAULT_DOMAIN)
    os.makedirs(normalized_dir, exist_ok=True)
    if not run(["python", os.path.join(TOOLS_DIR, "normalize.py"), filepath, DEFAULT_DOMAIN]):
        return

    # Step 2: Find the newest normalized file
    import glob
    files = sorted(
        glob.glob(os.path.join(normalized_dir, "*.md")),
        key=os.path.getctime,
        reverse=True
    )
    if not files:
        print("  [ERROR] No normalized file found.")
        return
    normalized = files[0]

    # Step 3: Extract
    if not run(["python", os.path.join(TOOLS_DIR, "extract.py"), normalized]):
        return
    json_path = normalized + ".json"

    # Step 4: Integrate
    title = os.path.splitext(filename)[0].replace("_", " ").title()
    run(["python", os.path.join(TOOLS_DIR, "integrate.py"),
         json_path, "concepts", DEFAULT_DOMAIN, title])

    # Step 5: Rebuild index
    run(["python", os.path.join(TOOLS_DIR, "index.py")])

    write_log("watchdog", "pipeline_complete", filename)
    print(f"[watchdog] Pipeline complete for: {filename}")


class ManualDropHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        # Wait briefly for file write to finish
        time.sleep(1)
        run_pipeline(event.src_path)


def main():
    os.makedirs(MANUAL_DIR, exist_ok=True)
    print(f"Watching {MANUAL_DIR} for new files...")
    print("Drop any .md, .txt, or .pdf file there to trigger the pipeline automatically.")
    print("Press Ctrl+C to stop.\n")

    observer = Observer()
    observer.schedule(ManualDropHandler(), MANUAL_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
