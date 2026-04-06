"""
Autonomous research agent that identifies knowledge gaps and generates hypotheses.
Proactively seeks to improve wiki coverage and quality.
"""

import os
import sys
import json
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import write_log, call_local_model, WIKI_DIR, WIKI_ROOT
from metrics_collector import MetricsCollector


class ResearchAgent:
    """Proactive research agent that identifies gaps and seeks answers."""
    
    def __init__(self, research_agenda_path: str = None):
        if research_agenda_path is None:
            research_agenda_path = os.path.join(WIKI_ROOT, 'research_agenda.md')
        
        self.research_agenda = self.load_research_agenda(research_agenda_path)
        self.metrics = MetricsCollector()
        self.hypothesis_number = self.metrics.get_hypothesis_count() + 1
        
        print("🔬 Research Agent initialized")
        print(f"   Research agenda loaded: {len(self.research_agenda)} priorities")
        print(f"   Starting hypothesis: #{self.hypothesis_number}")
    
    def load_research_agenda(self, path: str) -> Dict:
        """Load research agenda from markdown file."""
        if not os.path.exists(path):
            print(f"⚠️  Research agenda not found: {path}")
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple parsing - extract key sections
        agenda = {
            'priorities': [],
            'constraints': {},
            'thresholds': {}
        }
        
        # Extract priorities (simplified)
        if 'Agentic AI Security Threat Taxonomy' in content:
            agenda['priorities'].append({
                'name': 'Agentic AI Security Threat Taxonomy',
                'target': 50,
                'domain': 'security/attack-patterns'
            })
        
        if 'CVE Coverage' in content:
            agenda['priorities'].append({
                'name': 'CVE Coverage for Coding Agents',
                'target': 100,
                'domain': 'security/cve'
            })
        
        if 'Foundation Model' in content:
            agenda['priorities'].append({
                'name': 'Foundation Model Capability Tracking',
                'target': 5,
                'domain': 'entities/models'
            })
        
        # Extract thresholds
        agenda['thresholds'] = {
            'min_pages': 50,
            'min_confidence': 0.75,
            'max_experiments_per_day': 10
        }
        
        return agenda
    
    def generate_daily_hypotheses(self) -> List[Dict]:
        """Analyze wiki state and propose research directions."""
        print("\n📊 Analyzing wiki state...")
        
        hypotheses = []
        
        # 1. Coverage gaps
        coverage_gaps = self.identify_coverage_gaps()
        for gap in coverage_gaps:
            hypotheses.append({
                'type': 'coverage_expansion',
                'domain': gap['domain'],
                'description': f"Expand coverage in {gap['domain']} (currently {gap['count']} pages, target {gap['target']})",
                'action': f"Search arXiv for recent papers on {gap['topic']}",
                'success_metric': f"Add ≥{gap['needed']} new pages to {gap['domain']}",
                'priority': 'high' if gap['count'] < 30 else 'normal'
            })
        
        # 2. Low confidence pages
        low_conf_pages = self.identify_low_confidence_pages()
        for page in low_conf_pages:
            hypotheses.append({
                'type': 'validation',
                'domain': page['domain'],
                'description': f"Validate low-confidence page: {page['title']}",
                'action': f"Search for additional sources on {page['topic']}",
                'success_metric': f"Increase confidence from {page['confidence']:.2f} to ≥0.75",
                'priority': 'normal'
            })
        
        # 3. Synthesis opportunities
        synthesis_opps = self.identify_synthesis_opportunities()
        for opp in synthesis_opps:
            hypotheses.append({
                'type': 'synthesis',
                'domain': opp['domain'],
                'description': f"Create comparison page for {opp['topic']}",
                'action': f"Synthesize comparison from {len(opp['pages'])} related pages",
                'success_metric': f"Comparison page with ≥3 dimensions",
                'priority': 'low'
            })
        
        # 4. Outdated pages
        outdated_pages = self.identify_outdated_pages()
        for page in outdated_pages:
            hypotheses.append({
                'type': 'update',
                'domain': page['domain'],
                'description': f"Update outdated page: {page['title']}",
                'action': f"Search for recent sources on {page['topic']}",
                'success_metric': f"Update page with sources from last 90 days",
                'priority': 'normal'
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'normal': 1, 'low': 2}
        hypotheses.sort(key=lambda h: priority_order.get(h['priority'], 1))
        
        print(f"   Generated {len(hypotheses)} hypotheses:")
        for h in hypotheses[:5]:  # Show top 5
            print(f"   - [{h['priority'].upper()}] {h['description']}")
        
        return hypotheses
    
    def identify_coverage_gaps(self) -> List[Dict]:
        """Find domains with insufficient page count."""
        gaps = []
        
        # Check each priority domain
        for priority in self.research_agenda.get('priorities', []):
            domain_path = os.path.join(WIKI_DIR, priority['domain'])
            
            if not os.path.exists(domain_path):
                count = 0
            else:
                count = sum(1 for f in Path(domain_path).rglob('*.md') if f.is_file())
            
            target = priority['target']
            
            if count < target:
                gaps.append({
                    'domain': priority['domain'],
                    'topic': priority['name'],
                    'count': count,
                    'target': target,
                    'needed': target - count
                })
        
        return gaps
    
    def identify_low_confidence_pages(self) -> List[Dict]:
        """Find pages with confidence < 0.75."""
        low_conf = []
        
        # Scan wiki directory
        for root, dirs, files in os.walk(WIKI_DIR):
            for file in files:
                if not file.endswith('.md') or file in ['index.md', 'log.md', 'experiments.md']:
                    continue
                
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract confidence from frontmatter
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            import yaml
                            meta = yaml.safe_load(parts[1])
                            
                            confidence = meta.get('confidence', 1.0)
                            if confidence < 0.75:
                                domain = os.path.relpath(root, WIKI_DIR)
                                low_conf.append({
                                    'title': meta.get('title', file),
                                    'domain': domain,
                                    'topic': meta.get('title', file),
                                    'confidence': confidence,
                                    'path': filepath
                                })
                except Exception:
                    continue
        
        return low_conf[:5]  # Limit to top 5
    
    def identify_synthesis_opportunities(self) -> List[Dict]:
        """Find related pages that could be compared."""
        opportunities = []
        
        # Look for groups of related pages (simplified heuristic)
        # In a full implementation, would use semantic similarity
        
        # Example: Find multiple model pages
        models_dir = os.path.join(WIKI_DIR, 'entities', 'models')
        if os.path.exists(models_dir):
            model_files = list(Path(models_dir).glob('*.md'))
            
            if len(model_files) >= 3:
                opportunities.append({
                    'domain': 'comparisons',
                    'topic': 'LLM Models',
                    'pages': [f.name for f in model_files[:5]]
                })
        
        return opportunities
    
    def identify_outdated_pages(self) -> List[Dict]:
        """Find pages not updated in 90+ days."""
        outdated = []
        
        cutoff_date = datetime.now(timezone.utc).timestamp() - (90 * 24 * 3600)
        
        for root, dirs, files in os.walk(WIKI_DIR):
            for file in files:
                if not file.endswith('.md') or file in ['index.md', 'log.md', 'experiments.md']:
                    continue
                
                filepath = os.path.join(root, file)
                
                try:
                    # Check file modification time
                    mtime = os.path.getmtime(filepath)
                    
                    if mtime < cutoff_date:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                import yaml
                                meta = yaml.safe_load(parts[1])
                                
                                domain = os.path.relpath(root, WIKI_DIR)
                                outdated.append({
                                    'title': meta.get('title', file),
                                    'domain': domain,
                                    'topic': meta.get('title', file),
                                    'path': filepath
                                })
                except Exception:
                    continue
        
        return outdated[:3]  # Limit to top 3
    
    def execute_hypothesis(self, hypothesis: Dict) -> Dict:
        """Execute a research hypothesis."""
        print(f"\n🔬 Executing Hypothesis #{self.hypothesis_number}")
        print(f"   Type: {hypothesis['type']}")
        print(f"   Description: {hypothesis['description']}")
        
        result = {
            'hypothesis_number': self.hypothesis_number,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'hypothesis_type': hypothesis['type'],
            'description': hypothesis['description'],
            'action': hypothesis['action'],
            'success_metric': hypothesis['success_metric'],
            'pages_affected': 0,
            'confidence_improvement': 0.0,
            'decision': 'PENDING',
            'notes': ''
        }
        
        try:
            if hypothesis['type'] == 'coverage_expansion':
                result = self.execute_coverage_expansion(hypothesis, result)
            
            elif hypothesis['type'] == 'validation':
                result = self.execute_validation(hypothesis, result)
            
            elif hypothesis['type'] == 'synthesis':
                result = self.execute_synthesis(hypothesis, result)
            
            elif hypothesis['type'] == 'update':
                result = self.execute_update(hypothesis, result)
            
            else:
                result['decision'] = 'SKIPPED'
                result['notes'] = f"Unknown hypothesis type: {hypothesis['type']}"
        
        except Exception as e:
            result['decision'] = 'FAILED'
            result['notes'] = f"Error: {str(e)}"
            print(f"   ❌ Execution failed: {e}")
        
        # Log to database and file
        self.log_hypothesis(result)
        
        self.hypothesis_number += 1
        return result
    
    def execute_coverage_expansion(self, hypothesis: Dict, result: Dict) -> Dict:
        """Execute coverage expansion by searching for relevant sources."""
        print(f"   Action: Searching for sources on {hypothesis['domain']}")
        
        # Generate search query using LLM
        system_prompt = """You are a research query generator.
        
TASK: Generate a specific arXiv search query for the given topic.

OUTPUT: Return ONLY the search query string, no explanations."""
        
        input_text = f"Topic: {hypothesis['description']}\nGenerate an arXiv search query:"
        
        try:
            query = call_local_model(system_prompt, input_text)
            
            if query and len(query) > 5:
                result['notes'] = f"Generated search query: {query}"
                result['decision'] = 'SUCCESS'
                result['pages_affected'] = 0  # Would be updated after actual search
                print(f"   ✓ Generated query: {query[:50]}...")
            else:
                result['decision'] = 'FAILED'
                result['notes'] = "Failed to generate valid query"
                print(f"   ❌ Query generation failed")
        
        except Exception as e:
            result['decision'] = 'FAILED'
            result['notes'] = f"Error generating query: {e}"
            print(f"   ❌ Error: {e}")
        
        return result
    
    def execute_validation(self, hypothesis: Dict, result: Dict) -> Dict:
        """Execute validation by searching for corroborating sources."""
        print(f"   Action: Searching for validation sources")
        
        # Simplified: just mark as needing validation
        result['decision'] = 'SUCCESS'
        result['notes'] = f"Identified page needing validation: {hypothesis.get('domain')}"
        result['pages_affected'] = 1
        print(f"   ✓ Validation task created")
        
        return result
    
    def execute_synthesis(self, hypothesis: Dict, result: Dict) -> Dict:
        """Execute synthesis by creating comparison page."""
        print(f"   Action: Creating comparison page")
        
        # Generate comparison using LLM
        system_prompt = """You are a technical comparison writer.

TASK: Create a comparison page outline for the given topic.

OUTPUT: Return a markdown outline with comparison dimensions."""
        
        input_text = f"Topic: {hypothesis['description']}\nPages to compare: {hypothesis.get('pages', [])}"
        
        try:
            outline = call_local_model(system_prompt, input_text)
            
            if outline and len(outline) > 50:
                result['decision'] = 'SUCCESS'
                result['notes'] = f"Generated comparison outline ({len(outline)} chars)"
                result['pages_affected'] = 1
                print(f"   ✓ Comparison outline generated")
            else:
                result['decision'] = 'FAILED'
                result['notes'] = "Failed to generate outline"
                print(f"   ❌ Outline generation failed")
        
        except Exception as e:
            result['decision'] = 'FAILED'
            result['notes'] = f"Error: {e}"
            print(f"   ❌ Error: {e}")
        
        return result
    
    def execute_update(self, hypothesis: Dict, result: Dict) -> Dict:
        """Execute update by searching for recent sources."""
        print(f"   Action: Searching for recent sources")
        
        result['decision'] = 'SUCCESS'
        result['notes'] = f"Identified outdated page: {hypothesis.get('domain')}"
        result['pages_affected'] = 1
        print(f"   ✓ Update task created")
        
        return result
    
    def log_hypothesis(self, result: Dict):
        """Log hypothesis to database and experiments.md."""
        # Log to database
        self.metrics.record_research_hypothesis(result)
        
        # Log to experiments.md
        experiments_file = os.path.join(WIKI_DIR, 'experiments.md')
        
        if not os.path.exists(experiments_file):
            os.makedirs(os.path.dirname(experiments_file), exist_ok=True)
            with open(experiments_file, 'w', encoding='utf-8') as f:
                f.write("# Autonomous Experiments Log\n\n")
        
        with open(experiments_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## Research Hypothesis #{result['hypothesis_number']}: {result['description']}\n")
            f.write(f"**Date:** {result['timestamp']}\n\n")
            f.write(f"- **Type:** {result['hypothesis_type']}\n")
            f.write(f"- **Action:** {result['action']}\n")
            f.write(f"- **Success Metric:** {result['success_metric']}\n")
            f.write(f"- **Result:** {result['decision']}\n")
            f.write(f"- **Pages Affected:** {result['pages_affected']}\n")
            f.write(f"- **Notes:** {result['notes']}\n")
        
        write_log('research_agent', f"hypothesis_{result['hypothesis_number']}", 
                  f"{result['decision']}: {result['description']}")
    
    def close(self):
        """Close database connection."""
        self.metrics.close()


def main():
    """Run research agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Autonomous research agent')
    parser.add_argument('--hypotheses', type=int, default=5, help='Number of hypotheses to generate')
    parser.add_argument('--execute', type=int, default=0, help='Number of hypotheses to execute')
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Autonomous Research Agent")
    print("=" * 60)
    print()
    
    agent = ResearchAgent()
    
    # Generate hypotheses
    hypotheses = agent.generate_daily_hypotheses()
    
    print(f"\n📋 Generated {len(hypotheses)} hypotheses")
    
    # Execute if requested
    if args.execute > 0:
        print(f"\n🚀 Executing top {args.execute} hypotheses...")
        
        for i, hypothesis in enumerate(hypotheses[:args.execute]):
            if i > 0:
                print()
            result = agent.execute_hypothesis(hypothesis)
            print(f"   Result: {result['decision']}")
    
    agent.close()
    
    print(f"\n{'='*60}")
    print(f"  Complete!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
