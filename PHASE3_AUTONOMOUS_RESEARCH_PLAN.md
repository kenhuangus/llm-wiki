# Phase 3: Autonomous Research & Recursive Self-Improvement Plan

**Date:** 2026-04-05  
**Status:** Design Phase  
**Inspired by:** karpathy/autoresearch (March 2026)

---

## Executive Summary

Transform the LLM Wiki from a **human-supervised knowledge pipeline** into an **autonomous research system** that:
1. Continuously ingests, normalizes, extracts, and integrates knowledge without human intervention
2. Recursively improves its own extraction/integration prompts based on quality metrics
3. Generates novel research hypotheses and validates them against the wiki corpus
4. Advances research on agentic AI security through autonomous experimentation

---

## Current State Analysis

### ✅ What We Have (Phase 1-2 Complete)
- **Ingestion Pipeline**: arXiv, CVE, GitHub, RSS monitors with deduplication (SQLite state DB)
- **Normalization**: Format conversion to markdown with frontmatter
- **Extraction**: LLM-based entity/claim extraction (`extract.py`)
- **Integration**: LLM-based wiki page merging with conflict detection (`integrate.py`)
- **Quality Control**: Lightweight + deep lint, confidence scoring, source attribution
- **Human Oversight**: Manual review triggers for conflicts, low confidence, critical CVEs
- **UI**: React dashboard with semantic search, batch ingest, monitoring

### ❌ What's Missing for Full Autonomy

#### 1. **No Autonomous Execution Loop**
- Current: Each tool (`ingest.py`, `normalize.py`, etc.) runs independently via manual/cron trigger
- Needed: Continuous daemon that orchestrates the full pipeline end-to-end
- Gap: No "ratchet loop" like autoresearch — no automatic quality-based acceptance/rejection

#### 2. **No Self-Improvement Mechanism**
- Current: LLM prompts in `extract.py` and `integrate.py` are static
- Needed: Meta-learning layer that optimizes prompts based on downstream quality metrics
- Gap: System cannot learn from its own mistakes or improve extraction accuracy over time

#### 3. **No Hypothesis Generation**
- Current: System is purely reactive — processes whatever sources arrive
- Needed: Proactive research agent that identifies knowledge gaps and seeks answers
- Gap: No "research agenda" equivalent to autoresearch's `program.md`

#### 4. **No Quality Feedback Loop**
- Current: Confidence scores are assigned once during extraction, never validated
- Needed: Retrospective validation — check if extracted claims hold up against new sources
- Gap: No mechanism to detect and correct past extraction errors

#### 5. **Limited Cross-Domain Synthesis**
- Current: Integration happens page-by-page; no global reasoning
- Needed: Periodic synthesis runs that connect insights across domains
- Gap: System doesn't "think" about the wiki as a whole

#### 6. **No Experiment Tracking**
- Current: `log.md` records operations but not outcomes
- Needed: Structured experiment log tracking hypothesis → action → result → decision
- Gap: Cannot measure system improvement over time

---

## Autoresearch Pattern Applied to Wiki System

### Core Insight from Autoresearch
> "Give an AI agent a single GPU and training code, let it modify the script, run experiments, and keep the changes that improve performance. Repeat overnight."

### Translation to Wiki Context
> "Give an AI agent the wiki corpus and processing scripts, let it modify extraction/integration prompts, run pipeline cycles, and keep the changes that improve knowledge quality. Repeat continuously."

### Three-File Architecture Mapping

| Autoresearch | LLM Wiki Equivalent | Purpose |
|--------------|---------------------|---------|
| `prepare.py` (immutable) | `AGENTS.md` + quality metrics | Defines evaluation criteria; neither human nor agent modifies during runs |
| `train.py` (agent sandbox) | `prompts.py` (NEW) | Agent can modify extraction/integration prompts to improve quality |
| `program.md` (human direction) | `research_agenda.md` (NEW) | Human sets research priorities, constraints, and success criteria |

### Ratchet Loop for Wiki

