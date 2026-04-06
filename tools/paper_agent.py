"""
Research Paper Agent - Generates ICLR/ICML/NeurIPS-level papers.

Focus areas:
- Agentic AI Security
- Context Engineering
- Context Harness
- OpenClaw Security
- NemoClaw Security
- Recursive Self-Improvement
- Memory Management
- Long Horizon Tasks

Process:
1. Analyze wiki for novel insights
2. Search external sources for related work
3. Generate paper draft
4. Self-critique and improve (2 iterations)
5. Finalize and save
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import write_log, call_local_model, WIKI_ROOT, WIKI_DIR
from metrics_collector import MetricsCollector


# Research focus areas
FOCUS_AREAS = [
    "agentic_ai_security",
    "context_engineering",
    "context_harness",
    "openclaw_security",
    "nemoclaw_security",
    "recursive_self_improvement",
    "memory_management",
    "long_horizon_tasks"
]


class PaperAgent:
    """Autonomous research paper generation agent."""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.papers_dir = os.path.join(WIKI_ROOT, 'papers')
        os.makedirs(self.papers_dir, exist_ok=True)
        
        print("📝 Research Paper Agent initialized")
        print(f"   Papers directory: {self.papers_dir}")
        print(f"   Focus areas: {len(FOCUS_AREAS)}")
        
        write_log('paper_agent', 'initialized', f'{len(FOCUS_AREAS)} focus areas')
    
    def close(self):
        """Cleanup resources."""
        self.metrics.close()
    
    def generate_paper(self, focus_area: str = None, combine_topics: bool = False) -> dict:
        """
        Generate a research paper.
        
        Args:
            focus_area: Specific focus area or None for auto-select
            combine_topics: Whether to combine multiple topics
            
        Returns:
            dict with paper metadata and path
        """
        print("\n" + "=" * 80)
        print("  Research Paper Generation")
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
        
        # Step 4: Generate paper draft
        print("\n✍️  Generating paper draft...")
        draft_v1 = self._generate_draft(topics, wiki_insights, external_sources)
        
        # Step 5: Self-critique iteration 1
        print("\n🔬 Self-critique iteration 1...")
        draft_v2 = self._critique_and_improve(draft_v1, iteration=1)
        
        # Step 6: Self-critique iteration 2
        print("\n🔬 Self-critique iteration 2...")
        final_draft = self._critique_and_improve(draft_v2, iteration=2)
        
        # Step 7: Finalize and save
        print("\n💾 Finalizing paper...")
        paper_metadata = self._finalize_paper(final_draft, topics)
        
        print(f"\n✅ Paper generated: {paper_metadata['filename']}")
        print(f"   Title: {paper_metadata['title']}")
        print(f"   Topics: {', '.join(topics)}")
        print(f"   Word count: {paper_metadata['word_count']}")
        
        # Log to metrics
        self._log_paper_generation(paper_metadata)
        
        return paper_metadata
    
    def _select_topics(self, focus_area: str, combine_topics: bool) -> list:
        """Select research topics based on wiki analysis."""
        if focus_area and focus_area in FOCUS_AREAS:
            topics = [focus_area]
        elif combine_topics:
            # Use LLM to select complementary topics
            prompt = f"""Analyze these research areas and select 2-3 complementary topics that would make a novel research paper:

{chr(10).join(f'- {area}' for area in FOCUS_AREAS)}

