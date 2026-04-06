"""
Metrics collection system for tracking wiki quality over time.
Stores time-series data in SQLite for analysis and optimization.
"""

import sqlite3
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
import json

# Database path (repo root)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_DB_PATH = os.path.join(_REPO_ROOT, 'metrics.db')


class MetricsCollector:
    """Tracks system performance metrics over time."""
    
    def __init__(self, db_path: str = METRICS_DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize database schema if not exists."""
        self.conn = sqlite3.connect(self.db_path)
        
        # Extraction metrics table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                avg_confidence REAL,
                entity_count INTEGER,
                claim_count INTEGER,
                relationship_count INTEGER,
                json_valid BOOLEAN,
                error_message TEXT,
                prompt_version TEXT
            )
        """)
        
        # Integration metrics table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS integrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_path TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                conflict_detected BOOLEAN,
                claims_added INTEGER,
                confidence_delta REAL,
                source_count_delta INTEGER,
                prompt_version TEXT
            )
        """)
        
        # Prompt optimization experiments table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS prompt_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_number INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                prompt_type TEXT NOT NULL,
                hypothesis TEXT NOT NULL,
                old_version TEXT NOT NULL,
                new_version TEXT NOT NULL,
                baseline_confidence REAL,
                new_confidence REAL,
                baseline_conflict_rate REAL,
                new_conflict_rate REAL,
                baseline_json_valid_rate REAL,
                new_json_valid_rate REAL,
                decision TEXT NOT NULL,
                commit_hash TEXT,
                notes TEXT
            )
        """)
        
        # Research hypotheses table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS research_hypotheses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hypothesis_number INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                hypothesis_type TEXT NOT NULL,
                description TEXT NOT NULL,
                action TEXT NOT NULL,
                success_metric TEXT NOT NULL,
                result TEXT,
                pages_affected INTEGER,
                confidence_improvement REAL,
                decision TEXT,
                notes TEXT
            )
        """)
        
        # Daily summary table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT PRIMARY KEY,
                total_extractions INTEGER,
                avg_extraction_confidence REAL,
                total_integrations INTEGER,
                conflict_rate REAL,
                experiments_run INTEGER,
                experiments_kept INTEGER,
                wiki_page_count INTEGER,
                avg_wiki_confidence REAL,
                lint_pass_rate REAL
            )
        """)
        
        self.conn.commit()
    
    def record_extraction(self, source_id: str, metrics: Dict):
        """Log extraction quality metrics."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        self.conn.execute("""
            INSERT INTO extractions 
            (source_id, timestamp, avg_confidence, entity_count, claim_count, 
             relationship_count, json_valid, error_message, prompt_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source_id,
            timestamp,
            metrics.get('avg_confidence'),
            metrics.get('entity_count'),
            metrics.get('claim_count'),
            metrics.get('relationship_count', 0),
            metrics.get('json_valid', True),
            metrics.get('error_message'),
            metrics.get('prompt_version', 'V1')
        ))
        self.conn.commit()
    
    def record_integration(self, page_path: str, metrics: Dict):
        """Log integration outcomes."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        self.conn.execute("""
            INSERT INTO integrations 
            (page_path, timestamp, conflict_detected, claims_added, 
             confidence_delta, source_count_delta, prompt_version)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            page_path,
            timestamp,
            metrics.get('conflict_detected', False),
            metrics.get('claims_added', 0),
            metrics.get('confidence_delta', 0.0),
            metrics.get('source_count_delta', 1),
            metrics.get('prompt_version', 'V1')
        ))
        self.conn.commit()
    
    def record_prompt_experiment(self, experiment: Dict):
        """Log prompt optimization experiment."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        self.conn.execute("""
            INSERT INTO prompt_experiments 
            (experiment_number, timestamp, prompt_type, hypothesis, old_version, 
             new_version, baseline_confidence, new_confidence, baseline_conflict_rate, 
             new_conflict_rate, baseline_json_valid_rate, new_json_valid_rate, 
             decision, commit_hash, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            experiment.get('experiment_number'),
            timestamp,
            experiment.get('prompt_type'),
            experiment.get('hypothesis'),
            experiment.get('old_version'),
            experiment.get('new_version'),
            experiment.get('baseline_confidence'),
            experiment.get('new_confidence'),
            experiment.get('baseline_conflict_rate'),
            experiment.get('new_conflict_rate'),
            experiment.get('baseline_json_valid_rate'),
            experiment.get('new_json_valid_rate'),
            experiment.get('decision'),
            experiment.get('commit_hash'),
            experiment.get('notes')
        ))
        self.conn.commit()
    
    def record_research_hypothesis(self, hypothesis: Dict):
        """Log research hypothesis and outcome."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        self.conn.execute("""
            INSERT INTO research_hypotheses 
            (hypothesis_number, timestamp, hypothesis_type, description, action, 
             success_metric, result, pages_affected, confidence_improvement, 
             decision, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hypothesis.get('hypothesis_number'),
            timestamp,
            hypothesis.get('hypothesis_type'),
            hypothesis.get('description'),
            hypothesis.get('action'),
            hypothesis.get('success_metric'),
            hypothesis.get('result'),
            hypothesis.get('pages_affected'),
            hypothesis.get('confidence_improvement'),
            hypothesis.get('decision'),
            hypothesis.get('notes')
        ))
        self.conn.commit()
    
    def get_extraction_trend(self, days: int = 30) -> List[tuple]:
        """Get time series for extraction confidence."""
        cursor = self.conn.execute("""
            SELECT date(timestamp) as date, AVG(avg_confidence) as avg_conf
            FROM extractions
            WHERE timestamp > datetime('now', '-? days')
            AND json_valid = 1
            GROUP BY date(timestamp)
            ORDER BY date
        """, (days,))
        return cursor.fetchall()
    
    def get_integration_conflict_rate(self, days: int = 30) -> List[tuple]:
        """Get time series for integration conflict rate."""
        cursor = self.conn.execute("""
            SELECT date(timestamp) as date, 
                   SUM(CASE WHEN conflict_detected THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as conflict_rate
            FROM integrations
            WHERE timestamp > datetime('now', '-? days')
            GROUP BY date(timestamp)
            ORDER BY date
        """, (days,))
        return cursor.fetchall()
    
    def get_recent_failures(self, hours: int = 24) -> List[Dict]:
        """Get recent extraction failures for analysis."""
        cursor = self.conn.execute("""
            SELECT source_id, timestamp, error_message, prompt_version
            FROM extractions
            WHERE timestamp > datetime('now', '-? hours')
            AND json_valid = 0
            ORDER BY timestamp DESC
        """, (hours,))
        
        failures = []
        for row in cursor.fetchall():
            failures.append({
                'source_id': row[0],
                'timestamp': row[1],
                'error_message': row[2],
                'prompt_version': row[3]
            })
        return failures
    
    def get_baseline_metrics(self) -> Dict:
        """Get current baseline metrics for comparison."""
        # Avg extraction confidence (last 7 days)
        cursor = self.conn.execute("""
            SELECT AVG(avg_confidence)
            FROM extractions
            WHERE timestamp > datetime('now', '-7 days')
            AND json_valid = 1
        """)
        avg_confidence = cursor.fetchone()[0] or 0.72
        
        # Conflict rate (last 7 days)
        cursor = self.conn.execute("""
            SELECT SUM(CASE WHEN conflict_detected THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM integrations
            WHERE timestamp > datetime('now', '-7 days')
        """)
        conflict_rate = cursor.fetchone()[0] or 12.0
        
        # JSON valid rate (last 7 days)
        cursor = self.conn.execute("""
            SELECT SUM(CASE WHEN json_valid THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM extractions
            WHERE timestamp > datetime('now', '-7 days')
        """)
        json_valid_rate = cursor.fetchone()[0] or 95.0
        
        return {
            'avg_confidence': avg_confidence,
            'conflict_rate': conflict_rate,
            'json_valid_rate': json_valid_rate
        }
    
    def update_daily_summary(self, date: str, summary: Dict):
        """Update or insert daily summary."""
        self.conn.execute("""
            INSERT OR REPLACE INTO daily_summary 
            (date, total_extractions, avg_extraction_confidence, total_integrations, 
             conflict_rate, experiments_run, experiments_kept, wiki_page_count, 
             avg_wiki_confidence, lint_pass_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date,
            summary.get('total_extractions', 0),
            summary.get('avg_extraction_confidence', 0.0),
            summary.get('total_integrations', 0),
            summary.get('conflict_rate', 0.0),
            summary.get('experiments_run', 0),
            summary.get('experiments_kept', 0),
            summary.get('wiki_page_count', 0),
            summary.get('avg_wiki_confidence', 0.0),
            summary.get('lint_pass_rate', 0.0)
        ))
        self.conn.commit()
    
    def get_experiment_count(self) -> int:
        """Get total number of prompt experiments run."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM prompt_experiments")
        return cursor.fetchone()[0]
    
    def get_hypothesis_count(self) -> int:
        """Get total number of research hypotheses tested."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM research_hypotheses")
        return cursor.fetchone()[0]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Convenience functions for quick access
def record_extraction_success(source_id: str, data: Dict):
    """Quick function to record successful extraction."""
    collector = MetricsCollector()
    
    # Calculate metrics from extracted data
    claims = data.get('claims', [])
    avg_conf = sum(c.get('confidence', 0) for c in claims) / len(claims) if claims else 0.0
    
    metrics = {
        'avg_confidence': avg_conf,
        'entity_count': len(data.get('entities', [])),
        'claim_count': len(claims),
        'relationship_count': len(data.get('relationships', [])),
        'json_valid': True,
        'prompt_version': 'V1'
    }
    
    collector.record_extraction(source_id, metrics)
    collector.close()


def record_extraction_failure(source_id: str, error: str):
    """Quick function to record extraction failure."""
    collector = MetricsCollector()
    
    metrics = {
        'avg_confidence': 0.0,
        'entity_count': 0,
        'claim_count': 0,
        'json_valid': False,
        'error_message': str(error),
        'prompt_version': 'V1'
    }
    
    collector.record_extraction(source_id, metrics)
    collector.close()


if __name__ == '__main__':
    # Test the metrics collector
    print("Initializing metrics database...")
    collector = MetricsCollector()
    
    print(f"Database created at: {METRICS_DB_PATH}")
    print(f"Total experiments: {collector.get_experiment_count()}")
    print(f"Total hypotheses: {collector.get_hypothesis_count()}")
    
    baseline = collector.get_baseline_metrics()
    print(f"\nBaseline metrics:")
    print(f"  Avg confidence: {baseline['avg_confidence']:.3f}")
    print(f"  Conflict rate: {baseline['conflict_rate']:.1f}%")
    print(f"  JSON valid rate: {baseline['json_valid_rate']:.1f}%")
    
    collector.close()
    print("\n✓ Metrics database initialized successfully")
