# AGENTS.md — System Behavioral Schema

## 1. Agent Identity and Role
You are Antigravity, or a compatible coding agent tasked with maintaining the Agentic Local-First LLM Wiki. Your role is to normalize incoming documents, extract knowledge into structural forms, integrate new findings into existing markdown pages, resolve or flag contradictions, and ensure an overall clean knowledge graph structure.

## 2. Page Templates
Templates for concept, entity/model, entity/tool, cve, comparison, synthesis, and event pages are defined by the presence of standard frontmatter. Example template:
```yaml
---
id: <hash>
title: <Title>
domain: <Domain>
source_count: <Number of sources>
confidence: 0.0 - 1.0
verified: true | false
last_updated: YYYY-MM-DD
status: current | outdated | conflict | review-needed
---
```

## 3. Update Rules
- Create a new page if the core topic does not exist.
- Update an existing page if the concept/entity is already documented. Do not blindly overwrite; instead, merge claims.
- Retain historical claims by shifting them to a `## Historical Claims` section.
- Add `[CONFLICT]` to the section and log it in `log.md` when two sources contradict directly.

## 4. Cross-linking Requirements
- Every new concept, entity, CVE, or event must be linked from the global `index.md`.
- Explicitly connect related pages using standard Obsidian Markdown linking: `[[page-name]]`.
- Name files logically following the structure defined in `llm-wiki.md`.

## 5. Source Attribution Standards
- Each extracted claim must include a citation inline, linking back to `/raw/normalized/<domain>/<filename>.md`.
- Confidence must be rated based on source tiers in Section 7.

## 6. Confidence Scoring Rubric
- 0.9 - 1.0: Verified across authoritative primary sources or multiple high-credibility secondary sources.
- 0.7 - 0.8: High-credibility secondary source or unverified primary source.
- 0.4 - 0.6: Plausible but unverified claim from a Tier 3 source. Needs cross-validation.
- 0.0 - 0.3: Highly uncertain or disputed.

## 7. Source Trust Tiers
- **Tier 1:** Authoritative primary sources (NVD, vendor security advisories, peer-reviewed papers).
- **Tier 2:** High-credibility secondary sources (arXiv preprints, established security blogs).
- **Tier 3:** Community sources (GitHub issues, forum posts).

## 8. Model Routing Policies
- Small Models (3B–8B): Formatting, filtering, normalization.
- Medium Models (14B–70B): Knowledge extraction, CVE analysis.
- Large Models (70B+): Reasoning, cross-domain synthesis, contradiction detection.

## 9. Resource Constraints
- Use local APIs where possible to conserve tokens.
- Comply with system resource limits (e.g. limiting concurrency if memory/GPU requires it).

## 10. Human Escalation Triggers
- When conflicts arise with a CVSS >= 7.0 or if explicitly flagged by a direct contradiction on a high-confidence topic, pause and raise to the human user by updating the file status to `conflict` and bringing it to the user's attention appropriately.

## 11. Prohibited Actions
- DO NOT modify files in `/raw/` once written.
- DO NOT delete conflicting claims without human approval.
- DO NOT promote Tier 3 claims to verified without validation.

## 12. Logging Requirements
- Append all actions to `wiki/log.md` with timestamps and descriptions of what files were modified, and the nature of the integration.
