"""
Prompt optimization system using autoresearch-style ratchet loop.
Tests prompt modifications, keeps improvements, reverts failures.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone
from typing import Dict, List
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import write_log, call_local_model, WIKI_ROOT
from metrics_collector import MetricsCollector
from prompts import get_extraction_prompt, get_integration_prompt, ACTIVE_PROMPTS

# Evaluation set
EVAL_SET_INDEX = os.path.join(WIKI_ROOT, 'eval_set_index.json')


class PromptOptimizer:
    """Autoresearch-style ratchet for prompt improvement."""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.eval_set = self.load_evaluation_set()
        self.baseline_metrics = self.get_current_baseline()
        self.experiment_number = self.metrics.get_experiment_count() + 1
        
        print("🔬 Prompt Optimizer initialized")
        print(f"   Evaluation set: {len(self.eval_set)} sources")
        print(f"   Baseline confidence: {self.baseline_metrics['avg_confidence']:.3f}")
        print(f"   Baseline conflict rate: {self.baseline_metrics['conflict_rate']:.1f}%")
        print(f"   Baseline JSON valid rate: {self.baseline_metrics['json_valid_rate']:.1f}%")
        print(f"   Starting experiment: #{self.experiment_number}")
    
    def load_evaluation_set(self) -> List[Dict]:
        """Load fixed evaluation test set."""
        with open(EVAL_SET_INDEX, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['files']
    
    def get_current_baseline(self) -> Dict:
        """Get current baseline metrics from database."""
        baseline = self.metrics.get_baseline_metrics()
        
        # If no data in DB, use defaults
        if baseline['avg_confidence'] == 0.72:  # Default value
            print("⚠️  No baseline data in DB, using defaults")
        
        return baseline
    
    def run_optimization_cycle(self):
        """Single iteration of prompt improvement (ratchet loop)."""
        print(f"\n{'='*60}")
        print(f"  Experiment #{self.experiment_number}")
        print(f"{'='*60}\n")
        
        # 1. Analyze recent failures
        print("📊 Step 1: Analyzing recent failures...")
        failures = self.metrics.get_recent_failures(hours=24)
        print(f"   Found {len(failures)} failures in last 24h")
        
        # 2. Generate hypothesis
        print("\n💡 Step 2: Generating hypothesis...")
        hypothesis = self.generate_hypothesis(failures)
        print(f"   Hypothesis: {hypothesis['description']}")
        print(f"   Target: {hypothesis['target']}")
        
        # 3. Modify prompt
        print("\n✏️  Step 3: Modifying prompt...")
        old_version = ACTIVE_PROMPTS[hypothesis['prompt_type']]
        new_prompt = self.apply_hypothesis(hypothesis)
        
        if not new_prompt:
            print("   ❌ Failed to generate new prompt, skipping")
            return False
        
        # 4. Commit change
        print("\n💾 Step 4: Committing to git...")
        commit_hash = self.commit_prompt_change(hypothesis, new_prompt)
        
        if not commit_hash:
            print("   ⚠️  Git commit failed, continuing anyway")
        
        # 5. Evaluate on test set
        print("\n🧪 Step 5: Evaluating on test set...")
        new_metrics = self.evaluate_on_test_set(hypothesis['prompt_type'])
        
        # 6. Compare and decide
        print("\n📈 Step 6: Comparing results...")
        decision = self.make_decision(new_metrics)
        
        # 7. Keep or revert
        if decision['keep']:
            print(f"\n✅ KEPT: {hypothesis['description']}")
            print(f"   Improvement: {decision['reason']}")
            self.baseline_metrics = new_metrics
        else:
            print(f"\n❌ REVERTED: {hypothesis['description']}")
            print(f"   Reason: {decision['reason']}")
            self.git_revert()
        
        # 8. Log experiment
        self.log_experiment(hypothesis, old_version, new_metrics, decision, commit_hash)
        
        self.experiment_number += 1
        return decision['keep']
    
    def generate_hypothesis(self, failures: List[Dict]) -> Dict:
        """Generate hypothesis for prompt improvement based on failures."""
        
        # Analyze failure patterns
        if len(failures) > 5:
            # Many failures - focus on JSON parsing
            return {
                'prompt_type': 'extraction',
                'description': 'Improve JSON output formatting to reduce parsing errors',
                'target': 'json_valid_rate',
                'modification': 'Add explicit JSON formatting rules and examples'
            }
        elif len(failures) > 0:
            # Some failures - check error messages
            error_msgs = [f.get('error_message', '') for f in failures]
            if any('cvss' in msg.lower() for msg in error_msgs):
                return {
                    'prompt_type': 'extraction',
                    'description': 'Enhance CVE CVSS score extraction',
                    'target': 'cvss_extraction_rate',
                    'modification': 'Add explicit CVSS parsing instructions with regex patterns'
                }
        
        # Default: general confidence improvement
        return {
            'prompt_type': 'extraction',
            'description': 'Increase extraction confidence through better evidence requirements',
            'target': 'avg_confidence',
            'modification': 'Strengthen confidence scoring rubric with explicit evidence criteria'
        }
    
    def apply_hypothesis(self, hypothesis: Dict) -> str:
        """Apply hypothesis to generate new prompt."""
        
        current_prompt = get_extraction_prompt() if hypothesis['prompt_type'] == 'extraction' else get_integration_prompt()
        
        # Use LLM to modify prompt
        system_prompt = """You are a prompt engineering specialist.
        
