"""
Autonomous orchestration daemon for continuous wiki processing.
Runs 24/7: ingest → normalize → extract → integrate → lint → index
"""

import os
import sys
import time
import signal
from queue import PriorityQueue
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import json

# Add tools to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import write_log, WIKI_ROOT, RAW_DIR
from metrics_collector import MetricsCollector, record_extraction_success, record_extraction_failure

# Priority levels
PRIORITY_CRITICAL = 0  # CVSS ≥ 9.0
PRIORITY_HIGH = 1      # CVSS ≥ 7.0
PRIORITY_NORMAL = 2    # Regular sources
PRIORITY_LOW = 3       # Retry queue

# Daemon configuration
POLL_INTERVAL = 300  # 5 minutes between monitor polls
LINT_INTERVAL = 3600  # 1 hour between lint runs
INDEX_INTERVAL = 1800  # 30 minutes between index rebuilds


class WikiDaemon:
    """Autonomous orchestration daemon."""
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.metrics = MetricsCollector()
        self.running = True
        self.last_lint = 0
        self.last_index = 0
        self.processed_count = 0
        self.failure_count = 0
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        write_log('daemon', 'started', 'WikiDaemon initialized')
        print("🤖 WikiDaemon started")
        print(f"   Poll interval: {POLL_INTERVAL}s")
        print(f"   Lint interval: {LINT_INTERVAL}s")
        print(f"   Index interval: {INDEX_INTERVAL}s")
    
    def shutdown(self, signum, frame):
        """Graceful shutdown handler."""
        print("\n🛑 Shutdown signal received, finishing current task...")
        self.running = False
        write_log('daemon', 'shutdown', f'Processed: {self.processed_count}, Failures: {self.failure_count}')
    
    def detect_domain(self, source_path: str) -> str:
        """Detect domain from source path."""
        path_lower = source_path.lower()
        
        # Check path components
        if 'arxiv' in path_lower:
            return 'arxiv'
        elif 'cve' in path_lower:
            return 'cve'
        elif 'github' in path_lower:
            return 'github'
        elif 'rss' in path_lower or 'blog' in path_lower or 'news' in path_lower:
            return 'rss'
        elif 'curated' in path_lower:
            return 'curated'
        elif 'manual' in path_lower:
            return 'manual'
        elif 'web' in path_lower:
            return 'web'
        else:
            return 'general'
    
    def run(self):
        """Main daemon loop."""
        while self.running:
            try:
                # 1. Poll monitors for new sources
                self.poll_monitors()
                
                # 2. Process queue (highest priority first)
                processed_this_cycle = 0
                while not self.queue.empty() and processed_this_cycle < 10:
                    priority, source_path = self.queue.get()
                    self.process_source(source_path, priority)
                    processed_this_cycle += 1
                
                # 3. Periodic maintenance
                current_time = time.time()
                
                if current_time - self.last_lint > LINT_INTERVAL:
                    self.run_lint()
                    self.last_lint = current_time
                
                if current_time - self.last_index > INDEX_INTERVAL:
                    self.rebuild_index()
                    self.last_index = current_time
                
                # 4. Status report
                if self.processed_count % 10 == 0 and self.processed_count > 0:
                    self.print_status()
                
                # 5. Sleep until next cycle
                if self.queue.empty():
                    print(f"💤 Queue empty, sleeping for {POLL_INTERVAL}s...")
                    time.sleep(POLL_INTERVAL)
                else:
                    time.sleep(1)  # Quick cycle if queue has items
                    
            except KeyboardInterrupt:
                self.shutdown(None, None)
                break
            except Exception as e:
                print(f"❌ Daemon error: {e}")
                write_log('daemon_error', 'exception', str(e))
                time.sleep(60)  # Wait before retry
        
        # Cleanup
        self.metrics.close()
        print("👋 WikiDaemon stopped")
    
    def poll_monitors(self):
        """Poll all monitors for new sources."""
        monitors = [
            'arxiv_monitor.py',
            'cve_monitor.py',
            'github_monitor.py',
            'rss_monitor.py'
        ]
        
        for monitor in monitors:
            try:
                monitor_path = os.path.join(os.path.dirname(__file__), monitor)
                if os.path.exists(monitor_path):
                    print(f"📡 Polling {monitor}...")
                    result = subprocess.run(
                        [sys.executable, monitor_path],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        # Check for new files in auto_ingest
                        self.scan_auto_ingest()
                    else:
                        print(f"⚠️  {monitor} failed: {result.stderr[:100]}")
                        
            except subprocess.TimeoutExpired:
                print(f"⏱️  {monitor} timed out")
            except Exception as e:
                print(f"❌ Error polling {monitor}: {e}")
    
    def scan_auto_ingest(self):
        """Scan auto_ingest directory for new sources."""
        auto_ingest_dir = os.path.join(RAW_DIR, 'auto_ingest')
        
        for root, dirs, files in os.walk(auto_ingest_dir):
            for file in files:
                if file.endswith('.md'):
                    source_path = os.path.join(root, file)
                    
                    # Check if already processed (has .json file)
                    json_path = source_path + '.json'
                    if os.path.exists(json_path):
                        continue
                    
                    # Determine priority based on source type
                    priority = self.get_priority(source_path)
                    
                    # Add to queue
                    self.queue.put((priority, source_path))
                    print(f"📥 Queued: {os.path.basename(source_path)} (priority: {priority})")
    
    def get_priority(self, source_path: str) -> int:
        """Determine priority based on source type and content."""
        # Check if CVE
        if 'cve' in source_path.lower():
            # Try to extract CVSS score
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Look for CVSS score
                    if 'CVSS' in content or 'cvss' in content:
                        # Simple heuristic: look for numbers after CVSS
                        import re
                        cvss_match = re.search(r'CVSS[:\s]+(\d+\.?\d*)', content, re.IGNORECASE)
                        if cvss_match:
                            cvss_score = float(cvss_match.group(1))
                            if cvss_score >= 9.0:
                                return PRIORITY_CRITICAL
                            elif cvss_score >= 7.0:
                                return PRIORITY_HIGH
            except Exception:
                pass
            
            return PRIORITY_HIGH  # Default for CVEs
        
        return PRIORITY_NORMAL
    
    def process_source(self, source_path: str, priority: int):
        """Full pipeline: normalize → extract → integrate → index."""
        filename = os.path.basename(source_path)
        print(f"\n🔄 Processing: {filename} (priority: {priority})")
        
        try:
            # Step 1: Normalize (if not already normalized)
            normalized_path = self.normalize_source(source_path)
            if not normalized_path:
                print(f"⚠️  Normalization skipped or failed")
                return
            
            # Step 2: Extract
            extracted_path = self.extract_knowledge(normalized_path)
            if not extracted_path:
                print(f"❌ Extraction failed")
                self.failure_count += 1
                return
            
            # Step 3: Integrate
            integrated = self.integrate_knowledge(extracted_path)
            if not integrated:
                print(f"⚠️  Integration failed")
                self.failure_count += 1
                return
            
            # Step 4: Record success
            self.processed_count += 1
            print(f"✅ Processed successfully ({self.processed_count} total)")
            
            # Step 5: Critical escalation if needed
            if priority == PRIORITY_CRITICAL:
                self.escalate_critical(source_path)
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            write_log('daemon_error', 'process_source', f"{filename}: {e}")
            self.failure_count += 1
            
            # Retry with lower priority
            if priority < PRIORITY_LOW:
                self.queue.put((PRIORITY_LOW, source_path))
    
    def normalize_source(self, source_path: str) -> str:
        """Run normalization on source."""
        # Check if already normalized
        if 'normalized' in source_path:
            return source_path
        
        try:
            # Detect domain from path
            domain = self.detect_domain(source_path)
            
            result = subprocess.run(
                [sys.executable, 'tools/normalize.py', source_path, domain],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                # Parse output to find normalized file path
                output = result.stdout.strip()
                for line in output.split('\n'):
                    if line.startswith('Normalized:'):
                        normalized_path = line.split('Normalized:')[1].strip()
                        return normalized_path
                
                # Fallback: look for the file in normalized directory
                from common import get_hash
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                file_id = get_hash(content)
                normalized_path = os.path.join(RAW_DIR, 'normalized', domain, f"{file_id}.md")
                if os.path.exists(normalized_path):
                    return normalized_path
                
                print(f"⚠️  Normalized file not found")
                return None
            else:
                print(f"⚠️  Normalize error: {result.stderr[:100]}")
                return None
                
        except Exception as e:
            print(f"❌ Normalize exception: {e}")
            return None
    
    def extract_knowledge(self, normalized_path: str) -> str:
        """Run extraction on normalized source."""
        try:
            result = subprocess.run(
                [sys.executable, 'tools/extract.py', normalized_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                json_path = normalized_path + '.json'
                if os.path.exists(json_path):
                    # Record metrics
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        record_extraction_success(os.path.basename(normalized_path), data)
                    return json_path
                else:
                    print(f"⚠️  JSON file not found: {json_path}")
                    return None
            else:
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                print(f"❌ Extract error: {error_msg}")
                record_extraction_failure(os.path.basename(normalized_path), error_msg)
                return None
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  Extraction timed out")
            record_extraction_failure(os.path.basename(normalized_path), "Timeout")
            return None
        except Exception as e:
            print(f"❌ Extract exception: {e}")
            record_extraction_failure(os.path.basename(normalized_path), str(e))
            return None
    
    def integrate_knowledge(self, json_path: str) -> bool:
        """Run integration on extracted JSON."""
        try:
            # For now, use default category/subcategory
            # TODO: Determine from source metadata
            result = subprocess.run(
                [sys.executable, 'tools/integrate.py', json_path, 
                 'concepts', 'agentic-ai', 'test-integration'],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"⚠️  Integrate error: {result.stderr[:100]}")
                return False
                
        except Exception as e:
            print(f"❌ Integrate exception: {e}")
            return False
    
    def run_lint(self):
        """Run lightweight lint check."""
        print("\n🔍 Running lint check...")
        try:
            result = subprocess.run(
                [sys.executable, 'tools/lint.py'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ Lint passed")
            else:
                print(f"⚠️  Lint warnings: {result.stdout[:200]}")
                
        except Exception as e:
            print(f"❌ Lint error: {e}")
    
    def rebuild_index(self):
        """Rebuild wiki index."""
        print("\n📚 Rebuilding index...")
        try:
            result = subprocess.run(
                [sys.executable, 'tools/index.py'],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                print("✅ Index rebuilt")
            else:
                print(f"⚠️  Index error: {result.stderr[:100]}")
                
        except Exception as e:
            print(f"❌ Index error: {e}")
    
    def escalate_critical(self, source_path: str):
        """Escalate critical CVE to human."""
        alert_path = os.path.join(WIKI_ROOT, 'CRITICAL_ALERT.md')
        
        with open(alert_path, 'w', encoding='utf-8') as f:
            f.write(f"# CRITICAL ALERT\n\n")
            f.write(f"**Date:** {datetime.now(timezone.utc).isoformat()}\n\n")
            f.write(f"**Source:** {source_path}\n\n")
            f.write(f"**Reason:** CVSS ≥ 9.0 CVE detected\n\n")
            f.write(f"**Action Required:** Human review needed\n\n")
        
        write_log('daemon', 'critical_alert', f'CVSS ≥ 9.0: {os.path.basename(source_path)}')
        print(f"🚨 CRITICAL ALERT written to {alert_path}")
    
    def print_status(self):
        """Print daemon status."""
        print(f"\n📊 Status:")
        print(f"   Processed: {self.processed_count}")
        print(f"   Failures: {self.failure_count}")
        print(f"   Queue size: {self.queue.qsize()}")
        print(f"   Success rate: {(self.processed_count / (self.processed_count + self.failure_count) * 100) if (self.processed_count + self.failure_count) > 0 else 0:.1f}%")


def main():
    """Entry point for daemon."""
    print("=" * 60)
    print("  LLM Wiki Autonomous Daemon")
    print("  Phase 3: Continuous Knowledge Processing")
    print("=" * 60)
    print()
    
    daemon = WikiDaemon()
    daemon.run()


if __name__ == '__main__':
    main()
