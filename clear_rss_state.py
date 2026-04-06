#!/usr/bin/env python3
"""Clear RSS state to allow re-ingestion."""

import sqlite3

conn = sqlite3.connect('state.db')
cur = conn.execute('DELETE FROM ingested_ids WHERE source = "rss"')
conn.commit()
deleted = cur.rowcount
conn.close()

print(f"✅ Cleared {deleted} RSS items from state database")
print("Ready for fresh ingestion!")
print("\nRun: python tools/rss_monitor.py")