```
1. Read research_agenda.md (current priorities)
2. Examine recent integration quality metrics (confidence, conflicts, coverage)
3. Propose hypothesis: "Improve CVE extraction by adding CVSS parsing to prompt"
4. Modify prompts.py to implement change
5. Commit change to git branch
6. Run pipeline on 10 test sources (fixed evaluation set)
7. If crashes: log failure, revert, try again
8. Evaluate: Did avg confidence increase? Did conflicts decrease?
9. If improved: keep commit. If not: git reset HEAD~1
10. Repeat from step 1
```

---

## Phase 3 Implementation Plan

### 3.1 Autonomous Orchestration Daemon

**File:** `tools/daemon.py`

**Responsibilities:**
- Continuous loop: ingest → normalize → extract → integrate → lint → index
- Priority queue: CVE CVSS ≥ 7.0 gets immediate processing
- Resource management: respect LLM rate limits, GPU availability
- Graceful degradation: if main LLM fails, use backup; if both fail, queue for retry
- Human escalation: pause on critical conflicts (CVSS ≥ 9.0, contradictions in verified pages)

**Key Features:**
```python
class WikiDaemon:
    def __init__(self):
        self.queue = PriorityQueue()  # (priority, source_path)
        self.metrics = MetricsCollector()
        self.running = True
    
    def run(self):
        while self.running:
            # 1. Poll monitors for new sources
            self.poll_monitors()
            
            # 2. Process queue (highest priority first)
            while not self.queue.empty():
                priority, source = self.queue.get()
                self.process_source(source)
            
            # 3. Periodic maintenance
            if self.should_run_lint():
                self.run_lint()
            if self.should_rebuild_index():
                self.rebuild_index()
            
            # 4. Sleep until next cycle
            time.sleep(self.poll_interval)
    
    def process_source(self, source_path):
        """Full pipeline: normalize → extract → integrate → index"""
        try:
            normalized = normalize(source_path)
            extracted = extract(normalized)
            integrated = integrate(extracted)
            self.metrics.record_success(source_path, integrated)
        except Exception as e:
            self.metrics.record_failure(source_path, e)
            self.queue.put((RETRY_PRIORITY, source_path))
```

**Success Criteria:**
- Runs 24/7 without human intervention (except critical escalations)
- Processes 100+ sources/day with <1% failure rate
- Maintains wiki consistency (lint pass rate ≥ 95%)

---

### 3.2 Prompt Optimization System (Meta-Learning)

**File:** `tools/prompts.py` (NEW - agent-modifiable)

**Current Problem:**
- Extraction prompt in `extract.py` is hardcoded:
  ```python
  system_prompt = "You are a data extractor. Output ONLY valid JSON..."
  ```
- Integration prompt in `integrate.py` is hardcoded:
  ```python
  system_prompt = "You are a markdown editor. Merge the old claims..."
  ```

**Solution: Externalize and Version Prompts**

```python
# prompts.py (agent can modify this file)
EXTRACTION_PROMPT_V1 = """
You are a knowledge extraction specialist for agentic AI security research.

INPUT: Markdown document with frontmatter
OUTPUT: Valid JSON with this exact structure:
{
  "entities": [{"name": str, "type": str, "confidence": float}],
  "claims": [{"text": str, "confidence": float, "evidence": str}],
  "relationships": [{"source": str, "relation": str, "target": str}]
}

RULES:
- Confidence must be 0.0-1.0 based on evidence strength
- Extract CVE IDs, CVSS scores, affected systems explicitly
- Flag contradictions with existing knowledge if detected
- Cite specific sentences as evidence for each claim
"""

INTEGRATION_PROMPT_V1 = """
You are a wiki integration specialist.

TASK: Merge new claims into existing wiki page while preserving attribution.

RULES:
- If claims contradict: keep both, add [CONFLICT] tag, output "STATUS: CONFLICT"
- If claims reinforce: merge and increment source_count
- Update confidence: weighted average based on source trust tiers
- Preserve all source citations
- Move outdated claims to ## Historical Claims section
"""

# Prompt registry (tracks which version is active)
ACTIVE_PROMPTS = {
    "extraction": "EXTRACTION_PROMPT_V1",
    "integration": "INTEGRATION_PROMPT_V1"
}
```

