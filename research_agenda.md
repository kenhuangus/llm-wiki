# LLM Wiki Research Agenda

**Version:** 1.0  
**Last Updated:** 2026-04-05  
**Owner:** Ken Huang / DistributedApps.ai

---

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
- Sandbox and container escape techniques

**Constraints:**
- Do NOT create speculative attack patterns without evidence
- All patterns must cite ≥2 independent sources (Tier 1 or Tier 2)
- Mark unverified patterns with confidence <0.7

---

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
- Identify zero-day vulnerabilities in agent frameworks

**Constraints:**
- CVSS ≥ 9.0 requires immediate human escalation (write CRITICAL_ALERT.md)
- Do NOT speculate on unpatched vulnerabilities without vendor confirmation
- Always include patch status and mitigation steps

---

### 3. Foundation Model Capability Tracking
**Goal:** Maintain up-to-date comparison of LLM capabilities for agentic tasks  
**Success Criteria:**
- Comparison pages for: GPT-4, Claude 3.5, Gemini 2.0, Llama 4, Qwen 3
- Benchmarks: tool use accuracy, multi-step reasoning, code generation security
- Updated within 7 days of new model release

**Research Directions:**
- Track model releases from OpenAI, Anthropic, Google, Meta, Alibaba
- Compare tool-calling accuracy across models
- Evaluate security properties (prompt injection resistance, jailbreak resilience)
- Document context window limits and token costs

**Constraints:**
- Do NOT rely on vendor marketing claims alone
- Cross-validate benchmarks with independent research
- Mark vendor-reported metrics with confidence 0.6-0.7 until verified

---

## Autonomous Experiment Directives

### Hypothesis Generation Rules
1. **Coverage Gaps:** Identify domains with <50 pages or avg confidence <0.7
2. **Synthesis Opportunities:** Find ≥3 related pages with no comparison page
3. **Outdated Claims:** Flag sources >90 days old in fast-moving domains (LLM benchmarks, CVE patches)
4. **Low Confidence:** Find pages with confidence <0.6 and search for corroborating sources
5. **Orphaned Pages:** Detect pages with no inbound links and create connections

### Experiment Constraints
- **Daily Budget:** Max 10 experiments per day (LLM API cost limit)
- **Success Metric:** Each experiment must have measurable outcome (page count, confidence delta, conflict resolution)
- **Logging:** All experiments logged to `wiki/experiments.md` with hypothesis, action, result, decision
- **Failure Handling:** Max 3 retries per experiment; log failure and move to next

### Quality Thresholds
- **Extraction Confidence Target:** ≥0.75 avg across all domains
- **Integration Conflict Rate Target:** <5% of integrations result in conflicts
- **Lint Pass Rate Target:** ≥95% of pages pass lightweight lint at all times
- **Source Attribution:** 100% of claims must have source citation
- **Cross-linking:** ≥80% of pages have ≥2 inbound links (not orphaned)

---

## Prompt Optimization Directives

### Optimization Goals
1. **Increase Extraction Confidence:** Target +0.10 improvement over baseline (0.72 → 0.82)
2. **Reduce JSON Parsing Errors:** Target <1% of extractions fail JSON validation
3. **Improve CVE Extraction:** Target 95% of CVEs have CVSS score extracted
4. **Reduce False Conflicts:** Target <3% of integrations flag false contradictions

### Optimization Constraints
- **Evaluation Set:** Fixed 50-source test set (never modified during optimization)
- **Git Versioning:** Every prompt change committed with hypothesis description
- **Ratchet Rule:** Only keep changes that improve ≥1 metric without degrading others
- **Rollback:** Auto-revert if new prompt causes >10% increase in errors

### Evaluation Metrics
- **Primary:** avg_confidence (extraction quality)
- **Secondary:** json_valid_rate, cvss_extraction_rate, conflict_false_positive_rate
- **Tertiary:** entity_count, claim_count, relationship_count

---

## Resource Constraints

