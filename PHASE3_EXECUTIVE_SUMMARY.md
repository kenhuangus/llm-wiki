# Phase 3: Autonomous Research System — Executive Summary

**Date:** 2026-04-05  
**Prepared by:** Antigravity (Kiro AI Agent)  
**For:** Ken Huang / DistributedApps.ai

---

## The Vision

Transform the LLM Wiki from a **human-supervised knowledge pipeline** into an **autonomous research system** that continuously learns, improves itself, and advances research on agentic AI security — inspired by Andrej Karpathy's autoresearch (March 2026).

---

## What We're Building

### 1. Autonomous Orchestration (24/7 Operation)
A daemon that runs the full pipeline continuously without human intervention:
- Monitors sources (arXiv, CVE, GitHub, RSS)
- Processes 100+ sources per day
- Integrates knowledge into wiki
- Escalates only critical issues to humans

**Impact:** Reduces human workload from 15 interventions/week to <3.

### 2. Self-Improving Prompts (Meta-Learning)
An autoresearch-style "ratchet loop" that optimizes LLM prompts:
- Tests prompt modifications on evaluation set
- Keeps improvements, reverts failures
- Runs 200+ optimization cycles over 90 days
- All changes tracked in git history

**Impact:** Increases extraction confidence from 0.72 to 0.85+ (18% improvement).

### 3. Autonomous Research Agent
Proactive system that identifies knowledge gaps and seeks answers:
- Detects domains with <50 pages or low confidence
- Generates hypotheses (search, synthesis, validation)
- Executes experiments within daily budget
- Logs all results for human review

**Impact:** Generates 50+ novel research hypotheses in 90 days.

### 4. Quality Feedback Loop
Retrospective validation that checks if old claims still hold:
- Compares old claims against new sources
- Detects contradictions automatically
- Adjusts confidence scores dynamically
- Flags critical conflicts for human review

**Impact:** Catches 90% of contradictions, reduces error rate to <5%.

---

## The Autoresearch Pattern

Karpathy's autoresearch (33,000+ GitHub stars in first week) demonstrated:
> "Give an AI agent a GPU and training code, let it modify the script, run experiments, and keep changes that improve performance. Repeat overnight."

We apply this to knowledge work:
> "Give an AI agent the wiki corpus and processing scripts, let it modify extraction prompts, run pipeline cycles, and keep changes that improve knowledge quality. Repeat continuously."

### Three-File Architecture

| File | Owner | Purpose |
|------|-------|---------|
| `AGENTS.md` + metrics | Immutable | Quality standards (neither human nor agent modifies during runs) |
| `prompts.py` | Agent sandbox | Extraction/integration prompts (agent can modify) |
| `research_agenda.md` | Human | Research priorities, constraints, success criteria |

This separation ensures:
- Agent has freedom to experiment
- Quality standards remain stable
- Human maintains strategic control

---

## Success Metrics (90-Day Targets)

| Metric | Phase 2 Baseline | Phase 3 Target | Improvement |
|--------|------------------|----------------|-------------|
| Wiki pages | 150 | 500+ | 3.3x |
| Avg extraction confidence | 0.72 | 0.85+ | +18% |
| Integration conflict rate | 12% | <5% | -58% |
| Lint pass rate | 88% | ≥95% | +8% |
| Human interventions/week | 15 | <3 | -80% |
| Novel hypotheses tested | 0 | 50+ | New capability |
| Research outputs supported | 0 | 1+ paper/framework | New capability |

---

## Implementation Timeline

### 6-Week Roadmap

**Week 1: Foundation**
- Externalize prompts to `prompts.py`
- Create `research_agenda.md` with initial priorities
- Set up metrics database
- Curate 50-source evaluation test set

**Week 2: Autonomous Orchestration**
- Implement 24/7 daemon with priority queue
- Add CVE fast-track (CVSS ≥ 7.0)
- Test continuous operation for 24 hours

**Week 3: Meta-Learning**
- Implement prompt optimizer with ratchet loop
- Run 100-cycle overnight optimization
- Measure quality improvement

**Week 4: Autonomous Research**
- Implement hypothesis generation
- Add knowledge gap detection
- Test 7-day autonomous run

**Week 5: Quality Feedback**
- Implement retrospective validator
- Add contradiction detection
- Run weekly validation cycle

