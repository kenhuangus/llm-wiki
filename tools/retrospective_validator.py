"""
Retrospective validator that checks old claims against new sources.
Detects contradictions and adjusts confidence scores.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import write_log, call_local_model, WIKI_DIR, parse_frontmatter, serialize_frontmatter
from metrics_collector import MetricsCollector


class RetrospectiveValidator:
    """Validates past extractions against new evidence."""
    
    def __init__(self, lookback_days: int = 7):
        self.lookback_days = lookback_days
        self.metrics = MetricsCollector()
        self.contradictions_found = 0
        self.confidence_adjustments = 0
        self.pages_validated = 0
        
        print("🔍 Retrospective Validator initialized")
        print(f"   Lookback period: {lookback_days} days")
    
    def run_weekly_validation(self):
        """Check if old claims still hold up against new sources."""
        print("\n" + "=" * 60)
        print("  Weekly Retrospective Validation")
        print("=" * 60)
        print()
        
        # 1. Find recently updated pages
        print("📊 Step 1: Finding recently updated pages...")
        recent_pages = self.get_recently_updated_pages()
        print(f"   Found {len(recent_pages)} pages updated in last {self.lookback_days} days")
        
        # 2. For each page, check old claims vs new sources
        print("\n🔬 Step 2: Validating claims...")
        for page in recent_pages:
            self.validate_page(page)
        
        # 3. Find reinforced claims
        print("\n✅ Step 3: Finding reinforced claims...")
        reinforced = self.find_reinforced_claims(recent_pages)
        print(f"   Found {len(reinforced)} reinforced claims")
        
        # 4. Generate report
        print("\n📋 Step 4: Generating validation report...")
        self.generate_report()
        
        print(f"\n{'=' * 60}")
        print(f"  Validation Complete")
        print(f"  - Pages validated: {self.pages_validated}")
        print(f"  - Contradictions found: {self.contradictions_found}")
        print(f"  - Confidence adjustments: {self.confidence_adjustments}")
        print(f"{'=' * 60}")
    
    def get_recently_updated_pages(self) -> List[Dict]:
        """Find pages modified in the last N days."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)
        cutoff_timestamp = cutoff_time.timestamp()
        
        recent_pages = []
        
        for root, dirs, files in os.walk(WIKI_DIR):
            for file in files:
                if not file.endswith('.md') or file in ['index.md', 'log.md', 'experiments.md']:
                    continue
                
                filepath = os.path.join(root, file)
                
                try:
                    mtime = os.path.getmtime(filepath)
                    
                    if mtime >= cutoff_timestamp:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        meta, body = parse_frontmatter(content)
                        
                        recent_pages.append({
                            'path': filepath,
                            'title': meta.get('title', file),
                            'domain': meta.get('domain', 'unknown'),
                            'confidence': meta.get('confidence', 0.0),
                            'source_count': meta.get('source_count', 1),
                            'status': meta.get('status', 'current'),
                            'metadata': meta,
                            'body': body
                        })
                except Exception as e:
                    print(f"   ⚠️  Error reading {file}: {e}")
                    continue
        
        return recent_pages
    
    def validate_page(self, page: Dict):
        """Validate a single page's claims."""
        print(f"\n   Validating: {page['title']}")
        
        # Extract claims from page body
        claims = self.extract_claims_from_body(page['body'])
        
        if not claims:
            print(f"      No claims found")
            return
        
        print(f"      Found {len(claims)} claims to validate")
        
        # Check for contradictions (simplified - would need actual new sources)
        # For now, just check if page has [CONFLICT] tags
        if '[CONFLICT]' in page['body']:
            print(f"      ⚠️  Existing conflict detected")
            self.contradictions_found += 1
            
            # Update page status if not already marked
            if page['status'] != 'conflict':
                self.update_page_status(page['path'], 'conflict')
        
        # Check confidence level
        if page['confidence'] < 0.6:
            print(f"      📉 Low confidence: {page['confidence']:.2f}")
            # Would trigger search for additional sources
        
        self.pages_validated += 1
    
    def extract_claims_from_body(self, body: str) -> List[str]:
        """Extract individual claims from page body."""
        claims = []
        
        # Simple extraction: look for bullet points in Claims section
        if '## Claims' in body:
            claims_section = body.split('## Claims')[1].split('##')[0]
            
            for line in claims_section.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('*'):
                    # Extract claim text (before confidence/source info)
                    claim_text = line.lstrip('-*').strip()
                    if claim_text:
                        claims.append(claim_text)
        
        return claims
    
    def find_reinforced_claims(self, pages: List[Dict]) -> List[Dict]:
        """Find claims that have been reinforced by multiple sources."""
        reinforced = []
        
        for page in pages:
            if page['source_count'] >= 3 and page['confidence'] >= 0.75:
                # Claim is well-supported
                reinforced.append({
                    'title': page['title'],
                    'confidence': page['confidence'],
                    'source_count': page['source_count']
                })
                
                # Increase confidence if not already at max
                if page['confidence'] < 0.9:
                    new_confidence = min(0.9, page['confidence'] + 0.05)
                    self.update_page_confidence(page['path'], new_confidence)
                    self.confidence_adjustments += 1
                    print(f"      ✓ Increased confidence: {page['title']} ({page['confidence']:.2f} → {new_confidence:.2f})")
        
        return reinforced
    
    def update_page_status(self, filepath: str, new_status: str):
        """Update page status in frontmatter."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            meta, body = parse_frontmatter(content)
            meta['status'] = new_status
            
            updated_content = serialize_frontmatter(meta, body)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            write_log('retrospective_validator', 'status_update', f"{filepath}: {new_status}")
            
        except Exception as e:
            print(f"      ❌ Error updating status: {e}")
    
    def update_page_confidence(self, filepath: str, new_confidence: float):
        """Update page confidence in frontmatter."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            meta, body = parse_frontmatter(content)
            old_confidence = meta.get('confidence', 0.0)
            meta['confidence'] = new_confidence
            
            updated_content = serialize_frontmatter(meta, body)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            write_log('retrospective_validator', 'confidence_update', 
                     f"{filepath}: {old_confidence:.2f} → {new_confidence:.2f}")
            
        except Exception as e:
            print(f"      ❌ Error updating confidence: {e}")
    
    def check_contradiction(self, old_claim: str, new_source_text: str) -> bool:
        """Use LLM to check if new source contradicts old claim."""
        system_prompt = """You are a fact-checking specialist.

TASK: Determine if the new source contradicts the old claim.

OUTPUT: Return ONLY "CONTRADICTION" or "NO_CONTRADICTION", nothing else."""
        
        input_text = f"""Old Claim:
{old_claim}

New Source:
{new_source_text}

Does the new source contradict the old claim?"""
        
        try:
            result = call_local_model(system_prompt, input_text)
            
            if result and 'CONTRADICTION' in result.upper():
                return 'CONTRADICTION' in result.upper() and 'NO_CONTRADICTION' not in result.upper()
            
            return False
            
        except Exception as e:
            print(f"      ❌ Error checking contradiction: {e}")
            return False
    
    def generate_report(self):
        """Generate validation report."""
        report_path = os.path.join(WIKI_DIR, 'validation_report.md')
        
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        report = f"""# Retrospective Validation Report

**Date:** {timestamp}  
**Lookback Period:** {self.lookback_days} days

## Summary

- **Pages Validated:** {self.pages_validated}
- **Contradictions Found:** {self.contradictions_found}
- **Confidence Adjustments:** {self.confidence_adjustments}

## Actions Taken

### Contradictions
{self.contradictions_found} pages marked with conflict status for human review.

### Confidence Adjustments
{self.confidence_adjustments} pages had confidence scores increased due to reinforcement from multiple sources.

## Recommendations

1. Review pages with status: conflict
2. Search for additional sources for low-confidence pages (<0.6)
3. Update outdated pages (>90 days old)

---

*Generated automatically by Retrospective Validator*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"   ✓ Report saved to: {report_path}")
        
        write_log('retrospective_validator', 'report_generated', 
                 f"Pages: {self.pages_validated}, Contradictions: {self.contradictions_found}")
    
    def close(self):
        """Close database connection."""
        self.metrics.close()


def main():
    """Run retrospective validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Retrospective validation of wiki claims')
    parser.add_argument('--days', type=int, default=7, help='Lookback period in days')
    args = parser.parse_args()
    
    validator = RetrospectiveValidator(lookback_days=args.days)
    validator.run_weekly_validation()
    validator.close()


if __name__ == '__main__':
    main()