**File:** `tools/prompt_optimizer.py` (NEW - meta-learning agent)

```python
class PromptOptimizer:
    """Autoresearch-style ratchet for prompt improvement"""
    
    def __init__(self):
        self.eval_set = self.load_evaluation_set()  # 50 curated test sources
        self.baseline_metrics = self.run_baseline()
    
    def run_optimization_cycle(self):
        """Single iteration of prompt improvement"""
        # 1. Analyze recent failures
        failures = self.metrics.get_recent_failures()
        
        # 2. Propose prompt modification
        hypothesis = self.generate_hypothesis(failures)
        
        # 3. Modify prompts.py
        new_prompt = self.apply_hypothesis(hypothesis)
        self.commit_prompt_change(new_prompt, hypothesis)
        
        # 4. Evaluate on test set
        metrics = self.evaluate_on_test_set(new_prompt)
        
        # 5. Keep or revert
        if self.is_improvement(metrics, self.baseline_metrics):
            print(f"✓ Kept: {hypothesis} (Δ confidence: +{metrics.delta})")
            self.baseline_metrics = metrics
        else:
            print(f"✗ Reverted: {hypothesis} (no improvement)")
            self.git_revert()
    
    def evaluate_on_test_set(self, prompt):
        """Run extraction on 50 test sources, measure quality"""
        results = []
        for source in self.eval_set:
            extracted = extract_with_prompt(source, prompt)
            integrated = integrate(extracted)
            
            # Quality metrics
            results.append({
                "avg_confidence": np.mean([c["confidence"] for c in extracted["claims"]]),
                "conflict_rate": 1 if "CONFLICT" in integrated else 0,
                "entity_count": len(extracted["entities"]),
                "json_valid": True  # made it this far
            })
        
        return MetricsSummary(results)
```

**Success Criteria:**
- After 100 optimization cycles: avg extraction confidence increases by ≥10%
- Conflict rate decreases (fewer false contradictions)
- JSON parsing errors decrease to <1%

---

### 3.3 Research Agenda System

**File:** `research_agenda.md` (NEW - human-authored, agent-read)

```markdown
# LLM Wiki Research Agenda

## Current Priorities (2026-04-05)

### 1. Agentic AI Security Threat Taxonomy
**Goal:** Build comprehensive taxonomy of attack vectors against agentic systems
**Success Criteria:** 
- ≥50 distinct attack patterns documented in `/wiki/security/attack-patterns/`
- Each pattern linked to ≥1 real-world CVE or incident
- Cross-referenced with OWASP LLM Top 10 and MAESTRO framework

**Research Directions:**
- Prompt injection variants (direct, indirect, multi-hop)
- Tool misuse patterns (API abuse, data exfiltration)
- Memory poisoning attacks (episodic, semantic, procedural)
- Multi-agent coordination exploits

**Constraints:**
- Do NOT create speculative attack patterns without evidence
- All patterns must cite ≥2 independent sources (Tier 1 or Tier 2)

### 2. CVE Coverage for Coding Agents
**Goal:** Track all vulnerabilities affecting major coding agent frameworks
**Success Criteria:**
- 100% coverage of CVEs affecting: LangChain, OpenAI SDK, Anthropic SDK, AutoGen, CrewAI
- CVSS ≥ 7.0 CVEs integrated within 4 hours of NVD publication
- Each CVE page includes: exploit mechanism, affected versions, mitigations, related CVEs

**Research Directions:**
- Monitor GitHub security advisories for target repos
- Cross-reference CVEs with attack patterns
- Track patch adoption rates

### 3. Foundation Model Capability Tracking
**Goal:** Maintain up-to-date comparison of LLM capabilities for agentic tasks
**Success Criteria:**
- Comparison pages for: GPT-4, Claude 3.5, Gemini 2.0, Llama 4, Qwen 3
- Benchmarks: tool use accuracy, multi-step reasoning, code generation security
- Updated within 7 days of new model release

## Autonomous Experiment Directives

### Hypothesis Generation Rules
- Identify knowledge gaps: domains with <50 pages or avg confidence <0.7
- Propose synthesis opportunities: ≥3 related pages with no comparison page
- Flag outdated claims: sources >90 days old in fast-moving domains (LLM benchmarks)

### Experiment Constraints
- Max 10 experiments per day (LLM budget constraint)
- Each experiment must have clear success metric
- Log all experiments to `wiki/experiments.md`

### Quality Thresholds
- Extraction confidence target: ≥0.75 avg across all domains
- Integration conflict rate target: <5% of integrations
- Lint pass rate target: ≥95% at all times

## Prohibited Actions
- Do NOT modify `AGENTS.md` without human approval
- Do NOT delete conflicting claims (move to Historical Claims)
- Do NOT promote Tier 3 sources to verified without cross-validation
- Do NOT run experiments that would exceed daily LLM budget
```

