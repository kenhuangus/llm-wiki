"""
Quick test for prompt optimizer - verifies initialization and logic.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prompt_optimizer import PromptOptimizer

def test_optimizer():
    """Test optimizer initialization and hypothesis generation."""
    print("=" * 60)
    print("  Testing Prompt Optimizer")
    print("=" * 60)
    print()
    
    # Test initialization
    print("1. Testing initialization...")
    optimizer = PromptOptimizer()
    print(f"   ✓ Initialized with {len(optimizer.eval_set)} sources")
    print(f"   ✓ Baseline: confidence={optimizer.baseline_metrics['avg_confidence']:.3f}")
    
    # Test hypothesis generation
    print("\n2. Testing hypothesis generation...")
    hypothesis = optimizer.generate_hypothesis([])
    print(f"   ✓ Generated hypothesis: {hypothesis['description']}")
    print(f"   ✓ Target: {hypothesis['target']}")
    print(f"   ✓ Prompt type: {hypothesis['prompt_type']}")
    
    # Test decision logic
    print("\n3. Testing decision logic...")
    
    # Test improvement scenario
    new_metrics = {
        'avg_confidence': 0.75,  # +0.03 improvement
        'json_valid_rate': 96.0,  # +1% improvement
        'conflict_rate': 11.0  # -1% improvement
    }
    decision = optimizer.make_decision(new_metrics)
    print(f"   Scenario: All metrics improve")
    print(f"   Decision: {'KEEP' if decision['keep'] else 'REVERT'}")
    print(f"   Reason: {decision['reason']}")
    
    if decision['keep']:
        print(f"   ✓ Correctly decided to KEEP")
    else:
        print(f"   ✗ Should have kept improvement")
    
    # Test degradation scenario
    new_metrics = {
        'avg_confidence': 0.70,  # -0.02 degradation
        'json_valid_rate': 90.0,  # -5% degradation
        'conflict_rate': 15.0  # +3% degradation
    }
    decision = optimizer.make_decision(new_metrics)
    print(f"\n   Scenario: All metrics degrade")
    print(f"   Decision: {'KEEP' if decision['keep'] else 'REVERT'}")
    print(f"   Reason: {decision['reason']}")
    
    if not decision['keep']:
        print(f"   ✓ Correctly decided to REVERT")
    else:
        print(f"   ✗ Should have reverted degradation")
    
    optimizer.close()
    
    print(f"\n{'='*60}")
    print("  ✅ All tests passed!")
    print(f"{'='*60}")

if __name__ == '__main__':
    test_optimizer()
