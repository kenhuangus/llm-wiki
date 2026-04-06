#!/usr/bin/env python3
"""Check RSS ingestion state."""

import sqlite3
from datetime import datetime

conn = sqlite3.connect('state.db')

# Count by source
print("=" * 60)
print("Ingested Items by Source")
print("=" * 60)
cur = conn.execute('SELECT source, COUNT(*) FROM ingested_ids GROUP BY source')
for row in cur.fetchall():
    print(f"{row[0]:20s}: {row[1]:4d} items")

# Recent RSS items
print("\n" + "=" * 60)
print("Recent RSS Items (Last 10)")
print("=" * 60)
cur = conn.execute('''
    SELECT item_id, ingested_at 
    FROM ingested_ids 
    WHERE source = "rss" 
    ORDER BY ingested_at DESC 
    LIMIT 10
''')
for row in cur.fetchall():
    item_id = row[0][:70]
    timestamp = row[1]
    print(f"{timestamp}: {item_id}")

# Option to clear RSS state
print("\n" + "=" * 60)
print("Options")
print("=" * 60)
print("To clear RSS state and re-ingest:")
print("  python -c \"import sqlite3; conn = sqlite3.connect('state.db'); conn.execute('DELETE FROM ingested_ids WHERE source=\\\"rss\\\"'); conn.commit(); print('Cleared RSS state')\"")
print("\nTo re-run RSS monitor:")
print("  python tools/rss_monitor.py")

conn.close()