Return ONLY a JSON array of topic names, e.g.: ["topic1", "topic2"]
"""
            result = call_local_model("You are a research advisor.", prompt)
            try:
                if result.startswith("```json"):
                    result = result.strip("```json").strip("```").strip()
                elif result.startswith("```"):
                    result = result.strip("```").strip()
                topics = json.loads(result)
                # Validate topics
                topics = [t for t in topics if t in FOCUS_AREAS][:3]
            except:
                # Fallback: pick first 2
                topics = FOCUS_AREAS[:2]
        else:
            # Auto-select based on wiki coverage gaps
            topics = self._find_underexplored_topics()
        
        return topics if topics else [FOCUS_AREAS[0]]
    
    def _find_underexplored_topics(self) -> list:
        """Find topics with low wiki coverage."""
        # Count pages per topic
        topic_counts = {}
        
        for topic in FOCUS_AREAS:
            count = 0
            # Search wiki for topic mentions
            for root, dirs, files in os.walk(WIKI_DIR):
                for file in files:
                    if file.endswith('.md'):
                        try:
                            filepath = os.path.join(root, file)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read().lower()
                                if topic.replace('_', ' ') in content:
                                    count += 1
                        except:
                            pass
            topic_counts[topic] = count
        
        # Return topic with lowest coverage
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1])
        return [sorted_topics[0][0]]
    
    def _analyze_wiki(self, topics: list) -> dict:
        """Analyze wiki for insights on topics."""
        insights = {
            'key_findings': [],
            'gaps': [],
            'contradictions': [],
            'novel_connections': []
        }
        
        # Collect relevant wiki pages
        relevant_pages = []
        for root, dirs, files in os.walk(WIKI_DIR):
            for file in files:
                if file.endswith('.md') and file != 'index.md':
                    try:
                        filepath = os.path.join(root, file)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Check if any topic is mentioned
                            if any(topic.replace('_', ' ') in content.lower() for topic in topics):
                                relevant_pages.append({
                                    'path': filepath,
                                    'content': content[:5000]  # First 5000 chars
                                })
                    except:
                        pass
        
        print(f"   Found {len(relevant_pages)} relevant wiki pages")
        
        if not relevant_pages:
            return insights
        
        # Use LLM to analyze pages for insights
        pages_summary = "\n\n".join([
            f"Page {i+1}:\n{page['content'][:2000]}"
            for i, page in enumerate(relevant_pages[:5])  # Max 5 pages
        ])
        
        prompt = f"""Analyze these wiki pages about {', '.join(topics)} and identify:

1. Key findings (novel insights, important results)
2. Research gaps (what's missing, unexplored areas)
3. Contradictions (conflicting claims)
4. Novel connections (unexpected relationships between concepts)

Wiki pages:
{pages_summary}

Return JSON:
{{
  "key_findings": ["finding1", "finding2", ...],
  "gaps": ["gap1", "gap2", ...],
  "contradictions": ["contradiction1", ...],
  "novel_connections": ["connection1", ...]
}}
"""
        
        result = call_local_model("You are a research analyst.", prompt)
        
        try:
            if result.startswith("```json"):
                result = result.strip("```json").strip("```").strip()
            elif result.startswith("```"):
                result = result.strip("```").strip()
            insights = json.loads(result)
        except Exception as e:
            print(f"   ⚠️  Failed to parse insights: {e}")
        
        return insights
    
    def _search_external_sources(self, topics: list) -> list:
        """Search for external sources (arXiv, papers)."""
        # For now, return placeholder
        # In production, this would query arXiv API, Semantic Scholar, etc.
        return [
            {
                'title': f'Related work on {topics[0]}',
                'authors': 'Various',
                'year': 2025,
                'venue': 'arXiv',
                'summary': 'Placeholder for external source'
            }
        ]
    
    def _generate_draft(self, topics: list, wiki_insights: dict, external_sources: list) -> str:
        """Generate initial paper draft."""
        topics_str = ', '.join([t.replace('_', ' ').title() for t in topics])
        
        prompt = f"""Generate a COMPREHENSIVE research paper draft for a top-tier ML conference (ICLR/ICML/NeurIPS).

CRITICAL REQUIREMENTS:
- TARGET LENGTH: 6,000-8,000 words (approximately 8,000-10,000 tokens)
- Write COMPLETE, DETAILED paragraphs with extensive technical content
- Include mathematical formulations, algorithms, and detailed explanations
- Each section should be FULLY DEVELOPED, not just outlines

TOPICS: {topics_str}

WIKI INSIGHTS:
Key Findings: {json.dumps(wiki_insights.get('key_findings', []), indent=2)}
Research Gaps: {json.dumps(wiki_insights.get('gaps', []), indent=2)}
Novel Connections: {json.dumps(wiki_insights.get('novel_connections', []), indent=2)}

STRUCTURE AND LENGTH REQUIREMENTS:

# [Compelling Title]

## Abstract (250-300 words)
Write a COMPLETE abstract with:
- Problem statement (2-3 sentences)
- Motivation and significance (2-3 sentences)
- Proposed approach (3-4 sentences)
- Key results and contributions (2-3 sentences)
- Broader impact (1-2 sentences)

## 1. Introduction (1,200-1,500 words)
Write DETAILED introduction with:
- Background and context (300-400 words)
  * Historical development of the field
  * Current state of the art
  * Key challenges and limitations
- Problem statement (200-300 words)
  * Specific problem being addressed
  * Why existing solutions are insufficient
  * Scope and boundaries
- Motivation (200-300 words)
  * Why this problem matters
  * Real-world applications
  * Potential impact
- Our contributions (300-400 words)
  * List 3-5 specific contributions
  * Explain each contribution in detail
  * How they advance the field
- Paper organization (100-150 words)

## 2. Related Work (1,200-1,500 words)
Write COMPREHENSIVE literature review with:
- Traditional approaches (300-400 words)
  * Classical methods and their limitations
  * Historical context
- Recent advances (400-500 words)
  * State-of-the-art methods
  * Key papers and their contributions
  * Comparison of approaches
- Gaps in existing work (300-400 words)
  * What's missing in current research
  * Limitations of existing solutions
- How our work differs (200-300 words)
  * Unique aspects of our approach
  * Advantages over existing methods

## 3. Methodology (1,800-2,200 words)
Write DETAILED technical approach with:
- Problem formalization (400-500 words)
  * Mathematical notation and definitions
  * Formal problem statement
  * Assumptions and constraints
- Proposed framework (600-800 words)
  * System architecture
  * Key components and their interactions
  * Design decisions and rationale
- Algorithms (500-600 words)
  * Detailed algorithmic descriptions
  * Pseudocode for key procedures
  * Complexity analysis
- Theoretical analysis (300-400 words)
  * Theoretical guarantees
  * Convergence properties
  * Optimality conditions

## 4. Experimental Design (1,000-1,200 words)
Write COMPLETE experimental setup with:
- Datasets and benchmarks (300-400 words)
  * Description of datasets used
  * Data preprocessing steps
  * Train/validation/test splits
- Baseline methods (300-400 words)
  * Description of comparison methods
  * Implementation details
  * Hyperparameter settings
- Evaluation metrics (200-300 words)
  * Metrics used and their definitions
  * Why these metrics are appropriate
- Implementation details (200-300 words)
  * Hardware and software setup
  * Training procedures
  * Reproducibility information

## 5. Results (800-1,000 words)
Write DETAILED results with:
- Main results (400-500 words)
  * Performance comparison tables
  * Statistical significance tests
  * Analysis of results
- Ablation studies (300-400 words)
  * Impact of different components
  * Sensitivity analysis
- Qualitative analysis (100-200 words)
  * Case studies
  * Example outputs

## 6. Discussion (600-800 words)
Write THOUGHTFUL discussion with:
- Interpretation of results (250-350 words)
  * Why the method works
  * Insights gained
- Limitations (200-250 words)
  * Current limitations
  * Failure cases
- Future directions (150-200 words)
  * Potential improvements
  * Open questions

## 7. Conclusion (300-400 words)
Write COMPLETE conclusion with:
- Summary of contributions (150-200 words)
- Key findings (100-150 words)
- Broader impact (50-100 words)

## References
List 15-20 key papers to cite

WRITING GUIDELINES:
1. Write FULL paragraphs, not bullet points
2. Include technical details, equations, and formulations
3. Provide concrete examples and case studies
4. Use precise, academic language
5. Support claims with reasoning and evidence
6. Make the paper self-contained and comprehensive
7. IMPORTANT: Aim for 6,000-8,000 words total - write extensively!

Remember: This should be a COMPLETE, PUBLICATION-READY paper, not an outline!
"""
        
        draft = call_local_model("You are a research scientist writing for top ML conferences.", prompt)
        
        return draft
    
    def _critique_and_improve(self, draft: str, iteration: int) -> str:
        """Self-critique and improve the draft."""
        prompt = f"""You are a critical reviewer for a top ML conference. Review this paper draft and provide:

1. STRENGTHS (what works well)
2. WEAKNESSES (what needs improvement)
3. SPECIFIC SUGGESTIONS (concrete improvements)

Then generate an IMPROVED VERSION addressing all weaknesses.

CRITICAL: The improved version must be 6,000-8,000 words. EXPAND sections that are too brief. Add technical details, examples, and comprehensive explanations.

DRAFT:
{draft[:20000]}  # Increased limit for longer drafts

REVIEW CRITERIA:
- Novelty: Is the contribution truly novel?
- Rigor: Is the methodology sound?
- Clarity: Is the writing clear and precise?
- Completeness: Are all sections fully developed?
- Length: Is it comprehensive enough (6,000-8,000 words)?
- Impact: Will this advance the field?

OUTPUT FORMAT:
## REVIEW

### Strengths
[List strengths in detail]

### Weaknesses
[List weaknesses in detail]

### Suggestions
[Specific improvements needed]

## IMPROVED DRAFT

[Full improved paper - 6,000-8,000 words]

IMPORTANT: The improved draft must be LONGER and MORE DETAILED than the original. Expand every section with:
- More technical details
- Additional examples
- Deeper analysis
- More comprehensive explanations
- Extended literature review
- Detailed experimental descriptions
"""
        
        result = call_local_model(
            f"You are a senior researcher reviewing papers (Iteration {iteration}/2).",
            prompt
        )
        
        # Extract improved draft
        if "## IMPROVED DRAFT" in result:
            improved = result.split("## IMPROVED DRAFT")[1].strip()
        else:
            improved = result  # Fallback
        
        return improved
    
    def _finalize_paper(self, draft: str, topics: list) -> dict:
        """Finalize paper and save to file."""
        # Extract title from draft
        lines = draft.split('\n')
        title = "Untitled Paper"
        for line in lines:
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
        
        # Generate filename
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        safe_title = ''.join(c if c.isalnum() or c in ' -_' else '' for c in title)
        safe_title = safe_title.replace(' ', '_')[:50]  # Max 50 chars
        filename = f"{safe_title}-{timestamp}.md"
        filepath = os.path.join(self.papers_dir, filename)
        
        # Add metadata header
        metadata = {
            'title': title,
            'topics': topics,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'agent': 'paper_agent',
            'version': '1.0',
            'status': 'draft',
            'iterations': 2
        }
        
        # Format paper with frontmatter
        from common import serialize_frontmatter
        final_content = serialize_frontmatter(metadata, draft)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        # Calculate word count
        word_count = len(draft.split())
        
        write_log('paper_agent', 'paper_generated', f'{filename} ({word_count} words)')
        
        return {
            'title': title,
            'filename': filename,
            'filepath': filepath,
            'topics': topics,
            'word_count': word_count,
            'generated_at': metadata['generated_at']
        }
    
    def _log_paper_generation(self, metadata: dict):
        """Log paper generation to metrics DB."""
        try:
            conn = self.metrics.conn
            conn.execute("""
                INSERT INTO experiments (
                    timestamp, experiment_type, hypothesis, 
                    baseline_metric, new_metric, decision, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(timezone.utc).isoformat(),
                'paper_generation',
                f"Generate paper on {', '.join(metadata['topics'])}",
                0.0,
                float(metadata['word_count']),
                'SUCCESS',
                json.dumps(metadata)
            ))
            conn.commit()
        except Exception as e:
            print(f"   ⚠️  Failed to log to metrics: {e}")
    
    def generate_batch(self, count: int = 3, combine_topics: bool = True):
        """Generate multiple papers."""
        print(f"\n📚 Generating {count} research papers...")
        
        papers = []
        for i in range(count):
            print(f"\n{'='*80}")
            print(f"  Paper {i+1}/{count}")
            print(f"{'='*80}")
            
            try:
                paper = self.generate_paper(combine_topics=combine_topics)
                papers.append(paper)
            except Exception as e:
                print(f"\n❌ Error generating paper {i+1}: {e}")
                write_log('paper_agent_error', 'generation_failed', str(e))
        
        print(f"\n✅ Generated {len(papers)}/{count} papers")
        return papers


def main():
    """Entry point for paper agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Research Paper Agent')
    parser.add_argument('--focus', type=str, choices=FOCUS_AREAS, 
                       help='Specific focus area')
    parser.add_argument('--combine', action='store_true',
                       help='Combine multiple topics')
    parser.add_argument('--batch', type=int, default=1,
                       help='Number of papers to generate')
    
    args = parser.parse_args()
    
    agent = PaperAgent()
    
    try:
        if args.batch > 1:
            agent.generate_batch(count=args.batch, combine_topics=args.combine)
        else:
            agent.generate_paper(focus_area=args.focus, combine_topics=args.combine)
    finally:
        agent.close()


if __name__ == '__main__':
    main()