**File:** `tools/research_agent.py` (NEW - autonomous hypothesis generation)

```python
class ResearchAgent:
    """Proactive research agent that identifies gaps and seeks answers"""
    
    def generate_daily_hypotheses(self):
        """Analyze wiki state and propose research directions"""
        gaps = self.identify_knowledge_gaps()
        hypotheses = []
        
        for gap in gaps:
            if gap.type == "coverage":
                # Domain has <50 pages
                hypotheses.append({
                    "type": "coverage_expansion",
                    "domain": gap.domain,
                    "action": f"Search arXiv for recent papers on {gap.domain}",
                    "success_metric": f"Add ≥10 new pages to {gap.domain}"
                })
            
            elif gap.type == "synthesis":
                # Multiple related pages, no comparison
                hypotheses.append({
                    "type": "synthesis",
                    "pages": gap.related_pages,
                    "action": f"Create comparison page for {gap.topic}",
                    "success_metric": "Comparison page with ≥3 dimensions"
                })
            
            elif gap.type == "validation":
                # Low-confidence claims need cross-validation
                hypotheses.append({
                    "type": "validation",
                    "page": gap.page,
                    "action": f"Search for additional sources on {gap.topic}",
                    "success_metric": "Increase confidence from {gap.current} to ≥0.75"
                })
        
        return hypotheses
    
    def execute_hypothesis(self, hypothesis):
        """Run experiment to test hypothesis"""
        if hypothesis["type"] == "coverage_expansion":
            # Trigger targeted arXiv search
            results = self.search_arxiv(hypothesis["domain"])
            for paper in results:
                self.queue_for_ingestion(paper)
        
        elif hypothesis["type"] == "synthesis":
            # Generate comparison page
            pages = [self.load_page(p) for p in hypothesis["pages"]]
            comparison = self.synthesize_comparison(pages)
            self.write_page(comparison)
        
        elif hypothesis["type"] == "validation":
            # Search for corroborating sources
            sources = self.search_web(hypothesis["topic"])
            for source in sources:
                self.queue_for_ingestion(source)
        
        # Log experiment
        self.log_experiment(hypothesis, outcome)
```

**Success Criteria:**
- Generates ≥5 valid hypotheses per day
- 60% of hypotheses lead to measurable wiki improvement
- No hypothesis violates constraints in `research_agenda.md`

---

### 3.4 Quality Feedback Loop

**File:** `tools/retrospective_validator.py` (NEW)