### LLM Budget
- **Daily Limit:** $10 USD equivalent in API calls
- **Per-Experiment Limit:** $0.50 USD (prevents runaway costs)
- **Fallback Strategy:** Use local LLM (Ken-Mac 26B) as primary, cloud as backup

### Compute Resources
- **GPU:** Ken-Mac (26B model) - primary inference
- **CPU:** Local-PC (8B model) - backup inference
- **Storage:** 500GB allocated for wiki + raw sources
- **Concurrency:** Max 3 parallel LLM calls (prevent GPU OOM)

### Time Constraints
- **Extraction:** Max 5 minutes per source (timeout and retry)
- **Integration:** Max 3 minutes per page (timeout and retry)
- **Prompt Optimization:** Max 2 hours per cycle (50 sources × 2 min each)
- **Daily Maintenance:** Lint + index rebuild = 30 minutes

---

## Human Escalation Triggers

### Critical Escalations (Immediate)
1. **CVSS ≥ 9.0 CVE** affecting target frameworks → Write CRITICAL_ALERT.md
2. **Verified Page Contradiction** (confidence ≥0.9 pages conflict) → Flag for review
3. **System Failure** (>50% of experiments fail in 1 hour) → Pause and alert
4. **Budget Exceeded** (daily LLM cost >$10) → Pause experiments

### Weekly Review Triggers
1. **Unresolved Conflicts** (≥10 pages with status: conflict)
2. **Low Coverage Domains** (any domain <30 pages after 30 days)
3. **Stale Pages** (≥20 pages not updated in 90 days)
4. **Orphaned Pages** (≥15 pages with no inbound links)

### Monthly Audit Triggers
1. **Quality Regression** (avg confidence drops >0.05 from baseline)
2. **Lint Failures** (pass rate <90% for 7 consecutive days)
3. **Experiment Success Rate** (<50% of hypotheses lead to improvement)

---

## Prohibited Actions

### Never Allowed (Hard Constraints)
1. **Do NOT modify `AGENTS.md`** without explicit human approval
2. **Do NOT delete conflicting claims** (move to Historical Claims section)
3. **Do NOT promote Tier 3 sources to verified** without cross-validation
4. **Do NOT run experiments exceeding daily budget**
5. **Do NOT modify raw source files** in `/raw/` (immutable)
6. **Do NOT suppress contradictions** (always flag with [CONFLICT])
7. **Do NOT fabricate sources** (all claims must have real attribution)

### Requires Human Approval
1. Changing active prompt version (V1 → V2)
2. Adding new research priorities to this agenda
3. Modifying quality thresholds (confidence targets, lint pass rates)
4. Deleting wiki pages (even if outdated)
5. Changing source trust tier assignments

---

## Success Metrics (90-Day Targets)

| Metric | Baseline (Phase 2) | Target (Phase 3) | Current |
|--------|-------------------|------------------|---------|
| Wiki pages | 150 | 500+ | TBD |
| Avg extraction confidence | 0.72 | 0.85+ | TBD |
| Integration conflict rate | 12% | <5% | TBD |
| Lint pass rate | 88% | ≥95% | TBD |
| Human interventions/week | 15 | <3 | TBD |
| Novel hypotheses tested | 0 | 50+ | TBD |
| Prompt optimization cycles | 0 | 200+ | TBD |
| Research outputs supported | 0 | 1+ paper/framework | TBD |

---

## Experiment Log Reference

All experiments are logged to `wiki/experiments.md` with this format:

```markdown
### Experiment #NNN: [Hypothesis Title]
- **Hypothesis:** [What we're testing]
- **Change:** [What was modified]
- **Evaluation:** [How we measured success]
- **Results:** [Quantitative outcomes]
- **Decision:** ✓ KEPT or ✗ REVERTED (commit: hash)
```

---

## Version History

### v1.0 (2026-04-05)
- Initial research agenda
- 3 core priorities: threat taxonomy, CVE coverage, model tracking
- Autonomous experiment directives
- Prompt optimization directives
- Resource constraints and escalation triggers

---

**Next Review:** 2026-04-12 (weekly)  
**Owner:** Ken Huang  
**Agent:** Antigravity (Kiro)