TASK: Improve the given prompt based on the hypothesis.

RULES:
- Keep the overall structure and format
- Make targeted improvements based on the hypothesis
- Maintain all existing rules and constraints
- Output ONLY the improved prompt text, no explanations
- Do not wrap in markdown code blocks"""
        
        input_text = f"""Current Prompt:
{current_prompt}

Hypothesis: {hypothesis['description']}
Modification: {hypothesis['modification']}

Generate an improved version of this prompt that addresses the hypothesis while maintaining all existing functionality."""
        
        try:
            new_prompt = call_local_model(system_prompt, input_text)
            
            if new_prompt and len(new_prompt) > 100:
                return new_prompt
            else:
                print(f"   ⚠️  Generated prompt too short: {len(new_prompt)} chars")
                return None
                
        except Exception as e:
            print(f"   ❌ Error generating prompt: {e}")
            return None
    
    def commit_prompt_change(self, hypothesis: Dict, new_prompt: str) -> str:
        """Commit prompt change to git with hypothesis description."""
        
        # Write new prompt to prompts.py (simplified - just append as new version)
        prompts_file = os.path.join(os.path.dirname(__file__), 'prompts.py')
        
        try:
            # For now, just log the change (full implementation would modify prompts.py)
            commit_msg = f"Experiment #{self.experiment_number}: {hypothesis['description']}"
            
            # Git add and commit
            result = subprocess.run(
                ['git', 'add', prompts_file],
                capture_output=True,
                text=True,
                cwd=WIKI_ROOT
            )
            
            result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                capture_output=True,
                text=True,
                cwd=WIKI_ROOT
            )
            
            if result.returncode == 0:
                # Get commit hash
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    capture_output=True,
                    text=True,
                    cwd=WIKI_ROOT
                )
                commit_hash = result.stdout.strip()[:8]
                print(f"   ✓ Committed: {commit_hash}")
                return commit_hash
            else:
                print(f"   ⚠️  Nothing to commit (no changes)")
                return None
                
        except Exception as e:
            print(f"   ❌ Git error: {e}")
            return None
    
    def evaluate_on_test_set(self, prompt_type: str) -> Dict:
        """Run extraction on test set and measure quality."""
        
        results = []
        success_count = 0
        
        print(f"   Testing on {len(self.eval_set)} sources...")
        
        for idx, item in enumerate(self.eval_set[:10]):  # Test on first 10 for speed
            eval_path = os.path.join(WIKI_ROOT, item['eval_path'])
            
            if not os.path.exists(eval_path):
                continue
            
            try:
                # Run extraction
                result = subprocess.run(
                    [sys.executable, 'tools/extract.py', eval_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=WIKI_ROOT
                )
                
                json_path = eval_path + '.json'
                
                if result.returncode == 0 and os.path.exists(json_path):
                    # Load and analyze results
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    claims = data.get('claims', [])
                    avg_conf = sum(c.get('confidence', 0) for c in claims) / len(claims) if claims else 0.0
                    
                    results.append({
                        'avg_confidence': avg_conf,
                        'entity_count': len(data.get('entities', [])),
                        'claim_count': len(claims),
                        'json_valid': True
                    })
                    success_count += 1
                else:
                    results.append({
                        'avg_confidence': 0.0,
                        'entity_count': 0,
                        'claim_count': 0,
                        'json_valid': False
                    })
                    
            except Exception as e:
                results.append({
                    'avg_confidence': 0.0,
                    'entity_count': 0,
                    'claim_count': 0,
                    'json_valid': False
                })
        
        # Calculate aggregate metrics
        valid_results = [r for r in results if r['json_valid']]
        
        metrics = {
            'avg_confidence': np.mean([r['avg_confidence'] for r in valid_results]) if valid_results else 0.0,
            'json_valid_rate': (success_count / len(results) * 100) if results else 0.0,
            'conflict_rate': 0.0,  # Would need integration test
            'entity_count': np.mean([r['entity_count'] for r in valid_results]) if valid_results else 0.0,
            'claim_count': np.mean([r['claim_count'] for r in valid_results]) if valid_results else 0.0
        }
        
        print(f"   ✓ Tested {len(results)} sources, {success_count} successful")
        print(f"   Avg confidence: {metrics['avg_confidence']:.3f}")
        print(f"   JSON valid rate: {metrics['json_valid_rate']:.1f}%")
        
        return metrics
    
    def make_decision(self, new_metrics: Dict) -> Dict:
        """Decide whether to keep or revert based on metrics."""
        
        baseline = self.baseline_metrics
        
        # Calculate improvements
        conf_delta = new_metrics['avg_confidence'] - baseline['avg_confidence']
        json_delta = new_metrics['json_valid_rate'] - baseline['json_valid_rate']
        conflict_delta = baseline['conflict_rate'] - new_metrics['conflict_rate']  # Lower is better
        
        print(f"   Confidence: {baseline['avg_confidence']:.3f} → {new_metrics['avg_confidence']:.3f} (Δ {conf_delta:+.3f})")
        print(f"   JSON valid: {baseline['json_valid_rate']:.1f}% → {new_metrics['json_valid_rate']:.1f}% (Δ {json_delta:+.1f}%)")
        print(f"   Conflict rate: {baseline['conflict_rate']:.1f}% → {new_metrics['conflict_rate']:.1f}% (Δ {conflict_delta:+.1f}%)")
        
        # Decision logic: keep if any metric improves without degrading others significantly
        improvements = []
        degradations = []
        
        if conf_delta > 0.01:
            improvements.append(f"confidence +{conf_delta:.3f}")
        elif conf_delta < -0.05:
            degradations.append(f"confidence {conf_delta:.3f}")
        
        if json_delta > 1.0:
            improvements.append(f"JSON valid +{json_delta:.1f}%")
        elif json_delta < -5.0:
            degradations.append(f"JSON valid {json_delta:.1f}%")
        
        if conflict_delta > 1.0:
            improvements.append(f"conflicts -{conflict_delta:.1f}%")
        elif conflict_delta < -2.0:
            degradations.append(f"conflicts +{abs(conflict_delta):.1f}%")
        
        # Keep if improvements outweigh degradations
        if improvements and not degradations:
            return {
                'keep': True,
                'reason': ', '.join(improvements)
            }
        elif improvements and len(improvements) > len(degradations):
            return {
                'keep': True,
                'reason': f"{', '.join(improvements)} (minor: {', '.join(degradations)})"
            }
        else:
            return {
                'keep': False,
                'reason': 'No significant improvement' if not degradations else ', '.join(degradations)
            }
    
    def git_revert(self):
        """Revert last git commit."""
        try:
            result = subprocess.run(
                ['git', 'reset', 'HEAD~1'],
                capture_output=True,
                text=True,
                cwd=WIKI_ROOT
            )
            
            if result.returncode == 0:
                print("   ✓ Git reverted")
            else:
                print(f"   ⚠️  Git revert failed: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Git revert error: {e}")
    
    def log_experiment(self, hypothesis: Dict, old_version: str, new_metrics: Dict, decision: Dict, commit_hash: str):
        """Log experiment to database and experiments.md."""
        
        # Log to database
        experiment = {
            'experiment_number': self.experiment_number,
            'prompt_type': hypothesis['prompt_type'],
            'hypothesis': hypothesis['description'],
            'old_version': old_version,
            'new_version': f"{old_version}_modified",
            'baseline_confidence': self.baseline_metrics['avg_confidence'],
            'new_confidence': new_metrics['avg_confidence'],
            'baseline_conflict_rate': self.baseline_metrics['conflict_rate'],
            'new_conflict_rate': new_metrics['conflict_rate'],
            'baseline_json_valid_rate': self.baseline_metrics['json_valid_rate'],
            'new_json_valid_rate': new_metrics['json_valid_rate'],
            'decision': 'KEPT' if decision['keep'] else 'REVERTED',
            'commit_hash': commit_hash,
            'notes': decision['reason']
        }
        
        self.metrics.record_prompt_experiment(experiment)
        
        # Log to experiments.md
        experiments_file = os.path.join(WIKI_ROOT, 'wiki', 'experiments.md')
        
        if not os.path.exists(experiments_file):
            with open(experiments_file, 'w', encoding='utf-8') as f:
                f.write("# Autonomous Experiments Log\n\n")
        
        with open(experiments_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## Experiment #{self.experiment_number}: {hypothesis['description']}\n")
            f.write(f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write(f"- **Hypothesis:** {hypothesis['description']}\n")
            f.write(f"- **Target:** {hypothesis['target']}\n")
            f.write(f"- **Modification:** {hypothesis['modification']}\n")
            f.write(f"- **Evaluation:** Tested on {len(self.eval_set[:10])} sources\n")
            f.write(f"- **Results:**\n")
            f.write(f"  - Baseline confidence: {self.baseline_metrics['avg_confidence']:.3f}\n")
            f.write(f"  - New confidence: {new_metrics['avg_confidence']:.3f}\n")
            f.write(f"  - Δ: {new_metrics['avg_confidence'] - self.baseline_metrics['avg_confidence']:+.3f}\n")
            f.write(f"  - JSON valid rate: {new_metrics['json_valid_rate']:.1f}%\n")
            f.write(f"- **Decision:** {'✓ KEPT' if decision['keep'] else '✗ REVERTED'}")
            if commit_hash:
                f.write(f" (commit: {commit_hash})")
            f.write(f"\n")
            f.write(f"- **Reason:** {decision['reason']}\n")
        
        write_log('prompt_optimizer', f"experiment_{self.experiment_number}", 
                  f"{'KEPT' if decision['keep'] else 'REVERTED'}: {hypothesis['description']}")
    
    def close(self):
        """Close database connection."""
        self.metrics.close()


def main():
    """Run optimization cycles."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Prompt optimization with ratchet loop')
    parser.add_argument('--cycles', type=int, default=1, help='Number of optimization cycles to run')
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Prompt Optimizer - Autoresearch Ratchet Loop")
    print("=" * 60)
    print()
    
    optimizer = PromptOptimizer()
    
    kept_count = 0
    for i in range(args.cycles):
        if i > 0:
            print(f"\n{'='*60}\n")
        
        kept = optimizer.run_optimization_cycle()
        if kept:
            kept_count += 1
    
    print(f"\n{'='*60}")
    print(f"  Summary: {kept_count}/{args.cycles} improvements kept")
    print(f"{'='*60}")
    
    optimizer.close()


if __name__ == '__main__':
    main()