```python
class RetrospectiveValidator:
    """Validates past extractions against new evidence"""
    
    def run_weekly_validation(self):
        """Check if old claims still hold up"""
        # 1. Find pages updated in last 7 days
        recent_pages = self.get_recently_updated_pages()
        
        # 2. For each page, check if new sources contradict old claims
        for page in recent_pages:
            old_claims = self.get_claims_older_than(page, days=30)
            new_sources = self.get_sources_newer_than(page, days=7)
            
            for claim in old_claims:
                # Ask LLM: "Does this new source contradict this old claim?"
                contradictions = self.check_contradictions(claim, new_sources)
                
                if contradictions:
                    self.flag_for_review(page, claim, contradictions)
                    self.update_confidence(claim, decrease=0.1)
        
        # 3. Find claims that have been reinforced
        for page in recent_pages:
            claims = page.claims
            for claim in claims:
                supporting_sources = self.count_supporting_sources(claim)
                if supporting_sources >= 3:
                    self.update_confidence(claim, increase=0.1)
                    if claim.confidence >= 0.9:
                        self.mark_verified(claim)
```

**Success Criteria:**
- Catches ≥90% of contradictions introduced by new sources
- Confidence scores converge toward ground truth over time
- Verified claims have <5% error rate when spot-checked

---

### 3.5 Experiment Tracking System

**File:** `wiki/experiments.md` (NEW - append-only log)

```markdown
# Autonomous Experiments Log

## 2026-04-05

### Experiment #001: Improve CVE Extraction Prompt
- **Hypothesis:** Adding explicit CVSS parsing instruction will increase extraction accuracy
- **Change:** Modified `EXTRACTION_PROMPT_V1` to include "Extract CVSS score from CVE description"
- **Evaluation:** Ran on 50 test CVEs
- **Results:**
  - Baseline: 68% of CVEs had CVSS score extracted
  - Modified: 94% of CVEs had CVSS score extracted
  - Δ: +26 percentage points
- **Decision:** ✓ KEPT (commit: a1b2c3d4)

### Experiment #002: Add Relationship Extraction
- **Hypothesis:** Extracting entity relationships will improve cross-linking
- **Change:** Added "relationships" field to extraction JSON schema
- **Evaluation:** Ran on 50 test papers
- **Results:**
  - Baseline: 12 cross-links per page (manual)
  - Modified: 8 cross-links per page (auto-generated)
  - Quality: 60% of auto-links were valid
- **Decision:** ✗ REVERTED (too many false positives)

### Experiment #003: Targeted arXiv Search for "prompt injection"
- **Hypothesis:** Coverage gap in prompt injection attack patterns
- **Action:** Searched arXiv for "prompt injection" papers from 2025-2026
- **Results:**
  - Found 12 relevant papers
  - Ingested 8 (4 duplicates)
  - Created 3 new attack pattern pages
  - Updated 2 existing pages
- **Decision:** ✓ SUCCESS (coverage increased from 8 to 11 attack patterns)
```

**File:** `tools/metrics_collector.py` (NEW)

```python
class MetricsCollector:
    """Tracks system performance over time"""
    
    def __init__(self):
        self.db = sqlite3.connect('metrics.db')
        self.init_tables()
    
    def record_extraction(self, source_id, metrics):
        """Log extraction quality metrics"""
        self.db.execute("""
            INSERT INTO extractions (source_id, timestamp, avg_confidence, 
                                     entity_count, claim_count, json_valid)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (source_id, datetime.now(), metrics.avg_confidence, 
              metrics.entity_count, metrics.claim_count, metrics.json_valid))
    
    def record_integration(self, page_path, metrics):
        """Log integration outcomes"""
        self.db.execute("""
            INSERT INTO integrations (page_path, timestamp, conflict_detected,
                                      claims_added, confidence_delta)
            VALUES (?, ?, ?, ?, ?)
        """, (page_path, datetime.now(), metrics.conflict, 
              metrics.claims_added, metrics.confidence_delta))
    
    def get_trend(self, metric_name, days=30):
        """Get time series for a metric"""
        return self.db.execute("""
            SELECT timestamp, AVG(?) as value
            FROM extractions
            WHERE timestamp > datetime('now', '-? days')
            GROUP BY date(timestamp)
            ORDER BY timestamp
        """, (metric_name, days)).fetchall()
```

---

## Implementation Roadmap

