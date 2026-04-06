"""
Test script for daemon priority queue.
Runs a single cycle to verify priority ordering.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from daemon import WikiDaemon

def test_priority_queue():
    """Test that daemon processes sources in correct priority order."""
    print("=" * 60)
    print("  Testing Daemon Priority Queue")
    print("=" * 60)
    print()
    
    daemon = WikiDaemon()
    
    # Scan for test sources
    print("📡 Scanning for test sources...")
    daemon.scan_auto_ingest()
    
    print(f"\n📊 Queue Status:")
    print(f"   Total items: {daemon.queue.qsize()}")
    
    # Show queue contents (peek without removing)
    queue_items = []
    while not daemon.queue.empty():
        priority, path = daemon.queue.get()
        queue_items.append((priority, os.path.basename(path)))
    
    # Re-add items
    for priority, basename in queue_items:
        # Reconstruct path (simplified)
        if 'cve' in basename:
            path = os.path.join('raw', 'auto_ingest', 'cve', basename)
        else:
            path = os.path.join('raw', 'auto_ingest', 'arxiv', basename)
        daemon.queue.put((priority, path))
    
    print(f"\n📋 Queue Contents (in priority order):")
    for priority, basename in sorted(queue_items):
        priority_name = {0: 'CRITICAL', 1: 'HIGH', 2: 'NORMAL', 3: 'LOW'}.get(priority, 'UNKNOWN')
        print(f"   [{priority}] {priority_name:10s} - {basename}")
    
    # Process one item to verify pipeline
    if not daemon.queue.empty():
        print(f"\n🔄 Processing highest priority item...")
        priority, source_path = daemon.queue.get()
        
        # Just test priority detection, don't run full pipeline
        detected_priority = daemon.get_priority(source_path)
        print(f"   Source: {os.path.basename(source_path)}")
        print(f"   Detected priority: {detected_priority}")
        print(f"   Expected: {priority}")
        
        if detected_priority == priority:
            print(f"   ✅ Priority detection correct!")
        else:
            print(f"   ⚠️  Priority mismatch!")
    
    daemon.metrics.close()
    print(f"\n✅ Test complete!")

if __name__ == '__main__':
    test_priority_queue()
