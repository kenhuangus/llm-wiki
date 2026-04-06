# Phase 3 Design Complete — Quick Start Guide

**Status:** ✅ Design phase complete, ready for implementation approval  
**Date:** 2026-04-05  
**Commit:** a86e671

---

## What Just Happened?

I analyzed your request to make the system "fully armed with LLM for wiki processing from ingestion, normalization, lint, and recursive self-improvement" inspired by karpathy/autoresearch. I've created a comprehensive Phase 3 design that transforms the wiki from a human-supervised pipeline into an autonomous research system.

---

## Documents Created (4 Files)

### 1. **PHASE3_EXECUTIVE_SUMMARY.md** ⭐ START HERE
**Purpose:** High-level overview for decision-making  
**Read time:** 5 minutes  
**Contains:**
- The vision (what we're building and why)
- Success metrics (90-day targets)
- 6-week implementation timeline
- Risk mitigation strategies
- Investment required (time, resources, costs)
- Approval checklist

**Key takeaway:** 80% reduction in manual work, 3.3x knowledge coverage, enables publishable research outputs.

---

### 2. **PHASE3_AUTONOMOUS_RESEARCH_PLAN.md** 📋 DETAILED SPEC
**Purpose:** Complete technical specification  
**Read time:** 20 minutes  
**Contains:**
- Current state analysis (what's missing for full autonomy)
- Autoresearch pattern applied to wiki context
- 5 core components with code examples:
  1. Autonomous Orchestration Daemon
  2. Prompt Optimization System (Meta-Learning)
  3. Research Agenda System
  4. Quality Feedback Loop
  5. Experiment Tracking System
- Week-by-week implementation roadmap
- Success metrics and risk mitigation
- Open questions for discussion

**Key takeaway:** Detailed blueprint for building the autonomous system.

---

### 3. **AUTONOMOUS_LOOP_DIAGRAM.md** 🎨 VISUAL GUIDE
**Purpose:** Architecture diagrams and data flow  
**Read time:** 10 minutes  
**Contains:**
- System overview diagram (layers and components)
- Ratchet loop detail (how prompt optimization works)
- Research agent workflow (hypothesis generation)
- Quality feedback loop (retrospective validation)
- Data flow summary
- Autonomy levels (0-5 scale)

**Key takeaway:** Visual understanding of how all pieces fit together.

---

### 4. **task.md** (Updated) ✏️ PROJECT TRACKER
**Purpose:** Master task list with Phase 3 section  
**Contains:**
- Phase 1-2 completion status (all ✅)
- Phase 3 detailed checklist (6-week roadmap)
- Success metrics table
- Implementation roadmap
- Future enhancements

**Key takeaway:** Single source of truth for project status.

---

## The Core Idea (Autoresearch Pattern)

### Karpathy's Autoresearch (March 2026)
> "Give an AI agent a single GPU and training code, let it modify the script, run experiments, and keep the changes that improve performance. Repeat overnight."

**Result:** 83 experiments overnight, 15 improvements kept, validation loss improved from 1.000 → 0.975

### Applied to LLM Wiki
> "Give an AI agent the wiki corpus and processing scripts, let it modify extraction/integration prompts, run pipeline cycles, and keep the changes that improve knowledge quality. Repeat continuously."

**Expected result:** 200+ optimization cycles in 90 days, extraction confidence improves from 0.72 → 0.85+

---

## Three-File Architecture (Key Innovation)

| File | Owner | Purpose |
|------|-------|---------|
| `AGENTS.md` + quality metrics | **Immutable** | Evaluation criteria (neither human nor agent modifies during runs) |
| `prompts.py` | **Agent sandbox** | Extraction/integration prompts (agent can modify) |
| `research_agenda.md` | **Human** | Research priorities, constraints, success criteria |

This separation ensures:
- ✅ Agent has freedom to experiment
- ✅ Quality standards remain stable
- ✅ Human maintains strategic control

---

## 5 Core Components

### 1. Autonomous Orchestration Daemon (`tools/daemon.py`)
- Runs 24/7: ingest → normalize → extract → integrate → lint → index
- Priority queue: CVE CVSS ≥ 7.0 gets immediate processing
- Target: 100+ sources/day, <1% failure rate

### 2. Prompt Optimization System (`tools/prompt_optimizer.py`)
- Autoresearch-style ratchet loop
- Tests prompt modifications on 50-source evaluation set
- Keeps improvements, reverts failures
- Target: +18% extraction confidence after 100 cycles

### 3. Research Agenda System (`tools/research_agent.py`)
- Identifies knowledge gaps (domains <50 pages, confidence <0.7)
- Generates hypotheses (search, synthesis, validation)
- Executes experiments within daily budget
- Target: 50+ novel hypotheses in 90 days

### 4. Quality Feedback Loop (`tools/retrospective_validator.py`)
- Checks if old claims hold up against new sources
- Detects contradictions automatically
- Adjusts confidence scores dynamically
- Target: 90% contradiction detection rate

### 5. Experiment Tracking System (`wiki/experiments.md` + `metrics.db`)
- Logs all experiments: hypothesis → action → result → decision
- Time-series metrics: extraction quality, integration outcomes
- Audit trail for human review
- Target: 200+ experiments logged in 90 days

---

## Success Metrics (90-Day Targets)

| Metric | Phase 2 | Phase 3 | Improvement |
|--------|---------|---------|-------------|
| Wiki pages | 150 | 500+ | **3.3x** |
| Avg extraction confidence | 0.72 | 0.85+ | **+18%** |
| Integration conflict rate | 12% | <5% | **-58%** |
| Human interventions/week | 15 | <3 | **-80%** |
| Novel hypotheses tested | 0 | 50+ | **New** |

---

## Implementation Timeline

### 6-Week Sprint

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Foundation | Externalized prompts, research agenda, metrics DB, test set |
| 2 | Orchestration | 24/7 daemon with priority queue, 24h test run |
| 3 | Meta-Learning | Prompt optimizer with ratchet loop, 100-cycle overnight run |
| 4 | Research | Hypothesis generation, gap detection, 7-day autonomous run |
| 5 | Feedback | Retrospective validator, contradiction detection, weekly cycle |
| 6 | Integration | Unified daemon, monitoring dashboard, 30-day trial |

---

## What You Need to Decide

### Approval Checklist
- [ ] **Vision:** Approve autonomous research system concept
- [ ] **Scope:** All 5 components or phased rollout?
- [ ] **Timeline:** 6-week sprint or longer timeline?
- [ ] **Budget:** Acceptable monthly LLM cost ($50-100/month)?
- [ ] **Oversight:** Daily check-ins or weekly reviews?
- [ ] **Success Metrics:** Agree on 90-day targets?

### Key Questions
1. **When to start?** Ready to begin Week 1 implementation now?
2. **Resource allocation?** Can dedicate 6 weeks to this?
3. **Risk tolerance?** Comfortable with autonomous system making decisions?
4. **Review cadence?** Weekly experiment log review acceptable?

---

## Next Steps

### Option A: Full Implementation (Recommended)
1. Review `PHASE3_EXECUTIVE_SUMMARY.md` (5 min)
2. Approve vision and timeline
3. Begin Week 1 implementation immediately
4. Weekly check-ins to review progress

### Option B: Phased Rollout
1. Start with Weeks 1-2 (daemon + orchestration)
2. Validate continuous operation
3. Decide on meta-learning (Weeks 3-4) after seeing results
4. Add research agent (Weeks 5-6) if successful

### Option C: Pilot Study
1. Implement prompt optimizer only (Week 3 component)
2. Run 100-cycle optimization overnight
3. Measure improvement
4. Decide on full system based on results

---

## How to Read the Documents

### If you have 5 minutes:
→ Read `PHASE3_EXECUTIVE_SUMMARY.md`

### If you have 15 minutes:
→ Read `PHASE3_EXECUTIVE_SUMMARY.md` + `AUTONOMOUS_LOOP_DIAGRAM.md`

### If you have 30 minutes:
→ Read all 3 documents (summary, diagrams, detailed plan)

### If you want to start coding:
→ Read `PHASE3_AUTONOMOUS_RESEARCH_PLAN.md` Section 3.1 (Daemon) and begin Week 1

---

## Questions?

Common questions answered in the detailed plan:
- **Q: How does the ratchet loop work?** → See Section 3.2 + diagrams
- **Q: What if the agent makes bad changes?** → Git auto-reverts failures
- **Q: How do we control what the agent does?** → `research_agenda.md` (human-authored)
- **Q: What about LLM costs?** → Hard budget limit in agenda, primarily uses local LLM
- **Q: How do we know it's working?** → `metrics.db` tracks all quality metrics over time

---

## Bottom Line

Phase 3 transforms the wiki from a **tool you operate** into a **research partner that operates itself** — inspired by Karpathy's autoresearch breakthrough (33,000+ GitHub stars in first week).

**Investment:** 6 weeks implementation + 1-2 hours/week oversight  
**Return:** 80% less manual work, 3.3x more knowledge, publishable research outputs

**Ready to proceed?** Let me know which option (A/B/C) you prefer, and I'll start implementation.

---

**Files to review:**
1. ⭐ `PHASE3_EXECUTIVE_SUMMARY.md` (start here)
2. 📋 `PHASE3_AUTONOMOUS_RESEARCH_PLAN.md` (detailed spec)
3. 🎨 `AUTONOMOUS_LOOP_DIAGRAM.md` (visual guide)
4. ✏️ `task.md` (updated project tracker)