### Week 1: Foundation
- [ ] Create `prompts.py` with externalized prompts
- [ ] Refactor `extract.py` and `integrate.py` to use `prompts.py`
- [ ] Create `research_agenda.md` with initial priorities
- [ ] Set up `metrics.db` schema
- [ ] Create evaluation test set (50 curated sources)

### Week 2: Autonomous Orchestration
- [ ] Implement `daemon.py` with basic loop
- [ ] Add priority queue with CVE fast-track
- [ ] Integrate with existing monitors
- [ ] Add graceful degradation (LLM fallback)
- [ ] Test 24-hour continuous run

### Week 3: Meta-Learning
- [ ] Implement `prompt_optimizer.py`
- [ ] Run 10 manual optimization cycles to validate
- [ ] Add git integration for prompt versioning
- [ ] Create prompt evaluation metrics
- [ ] Run 100-cycle overnight optimization

### Week 4: Autonomous Research
- [ ] Implement `research_agent.py`
- [ ] Add knowledge gap detection
- [ ] Add hypothesis generation
- [ ] Add experiment execution
- [ ] Test 7-day autonomous run

### Week 5: Quality Feedback
- [ ] Implement `retrospective_validator.py`
- [ ] Add contradiction detection
- [ ] Add confidence adjustment logic
- [ ] Run weekly validation cycle
- [ ] Measure accuracy improvement

### Week 6: Integration & Testing
- [ ] Connect all components into unified daemon
- [ ] Add experiment logging to `experiments.md`
- [ ] Create monitoring dashboard (extend UI)
- [ ] Run 30-day autonomous trial
- [ ] Measure against success metrics

---

## Success Metrics (90-Day Targets)

| Metric | Baseline (Phase 2) | Target (Phase 3) |
|--------|-------------------|------------------|
| Wiki pages | 150 | 500+ |
| Avg extraction confidence | 0.72 | 0.85+ |
| Integration conflict rate | 12% | <5% |
| Lint pass rate | 88% | ≥95% |
| Human interventions/week | 15 | <3 |
| Novel hypotheses tested | 0 | 50+ |
| Prompt optimization cycles | 0 | 200+ |
| Research outputs supported | 0 | 1+ (paper/framework) |

---

## Risk Mitigation

### Risk: Runaway LLM Costs
- **Mitigation:** Hard daily budget limit in `research_agenda.md`
- **Fallback:** Pause autonomous experiments if budget exceeded

### Risk: Quality Degradation
- **Mitigation:** Ratchet only accepts improvements; bad changes auto-revert
- **Fallback:** Weekly human review of experiment log

### Risk: Knowledge Drift
- **Mitigation:** Immutable `AGENTS.md` defines quality standards
- **Fallback:** Git history allows rollback to any previous state

### Risk: Circular Reasoning
- **Mitigation:** Evaluation test set is fixed; agent cannot overfit to it
- **Fallback:** Periodic refresh of test set with new curated sources

### Risk: Agent Gets Stuck
- **Mitigation:** Diversity directives in `research_agenda.md`
- **Fallback:** Human can reset to earlier checkpoint and modify agenda

---

## Open Questions

1. **Evaluation Set Curation:** Who maintains the 50-source test set? How often is it refreshed?
2. **Prompt Versioning:** Should we keep all historical prompts or prune failed experiments?
3. **Multi-Agent Coordination:** Can multiple research agents work in parallel without conflicts?
4. **Human Review Cadence:** Daily check-ins vs weekly deep reviews?
5. **Production Cutover:** When is the system trusted enough to run unsupervised?

---

## References

- [karpathy/autoresearch](https://github.com/karpathy/autoresearch) - Autonomous ML experimentation
- [DataCamp Guide to AutoResearch](https://www.datacamp.com/tutorial/guide-to-autoresearch) - Architecture analysis
- Current system: `llm-wiki.md` (PRD), `AGENTS.md` (behavioral schema), `task.md` (Phase 1-2 completion)

---

**Next Steps:** Review this plan with human operator, prioritize components, begin Week 1 implementation.
