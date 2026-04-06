"""
Long-form Paper Agent - Generates 6,000-8,000 word papers by section.

This version generates each section separately to ensure comprehensive length.
"""

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import write_log, call_local_model, WIKI_ROOT
from paper_agent import PaperAgent


class LongFormPaperAgent(PaperAgent):
    """Extended paper agent that generates longer papers section by section."""
    
    def generate_paper(self, focus_area: str = None, combine_topics: bool = False) -> dict:
        """
        Generate a comprehensive research paper (6,000-8,000 words).
        Overrides parent to skip critique iterations that condense content.
        """
        print("\n" + "=" * 80)
        print("  Long-Form Research Paper Generation (6K-8K words)")
        print("=" * 80)
        
        # Step 1: Select topic(s)
        topics = self._select_topics(focus_area, combine_topics)
        print(f"\n📋 Selected topics: {', '.join(topics)}")
        
        # Step 2: Analyze wiki for insights
        print("\n🔍 Analyzing wiki for novel insights...")
        wiki_insights = self._analyze_wiki(topics)
        
        # Step 3: Search external sources
        print("\n🌐 Searching external sources for related work...")
        external_sources = self._search_external_sources(topics)
        
        # Step 4: Generate comprehensive draft (section by section)
        print("\n✍️  Generating comprehensive paper draft...")
        final_draft = self._generate_draft(topics, wiki_insights, external_sources)
        
        # Skip critique iterations to preserve length
        print("\n📊 Preserving full length (skipping critique iterations)...")
        
        # Step 5: Finalize and save
        print("\n💾 Finalizing paper...")
        paper_metadata = self._finalize_paper(final_draft, topics)
        
        print(f"\n✅ Paper generated: {paper_metadata['filename']}")
        print(f"   Title: {paper_metadata['title']}")
        print(f"   Topics: {', '.join(topics)}")
        print(f"   Word count: {paper_metadata['word_count']}")
        
        # Log to metrics
        self._log_paper_generation(paper_metadata)
        
        return paper_metadata
    
    def _generate_draft(self, topics: list, wiki_insights: dict, external_sources: list) -> str:
        """Generate paper draft section by section for maximum length."""
        topics_str = ', '.join([t.replace('_', ' ').title() for t in topics])
        
        print("\n📝 Generating paper section by section for comprehensive coverage...")
        
        sections = {}
        
        # Section 1: Title and Abstract
        print("   Generating: Title & Abstract...")
        sections['abstract'] = self._generate_abstract(topics_str, wiki_insights)
        
        # Section 2: Introduction
        print("   Generating: Introduction (1,200-1,500 words)...")
        sections['introduction'] = self._generate_introduction(topics_str, wiki_insights)
        
        # Section 3: Related Work
        print("   Generating: Related Work (1,200-1,500 words)...")
        sections['related_work'] = self._generate_related_work(topics_str, wiki_insights)
        
        # Section 4: Methodology
        print("   Generating: Methodology (1,800-2,200 words)...")
        sections['methodology'] = self._generate_methodology(topics_str, wiki_insights)
        
        # Section 5: Experimental Design
        print("   Generating: Experimental Design (1,000-1,200 words)...")
        sections['experiments'] = self._generate_experiments(topics_str)
        
        # Section 6: Results
        print("   Generating: Results (800-1,000 words)...")
        sections['results'] = self._generate_results(topics_str)
        
        # Section 7: Discussion
        print("   Generating: Discussion (600-800 words)...")
        sections['discussion'] = self._generate_discussion(topics_str)
        
        # Section 8: Conclusion
        print("   Generating: Conclusion (300-400 words)...")
        sections['conclusion'] = self._generate_conclusion(topics_str)
        
        # Combine all sections
        paper = f"""{sections['abstract']}

{sections['introduction']}

{sections['related_work']}

{sections['methodology']}

{sections['experiments']}

{sections['results']}

{sections['discussion']}

{sections['conclusion']}

## References
1. [Key reference 1]
2. [Key reference 2]
3. [Key reference 3]
"""
        
        word_count = len(paper.split())
        print(f"\n✅ Draft complete: {word_count} words")
        
        return paper
    
    def _generate_abstract(self, topics_str, wiki_insights):
        prompt = f"""Write a comprehensive abstract (250-300 words) for a research paper on {topics_str}.

Include:
- Problem statement (2-3 sentences)
- Motivation (2-3 sentences)
- Proposed approach (3-4 sentences)
- Key results (2-3 sentences)
- Impact (1-2 sentences)

Write in complete, detailed sentences. Target: 250-300 words.
"""
        result = call_local_model("You are writing an academic paper abstract.", prompt)
        return f"# [Title for {topics_str}]\n\n## Abstract\n{result}"
    
    def _generate_introduction(self, topics_str, wiki_insights):
        prompt = f"""Write a comprehensive Introduction section (1,200-1,500 words) for a research paper on {topics_str}.

Structure:
1. Background and Context (300-400 words)
   - Historical development
   - Current state of the art
   - Key challenges

2. Problem Statement (200-300 words)
   - Specific problem being addressed
   - Why existing solutions are insufficient
   - Scope and boundaries

3. Motivation (200-300 words)
   - Why this problem matters
   - Real-world applications
   - Potential impact

4. Our Contributions (300-400 words)
   - List 3-5 specific contributions
   - Explain each in detail
   - How they advance the field

5. Paper Organization (100-150 words)

Write in complete paragraphs with technical details. Target: 1,200-1,500 words total.
"""
        result = call_local_model("You are writing an academic paper introduction.", prompt)
        return f"## 1. Introduction\n{result}"
    
    def _generate_related_work(self, topics_str, wiki_insights):
        prompt = f"""Write a comprehensive Related Work section (1,200-1,500 words) for a research paper on {topics_str}.

Structure:
1. Traditional Approaches (300-400 words)
   - Classical methods
   - Historical context
   - Limitations

2. Recent Advances (400-500 words)
   - State-of-the-art methods
   - Key papers and contributions
   - Comparison of approaches

3. Gaps in Existing Work (300-400 words)
   - What's missing
   - Limitations of current solutions

4. How Our Work Differs (200-300 words)
   - Unique aspects
   - Advantages over existing methods

Write detailed paragraphs with specific examples. Target: 1,200-1,500 words total.
"""
        result = call_local_model("You are writing an academic literature review.", prompt)
        return f"## 2. Related Work\n{result}"
    
    def _generate_methodology(self, topics_str, wiki_insights):
        prompt = f"""Write a comprehensive Methodology section (1,800-2,200 words) for a research paper on {topics_str}.

Structure:
1. Problem Formalization (400-500 words)
   - Mathematical notation and definitions
   - Formal problem statement
   - Assumptions and constraints
   - Include equations and formulas

2. Proposed Framework (600-800 words)
   - System architecture
   - Key components and interactions
   - Design decisions and rationale
   - Detailed technical descriptions

3. Algorithms (500-600 words)
   - Detailed algorithmic descriptions
   - Pseudocode for key procedures
   - Complexity analysis
   - Step-by-step explanations

4. Theoretical Analysis (300-400 words)
   - Theoretical guarantees
   - Convergence properties
   - Optimality conditions

Write with extensive technical details, equations, and explanations. Target: 1,800-2,200 words total.
"""
        result = call_local_model("You are writing a technical methodology section.", prompt)
        return f"## 3. Methodology\n{result}"
    
    def _generate_experiments(self, topics_str):
        prompt = f"""Write a comprehensive Experimental Design section (1,000-1,200 words) for a research paper on {topics_str}.

Structure:
1. Datasets and Benchmarks (300-400 words)
   - Description of datasets
   - Data preprocessing
   - Train/validation/test splits
   - Dataset statistics

2. Baseline Methods (300-400 words)
   - Description of comparison methods
   - Implementation details
   - Hyperparameter settings

3. Evaluation Metrics (200-300 words)
   - Metrics and definitions
   - Why these metrics are appropriate

4. Implementation Details (200-300 words)
   - Hardware and software setup
   - Training procedures
   - Reproducibility information

Write detailed descriptions with specific numbers and configurations. Target: 1,000-1,200 words total.
"""
        result = call_local_model("You are writing an experimental design section.", prompt)
        return f"## 4. Experimental Design\n{result}"
    
    def _generate_results(self, topics_str):
        prompt = f"""Write a comprehensive Results section (800-1,000 words) for a research paper on {topics_str}.

Structure:
1. Main Results (400-500 words)
   - Performance comparison tables
   - Statistical significance tests
   - Analysis of results
   - Detailed interpretation

2. Ablation Studies (300-400 words)
   - Impact of different components
   - Sensitivity analysis
   - Component contributions

3. Qualitative Analysis (100-200 words)
   - Case studies
   - Example outputs
   - Visual analysis

Write with detailed analysis and interpretation. Target: 800-1,000 words total.
"""
        result = call_local_model("You are writing a results section.", prompt)
        return f"## 5. Results\n{result}"
    
    def _generate_discussion(self, topics_str):
        prompt = f"""Write a comprehensive Discussion section (600-800 words) for a research paper on {topics_str}.

Structure:
1. Interpretation of Results (250-350 words)
   - Why the method works
   - Insights gained
   - Implications

2. Limitations (200-250 words)
   - Current limitations
   - Failure cases
   - Constraints

3. Future Directions (150-200 words)
   - Potential improvements
   - Open questions
   - Research opportunities

Write thoughtful analysis with depth. Target: 600-800 words total.
"""
        result = call_local_model("You are writing a discussion section.", prompt)
        return f"## 6. Discussion\n{result}"
    
    def _generate_conclusion(self, topics_str):
        prompt = f"""Write a comprehensive Conclusion section (300-400 words) for a research paper on {topics_str}.

Structure:
1. Summary of Contributions (150-200 words)
   - Recap main contributions
   - Key innovations

2. Key Findings (100-150 words)
   - Main results
   - Important insights

3. Broader Impact (50-100 words)
   - Significance for the field
   - Potential applications

Write a strong, impactful conclusion. Target: 300-400 words total.
"""
        result = call_local_model("You are writing a conclusion section.", prompt)
        return f"## 7. Conclusion\n{result}"


def main():
    """Entry point for long-form paper agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Long-Form Paper Agent (6K-8K words)')
    parser.add_argument('--focus', type=str, 
                       choices=['agentic_ai_security', 'context_engineering', 'context_harness',
                               'openclaw_security', 'nemoclaw_security', 'recursive_self_improvement',
                               'memory_management', 'long_horizon_tasks'],
                       help='Specific focus area')
    
    args = parser.parse_args()
    
    agent = LongFormPaperAgent()
    
    try:
        agent.generate_paper(focus_area=args.focus, combine_topics=False)
    finally:
        agent.close()


if __name__ == '__main__':
    main()
