# Autonomous Research Loop Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HUMAN OPERATOR                              │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │ research_agenda  │         │   AGENTS.md      │                 │
│  │ .md              │         │ (quality rules)  │                 │
│  │ (priorities)     │         │                  │                 │
│  └────────┬─────────┘         └────────┬─────────┘                 │
│           │ reads                      │ enforces                  │
└───────────┼────────────────────────────┼───────────────────────────┘
            │                            │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS DAEMON LAYER                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    WikiDaemon (24/7)                         │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │  │
│  │  │  Monitor   │  │  Priority  │  │  Process   │            │  │
│  │  │  Sources   │─▶│   Queue    │─▶│  Pipeline  │            │  │
│  │  └────────────┘  └────────────┘  └────────────┘            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PROCESSING PIPELINE                              │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│  │ Ingest   │──▶│Normalize │──▶│ Extract  │──▶│Integrate │       │
│  │          │   │          │   │  (LLM)   │   │  (LLM)   │       │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘       │
│                                      │              │              │
│                                      ▼              ▼              │
│                              ┌────────────────────────┐            │
│                              │   prompts.py           │            │
│                              │ (agent-modifiable)     │            │
│                              └────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE (WIKI)                            │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│  │ Concepts │   │ Entities │   │ Security │   │Synthesis │       │
│  │          │   │          │   │   (CVE)  │   │          │       │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘       │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    META-LEARNING LAYER                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              PromptOptimizer (Ratchet Loop)                  │  │
│  │                                                              │  │
│  │  1. Analyze recent quality metrics                          │  │
│  │  2. Propose prompt modification                             │  │
│  │  3. Commit change to git                                    │  │
│  │  4. Evaluate on test set (50 sources)                       │  │
│  │  5. Keep if improved, revert if not                         │  │
│  │  6. Repeat                                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              ResearchAgent (Hypothesis Generation)           │  │
│  │                                                              │  │
│  │  1. Identify knowledge gaps (coverage, confidence)           │  │
│  │  2. Generate hypotheses (search, synthesis, validation)      │  │
│  │  3. Execute experiments                                      │  │
│  │  4. Log results to experiments.md                           │  │
│  │  5. Update wiki based on findings                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         RetrospectiveValidator (Quality Feedback)            │  │
│  │                                                              │  │
│  │  1. Check old claims against new sources                     │  │
│  │  2. Detect contradictions                                    │  │
│  │  3. Adjust confidence scores                                 │  │
│  │  4. Flag for human review if critical                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    METRICS & LOGGING                                │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │   metrics.db     │         │ experiments.md   │                 │
│  │ (time series)    │         │ (audit trail)    │                 │
│  └──────────────────┘         └──────────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Ratchet Loop Detail (Autoresearch Pattern)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROMPT OPTIMIZATION CYCLE                        │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │  Current State: prompts.py @ commit abc123               │
    │  Baseline: avg_confidence = 0.72, conflict_rate = 12%    │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  1. ANALYZE: Review recent failures                      │
    │     - 15 CVEs missing CVSS scores                        │
    │     - 8 papers with low entity extraction                │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  2. HYPOTHESIZE: Propose modification                    │
    │     "Add explicit CVSS parsing instruction to prompt"    │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  3. MODIFY: Update prompts.py                            │
    │     + "Extract CVSS score from CVE description"          │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  4. COMMIT: git commit -m "Exp #042: CVSS parsing"       │
    │     New commit: def456                                   │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  5. EVALUATE: Run on test set (50 sources)               │
    │     - Extract all 50 sources with new prompt             │
    │     - Measure: avg_confidence, conflict_rate, etc.       │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  6. COMPARE: New vs Baseline                             │
    │     New: avg_confidence = 0.78, conflict_rate = 10%      │
    │     Δ: +0.06 confidence, -2% conflicts                   │
    └────────────────────┬─────────────────────────────────────┘
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
    ┌─────────────────┐   ┌─────────────────┐
    │  IMPROVED?      │   │  NO IMPROVEMENT │
    │  ✓ YES          │   │  ✗ REVERT       │
    └────────┬────────┘   └────────┬────────┘
             │                     │
             ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐
    │  KEEP COMMIT    │   │ git reset HEAD~1│
    │  Update baseline│   │ Try new idea    │
    └────────┬────────┘   └────────┬────────┘
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
    ┌──────────────────────────────────────────────────────────┐
    │  7. LOG: Record to experiments.md                        │
    │     - Hypothesis, change, results, decision              │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  8. REPEAT: Generate next hypothesis                     │
    │     (Loop runs continuously, 24/7)                       │
    └──────────────────────────────────────────────────────────┘
