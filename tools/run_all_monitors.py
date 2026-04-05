"""
run_all_monitors.py — Single entry point to run all ingestion monitors.

Runs each monitor in sequence with error isolation so one failure
doesn't block the others. Designed for cron/Task Scheduler.

Usage:
    python tools/run_all_monitors.py [--arxiv] [--cve] [--github] [--rss]
    (no flags = run all)
"""
import sys
import os
import importlib
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import write_log

MONITORS = {
    "arxiv":  ("arxiv_monitor",  "check_arxiv"),
    "cve":    ("cve_monitor",    "check_cve"),
    "github": ("github_monitor", "check_github"),
    "rss":    ("rss_monitor",    "check_rss"),
}


def run_monitor(name, module_name, func_name):
    print(f"\n{'='*60}")
    print(f"  Running: {name}  [{datetime.now().strftime('%H:%M:%S')}]")
    print(f"{'='*60}")
    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, func_name)
        fn()
        write_log("monitor_runner", name, "completed successfully")
    except Exception as e:
        msg = traceback.format_exc()
        write_log("monitor_runner", f"{name}_error", str(e))
        print(f"[ERROR] {name} failed: {e}")
        print(msg)


def main():
    flags = {k for k in MONITORS if f"--{k}" in sys.argv}
    to_run = flags if flags else set(MONITORS.keys())

    print(f"LLM Wiki Monitor Runner — {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"Running: {', '.join(sorted(to_run))}")

    for name in ["arxiv", "cve", "github", "rss"]:  # deterministic order
        if name in to_run:
            module_name, func_name = MONITORS[name]
            run_monitor(name, module_name, func_name)

    print(f"\n{'='*60}")
    print(f"  All monitors complete. [{datetime.now().strftime('%H:%M:%S')}]")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
