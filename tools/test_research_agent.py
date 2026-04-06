"""
Test research agent without LLM calls.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from research_agent import ResearchAgent

def test_research_agent():
    """Test research agent initialization and hypothesis generation."""
    print("=" * 60)
    print("  Testing Research Agent")
    print("=" * 60)
    print()
    
    # Test initialization
    print("1. Testing initialization...")
    agent = ResearchAgent()
    print(f"   ✓ Initialized with {len(agent.research_agenda.get('priorities', []))} priorities")
    
    # Test hypothesis generation
    print("\n2. Testing hypothesis generation...")
    hypotheses = agent.generate_daily_hypotheses()
    print(f"   ✓ Generated {len(hypotheses)} hypotheses")
    
    # Show hypotheses
    print("\n3. Hypothesis details:")
    for i, h in enumerate(hypotheses[:5], 1):
        print(f"   {i}. [{h['priority'].upper()}] {h['type']}")
        print(f"      {h['description']}")
        print(f"      Action: {h['action']}")
        print(f"      Metric: {h['success_metric']}")
        print()
    
    # Test coverage gap detection
    print("4. Testing coverage gap detection...")
    gaps = agent.identify_coverage_gaps()
    print(f"   ✓ Found {len(gaps)} coverage gaps")
    for gap in gaps:
        print(f"      - {gap['domain']}: {gap['count']}/{gap['target']} pages")
    
    # Test low confidence detection
    print("\n5. Testing low confidence page detection...")
    low_conf = agent.identify_low_confidence_pages()
    print(f"   ✓ Found {len(low_conf)} low-confidence pages")
    
    agent.close()
    
    print(f"\n{'='*60}")
    print("  ✅ All tests passed!")
    print(f"{'='*60}")

if __name__ == '__main__':
    test_research_agent()