**Week 6: Integration & Testing**
- Connect all components
- Create monitoring dashboard
- Run 30-day autonomous trial

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Runaway LLM costs | Hard daily budget limit in research agenda |
| Quality degradation | Ratchet only accepts improvements; bad changes auto-revert |
| Knowledge drift | Immutable AGENTS.md defines quality standards |
| Circular reasoning | Fixed evaluation test set prevents overfitting |
| Agent gets stuck | Diversity directives + human can reset to earlier checkpoint |

---

## Why This Matters for Agentic AI Security Research

### Current Problem
- Agentic AI security is a fast-moving field
- New CVEs, papers, and frameworks appear weekly
- Manual curation cannot keep pace
- Knowledge is fragmented across sources

### Phase 3 Solution
- Continuous ingestion keeps wiki current
- Autonomous research identifies gaps proactively
- Self-improvement ensures quality increases over time
- System becomes authoritative knowledge base for the field

### Research Output Potential
With 500+ pages of synthesized knowledge:
- Generate threat taxonomy papers
- Contribute to OWASP LLM Top 10 updates
- Create MAESTRO framework extensions
- Publish security best practices for coding agents

---

## Comparison to Existing Systems

| System | Approach | Limitation | Phase 3 Advantage |
|--------|----------|------------|-------------------|
| Traditional RAG | Stateless retrieval | No learning | Persistent, self-improving wiki |
| AutoML (Optuna, Ray Tune) | Hyperparameter search | Fixed search space | LLM proposes arbitrary improvements |
| AlphaEvolve (DeepMind) | Evolutionary algorithms | Closed-source | Open, reproducible, local-first |
| SWE-Agent, Aider | General coding agents | No experiment loop | Ratchet-based quality improvement |
| Manual curation | Human-driven | Cannot scale | Autonomous with human oversight |

---

## Investment Required

### Technical Resources
- Python 3.11+, 16GB+ RAM (already have)
- GPU with 24GB+ VRAM for local LLM (already have: Ken-Mac 26B)
- ~500GB storage (already provisioned)

### Development Time
- 6 weeks for core implementation
- 1-2 hours/week human oversight after deployment
- Weekly review of experiment log (30 min)

### LLM API Costs
- Estimated: $50-100/month for 100+ experiments/day
- Hard budget limit configurable in research agenda
- Primarily uses local LLM (Ken-Mac), cloud as fallback

---

## Next Steps

### Immediate (This Week)
1. Review Phase 3 plan with human operator
2. Prioritize components (all 5 or subset?)
3. Set 90-day success criteria
4. Begin Week 1 implementation

### Decision Points
- **Scope:** Implement all 5 components or start with daemon + meta-learning?
- **Timeline:** 6-week sprint or phased rollout?
- **Oversight:** Daily check-ins or weekly reviews?
- **Budget:** What's the acceptable monthly LLM cost?

### Approval Needed
- [ ] Approve overall Phase 3 vision
- [ ] Approve 6-week implementation timeline
- [ ] Approve success metrics (90-day targets)
- [ ] Approve LLM budget allocation
- [ ] Approve human oversight cadence (weekly reviews)

---

## References

- **Autoresearch:** [github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- **DataCamp Guide:** [datacamp.com/tutorial/guide-to-autoresearch](https://www.datacamp.com/tutorial/guide-to-autoresearch)
- **Current System:** `llm-wiki.md` (PRD), `AGENTS.md` (behavioral schema), `task.md` (Phase 1-2 complete)
- **Detailed Plan:** `PHASE3_AUTONOMOUS_RESEARCH_PLAN.md` (full specification)
- **Architecture:** `AUTONOMOUS_LOOP_DIAGRAM.md` (visual diagrams)

---

## Bottom Line

Phase 3 transforms the LLM Wiki from a **tool you operate** into a **research partner that operates itself** — continuously learning, improving, and advancing knowledge on agentic AI security while you focus on strategic direction and high-value research outputs.

**Estimated ROI:** 80% reduction in manual curation time, 3.3x increase in knowledge coverage, enabling 1+ publishable research output within 6 months.

**Ready to proceed?** Review the detailed plan in `PHASE3_AUTONOMOUS_RESEARCH_PLAN.md` and approve next steps.