```

---

## Research Agent Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DAILY HYPOTHESIS GENERATION                      │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │  Read research_agenda.md                                 │
    │  - Priority 1: Agentic AI Security Threat Taxonomy       │
    │  - Priority 2: CVE Coverage for Coding Agents            │
    │  - Priority 3: Foundation Model Capability Tracking      │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Analyze wiki state                                      │
    │  - Domain: ai-security has 42 pages (target: 50+)        │
    │  - Domain: llm has avg confidence 0.68 (target: 0.75+)   │
    │  - 8 pages with status: conflict (need resolution)       │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Generate hypotheses                                     │
    │                                                          │
    │  H1: Coverage gap in ai-security                         │
    │      → Search arXiv for "prompt injection" papers        │
    │                                                          │
    │  H2: Low confidence in llm domain                        │
    │      → Search for additional sources on GPT-4 benchmarks │
    │                                                          │
    │  H3: Synthesis opportunity                               │
    │      → Create comparison page for Claude vs GPT-4        │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Execute experiments (one per day, respecting budget)    │
    │                                                          │
    │  Day 1: Execute H1                                       │
    │    - Search arXiv: found 12 papers                       │
    │    - Ingest 8 (4 duplicates)                             │
    │    - Result: +3 new attack pattern pages                 │
    │    - Success: coverage now 45 pages (closer to target)   │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Log to experiments.md                                   │
    │  - Hypothesis, action, results, decision                 │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Update wiki state                                       │
    │  - Rebuild index.md                                      │
    │  - Update coverage stats                                 │
    └──────────────────────────────────────────────────────────┘
```

---

## Quality Feedback Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WEEKLY RETROSPECTIVE VALIDATION                  │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │  Find pages updated in last 7 days                       │
    │  - 23 pages modified                                     │
    │  - 47 new sources integrated                             │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  For each page: check old claims vs new sources          │
    │                                                          │
    │  Page: /wiki/security/cve/CVE-2024-1234.md              │
    │    Old claim (30 days ago):                              │
    │      "Affects LangChain 0.1.0-0.1.5"                     │
    │    New source (today):                                   │
    │      "Patch released in 0.1.3, backported to 0.1.2"      │
    │                                                          │
    │  → CONTRADICTION DETECTED                                │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Update page                                             │
    │  - Add [CONFLICT] tag                                    │
    │  - Decrease confidence: 0.85 → 0.75                      │
    │  - Flag for human review                                 │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Find reinforced claims                                  │
    │                                                          │
    │  Page: /wiki/concepts/agentic-ai/react.md                │
    │    Claim: "ReAct improves reasoning by 15%"              │
    │    Supporting sources: 4 (was 2)                         │
    │                                                          │
    │  → CONFIDENCE INCREASE                                   │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Update page                                             │
    │  - Increase confidence: 0.75 → 0.85                      │
    │  - Mark verified if confidence ≥ 0.9                     │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │  Generate weekly report                                  │
    │  - 3 contradictions detected                             │
    │  - 12 claims reinforced                                  │
    │  - 5 claims promoted to verified                         │
    └──────────────────────────────────────────────────────────┘
```

---

## Data Flow Summary

```
External Sources (arXiv, CVE, GitHub, RSS)
    │
    ▼
[Monitor Layer] ──▶ Priority Queue
    │
    ▼
[Processing Pipeline] ──▶ Wiki Pages
    │                        │
    ▼                        ▼
[Metrics Collection] ◀── [Quality Feedback]
    │                        │
    ▼                        ▼
[Meta-Learning] ──▶ Prompt Optimization
    │
    ▼
[Research Agent] ──▶ Hypothesis Generation
    │
    ▼
[Experiment Log] ──▶ Human Review (weekly)
```

---

## Key Differences from Traditional Systems

| Traditional RAG | Phase 2 (Current) | Phase 3 (Autonomous) |
|-----------------|-------------------|----------------------|
| Stateless retrieval | Persistent wiki | Self-improving wiki |
| No learning | Manual prompt tuning | Automatic prompt optimization |
| Reactive only | Scheduled ingestion | Proactive research |
| No quality tracking | Confidence scores | Retrospective validation |
| Human-driven | Human-supervised | Human-advised |

---

## Autonomy Levels

```
Level 0: Manual Operation
  └─ Human runs each tool manually

Level 1: Scheduled Automation (Phase 2)
  └─ Cron jobs run monitors, human reviews results

Level 2: Supervised Autonomy (Phase 3 Week 1-2)
  └─ Daemon runs continuously, human reviews daily

Level 3: Autonomous Operation (Phase 3 Week 3-4)
  └─ System optimizes itself, human reviews weekly

Level 4: Research Autonomy (Phase 3 Week 5-6)
  └─ System generates hypotheses, human sets agenda

Level 5: Full Autonomy (Future)
  └─ System sets own research agenda, human audits outcomes
```

Current target: **Level 4** (Research Autonomy)

---

**Next:** Begin Week 1 implementation — externalize prompts, create research agenda, set up metrics DB.
