\# PRD: Agentic Local-First LLM Wiki with Continuous Ingestion



\*\*Version:\*\* 2.0  

\*\*Status:\*\* Draft  

\*\*Classification:\*\* Internal — Research Infrastructure  

\*\*Owner:\*\* DistributedApps.ai / Ken Huang



\---



\## Table of Contents



1\. \[Overview](#1-overview)

2\. \[Problem Statement](#2-problem-statement)

3\. \[Goals and Non-Goals](#3-goals-and-non-goals)

4\. \[Core Concept](#4-core-concept)

5\. \[System Architecture](#5-system-architecture)

6\. \[Agent Role and Configuration](#6-agent-role-and-configuration)

7\. \[Continuous Ingestion System](#7-continuous-ingestion-system)

8\. \[Domain Coverage](#8-domain-coverage)

9\. \[Query and Synthesis System](#9-query-and-synthesis-system)

10\. \[Maintenance and Lint System](#10-maintenance-and-lint-system)

11\. \[Indexing, Logging, and Observability](#11-indexing-logging-and-observability)

12\. \[Model Orchestration](#12-model-orchestration)

13\. \[Security, Trust, and Source Integrity](#13-security-trust-and-source-integrity)

14\. \[Event-Driven Triggers](#14-event-driven-triggers)

15\. \[Required Tooling: Obsidian Ecosystem](#15-required-tooling-obsidian-ecosystem)

16\. \[Access and Interface Modes](#16-access-and-interface-modes)

17\. \[Deployment Model](#17-deployment-model)

17\. \[Success Metrics](#17-success-metrics)

18\. \[Risk and Mitigations](#18-risk-and-mitigations)

19\. \[Future Extensions](#19-future-extensions)

20\. \[Open Questions](#20-open-questions)

21\. \[Appendix A: Directory Structure](#appendix-a-directory-structure)

22\. \[Appendix B: AGENTS.md Schema Outline](#appendix-b-agentsmd-schema-outline)

23\. \[Appendix C: Glossary](#appendix-c-glossary)



\---



\## 1. Overview



This document specifies an \*\*agent-maintained, local-first knowledge infrastructure\*\* that continuously ingests, synthesizes, and maintains structured knowledge across:



\- Agentic AI systems and architectures

\- Agentic AI security and threat modeling

\- LLMs and multimodal foundation models

\- Physical AI, humanoid robotics, and embodied intelligence

\- Secure coding practices for AI-driven development

\- CVE intelligence for agentic systems and coding agents



The system replaces fragmented, stateless RAG-based workflows with a \*\*persistent wiki model\*\*: knowledge is incrementally compiled, cross-linked, and maintained over time by one or more coding agents operating under a shared schema.



This PRD is \*\*agent-agnostic and model-agnostic by design\*\*. Antigravity and local OpenAI-compatible models are treated as the reference implementation and primary example — not architectural requirements. Any capable coding agent and any compatible LLM backend may be substituted.



\---



\## 2. Problem Statement



Knowledge workers in AI security and agentic systems research currently face three compounding problems:



\*\*Fragmentation.\*\* Relevant information is scattered across arXiv, CVE feeds, GitHub, documentation, blogs, conference proceedings, and private notes. No unified structure ties these together.



\*\*Statelesness.\*\* RAG pipelines retrieve fragments at query time but do not accumulate understanding. Each query starts from scratch. Relationships between concepts are never made explicit or persistent.



\*\*Velocity mismatch.\*\* The field advances faster than any individual can manually process. CVEs, model releases, and architectural shifts appear weekly. Manual curation cannot keep pace.



This system resolves all three by building a self-maintaining, continuously evolving knowledge base that compounds in value over time.



\---



\## 3. Goals and Non-Goals



\### Goals



\- Build a \*\*persistent, compounding personal and team knowledge base\*\*

\- Enable \*\*continuous automatic ingestion\*\* of relevant technical and security information

\- Maintain \*\*cross-domain synthesis\*\* across AI, security, and robotics subdomains

\- Track and analyze \*\*vulnerabilities in agentic systems and coding agents\*\*

\- Support \*\*long-horizon research, writing, and system design\*\* workflows

\- Operate primarily on \*\*local or self-hosted infrastructure\*\* with controlled resource usage

\- Remain \*\*agent-agnostic and model-agnostic\*\* — portable across implementations



\### Additional Goals



\- Achieve \*\*near-real-time ingestion responsiveness\*\* for high-priority events (CVEs, major releases) — not internet-scale latency, but fast enough that the wiki reflects critical developments within hours, not days

\- \*\*Supersede reliance on external search engines and citation managers\*\* for in-domain queries by making the wiki the authoritative first stop for research and security analysis

\- \*\*Enforce human oversight as a first-class design principle\*\* — trust validation, conflict resolution, and low-confidence claims must surface to a human operator; automation serves human judgment, not the reverse

\- \*\*Function as a domain-specialized reasoning interface\*\*, not a general chatbot — every interaction is grounded in the accumulated wiki and attributed sources

\- \*\*Remain fully portable\*\* — no lock-in to any specific coding agent, model provider, or hosting environment; the system must be reproducible by any team with compatible tooling



\---



\## 4. Core Concept



The system replaces stateless retrieval with \*\*stateful knowledge compilation\*\*.



Traditional RAG:



```

query → search documents → return fragments → discard context

```



This system:



```

source → normalize → extract → integrate into wiki → maintain relationships → query wiki

```



Each source is processed once. Knowledge extracted from it is integrated into structured pages. Relationships between pages are maintained and updated as new information arrives. The wiki is the primary reasoning surface — not the raw documents.



This produces a knowledge base that:



\- \*\*Compounds\*\*: each new source enriches the existing structure rather than existing in isolation

\- \*\*Is queryable at depth\*\*: answers draw on synthesized understanding, not keyword matching

\- \*\*Evolves explicitly\*\*: contradictions, updates, and retractions are tracked, not silently overwritten



\---



\## 5. System Architecture



The system is organized into six layers. Each layer has a defined responsibility and clean interface to adjacent layers.



\### 5.1 Raw Sources Layer



Immutable append-only storage of all input data. Sources include:



\- Research papers (arXiv, ACL, USENIX, IEEE, etc.)

\- Technical blogs, documentation, and conference write-ups

\- CVE/NVD feeds and security advisories

\- GitHub repositories and changelogs

\- Agent execution logs and traces

\- Manually contributed materials



Storage structure:



```

/raw/

&#x20; /auto\_ingest/<source>/<timestamp>.<ext>

&#x20; /manual/<domain>/<filename>.<ext>

&#x20; /agent\_logs/<date>/<session\_id>.log

```



Raw files are never modified after write.



\---



\### 5.2 Normalization Layer



Converts raw inputs into a canonical structured markdown format with consistent metadata headers.



Responsibilities:



\- Format conversion: PDF, HTML, DOCX, Jupyter notebooks → markdown

\- Metadata extraction: title, authors, publication date, source URL, domain tags

\- Content segmentation: abstract, sections, figures, code blocks, references

\- Deduplication fingerprinting



Output:



```

/raw/normalized/<domain>/<content\_hash>.md

```



Metadata header format:



```yaml

\---

id: <content\_hash>

title: <string>

source\_url: <url>

source\_type: paper | blog | cve | repo | doc | log

domain: \[agentic-ai, ai-security, physical-ai, llm, coding-security]

ingested\_at: <ISO 8601>

authors: \[<string>]

confidence: <0.0–1.0>

verified: false

\---

```



\---



\### 5.3 Knowledge Extraction Layer



Uses an LLM (local or remote) to extract structured information from normalized content. Outputs are structured JSON that feeds the wiki integration step.



Extracted types:



| Type | Examples |

|------|----------|

| \*\*Entities\*\* | Models, tools, organizations, CVEs, frameworks |

| \*\*Concepts\*\* | Architectures, attack patterns, design patterns |

| \*\*Relationships\*\* | Depends-on, supersedes, mitigates, exploits |

| \*\*Events\*\* | CVE disclosures, model releases, incidents |

| \*\*Claims\*\* | Empirical results, benchmarks, assertions |



All extracted data is attributed to its source and assigned a confidence score.



\---



\### 5.4 Wiki Layer (Persistent Knowledge Base)



The primary knowledge artifact. A structured, cross-linked, agent-maintained markdown knowledge graph stored on the local filesystem.



\#### Directory Structure



```

/wiki/

&#x20; index.md                      ← Global catalog and entry point

&#x20; log.md                        ← Append-only operation log

&#x20; /concepts/

&#x20;   /agentic-ai/

&#x20;   /ai-security/

&#x20;   /llm-architectures/

&#x20;   /physical-ai/

&#x20;   /secure-coding/

&#x20; /entities/

&#x20;   /models/

&#x20;   /tools/

&#x20;   /frameworks/

&#x20;   /organizations/

&#x20; /security/

&#x20;   /cve/

&#x20;   /threat-models/

&#x20;   /attack-patterns/

&#x20;   /exploits/

&#x20;   /mitigations/

&#x20; /comparisons/

&#x20; /synthesis/

&#x20; /events/

```



\#### Page Properties



Every wiki page:



\- Has a YAML frontmatter block (id, title, domain, last\_updated, sources, confidence)

\- Contains cross-links to related pages using `\[\[page-name]]` syntax

\- Explicitly tracks \*\*contradictions\*\* between sources

\- Records \*\*version history\*\* in its own frontmatter (prior claims, what changed, when)

\- Notes \*\*uncertainty and confidence\*\* per claim section



\---



\### 5.5 Schema and Control Layer



Defines system behavior via a structured control document at the repository root:



```

/AGENTS.md

```



This file is the authoritative specification for any agent operating the system. It includes:



\- Page templates per content type (concept, entity, CVE, comparison, synthesis)

\- Update rules: when to create vs. update, how to handle contradictions

\- Cross-linking requirements and naming conventions

\- Source attribution standards

\- Confidence scoring rubrics

\- Model routing policies (which model class handles which task)

\- Resource usage constraints (max concurrency, GPU budget, batch limits)

\- Trust tier definitions for sources



The AGENTS.md is human-editable and version-controlled. It serves as the single point of behavioral configuration for all agents, regardless of which agent implementation is used.



\---



\### 5.6 Tooling Layer



Provides operational capabilities callable by any agent. All tools are standard CLI utilities or Python scripts. No agent-specific SDK is required.



Core tools:



| Tool | Function |

|------|----------|

| `ingest.py` | Fetch and enqueue new sources |

| `normalize.py` | Convert formats to markdown |

| `extract.py` | Run LLM extraction on normalized content |

| `integrate.py` | Merge extracted knowledge into wiki pages |

| `query.py` | Query the wiki using BM25 or hybrid search |

| `lint.py` | Validate wiki consistency |

| `index.py` | Rebuild index.md |

| `cve\_monitor.py` | Poll CVE/NVD feeds |

| `arxiv\_monitor.py` | Poll arXiv for new papers |

| `github\_monitor.py` | Monitor repos for releases and advisories |



Optional tools:



\- Vector indexing (FAISS, Chroma, or similar) for semantic search

\- CLI REPL for interactive queries



> \*\*Note:\*\* Obsidian and its required plugin stack (Web Clipper, Marp, Dataview, Obsidian Git) are specified in full in §15 and are mandatory, not optional.



\---



\## 6. Agent Role and Configuration



\### 6.1 Reference Implementation: Antigravity



The reference coding agent for this system is \*\*Antigravity\*\*, operated locally. Antigravity is responsible for:



\- Implementing system components according to this PRD

\- Executing ingestion, normalization, extraction, and integration pipelines

\- Maintaining wiki consistency and cross-links

\- Writing and updating markdown files

\- Managing model calls and orchestration

\- Building and maintaining tooling

\- Logging all actions to `log.md` and `/logs/`



This is a reference example. \*\*Any coding agent\*\* (Claude Code, Cursor, Aider, Cline, Continue, or a custom agent harness) that can read the AGENTS.md schema, execute shell commands, and write files may operate this system.



\### 6.2 Agent Execution Loop



```

while True:

&#x20;   read AGENTS.md                     # load current behavioral schema

&#x20;   read wiki/index.md                 # understand current state

&#x20;   select next task from queue        # ingest | extract | integrate | lint | query

&#x20;   execute task using tooling layer

&#x20;   write results to wiki or logs

&#x20;   validate consistency (lightweight)

&#x20;   update log.md

&#x20;   apply any schema updates signaled by human

&#x20;   sleep or await next trigger

```



\### 6.3 Agent Constraints



Agents operating this system must:



\- Never modify raw source files

\- Always attribute knowledge to its source

\- Mark uncertainty explicitly; never fabricate claims

\- Log every write operation to `log.md`

\- Obey resource limits defined in AGENTS.md

\- Pause and surface conflicts to the human operator when confidence is below threshold



\---



\## 7. Continuous Ingestion System



\### 7.1 Objective



Maintain an always-current knowledge base through automatic, background ingestion of new information across all target domains, with human oversight of priority and trust decisions.



\### 7.2 Pipeline Stages



\#### Stage 1: Source Discovery



Continuously monitor configured source endpoints:



| Source | Mechanism | Frequency |

|--------|-----------|-----------|

| arXiv (cs.AI, cs.CR, cs.RO, cs.LG) | API polling | Daily |

| NVD/CVE feeds | RSS/API | Real-time |

| GitHub (target repos) | Webhook or polling | Daily |

| Configured blogs and documentation | RSS/scraper | Daily |

| Agent execution logs | Filesystem watch | Continuous |

| Manual drops to `/raw/manual/` | Filesystem watch | Continuous |



Output goes to `/raw/auto\_ingest/<source>/<timestamp>.md`.



\#### Stage 2: Filtering and Prioritization



Before normalization, each candidate source is evaluated for:



\- \*\*Domain relevance\*\*: does it match a target domain?

\- \*\*Novelty\*\*: is this meaningfully different from existing knowledge?

\- \*\*Impact\*\*: CVEs, major model releases, and security incidents get elevated priority

\- \*\*Source credibility\*\*: tier-rated in AGENTS.md



Each item receives a priority score. Items above a configurable threshold proceed automatically. Items below threshold are queued for human review.



\#### Stage 3: Normalization



Convert to standard markdown with metadata header (see §5.2).



\#### Stage 4: Knowledge Extraction



Run the extraction LLM against normalized content. Output: structured JSON artifact per source.



\#### Stage 5: Wiki Integration



For each extracted knowledge item:



\- Check if a matching page exists

\- If yes: update the page, noting what changed and why, and flagging any contradictions with prior content

\- If no: create a new page from the appropriate template defined in AGENTS.md

\- Update all relevant cross-links

\- Update `index.md`



\#### Stage 6: Post-Integration Validation



After each integration cycle:



\- Check for broken cross-links

\- Detect duplicate pages

\- Flag pages with conflicting claims for human review

\- Check for missing source attribution



\---



\## 8. Domain Coverage



\### 8.1 Agentic AI Systems



Coverage targets:



\- Planning and reasoning architectures (ReAct, Tree-of-Thought, LATS, etc.)

\- Tool use and function-calling implementations

\- Memory architectures: episodic, semantic, procedural, external stores

\- Multi-agent coordination and communication protocols

\- Failure modes: goal drift, tool misuse, context loss, hallucination under long horizon



\### 8.2 AI Security



Coverage targets:



\- Prompt injection: direct, indirect, multi-hop

\- Tool and API misuse

\- Data exfiltration via agent channels

\- Sandbox and container escape

\- Model inversion and extraction attacks

\- Supply chain threats to model weights and fine-tuning datasets

\- Trust boundary violations in multi-agent systems



Reference frameworks: MAESTRO, OWASP LLM Top 10, AIVSS, MITRE ATLAS



\### 8.3 Coding Agent Security (CVE Intelligence)



Each CVE entry in `/wiki/security/cve/` includes:



| Field | Description |

|-------|-------------|

| CVE ID | Official identifier |

| Affected systems | Models, tools, frameworks |

| Attack vector | How the vulnerability is exploited |

| Exploit mechanism | Technical description |

| CVSS / AIVSS score | Severity rating |

| Mitigations | Known patches and workarounds |

| Status | Open, patched, disputed |

| Related CVEs | Cross-links |

| Source attribution | NVD, vendor advisories, research papers |



\### 8.4 Physical AI and Robotics



Coverage targets:



\- Perception system architectures and failure modes

\- Motion planning and control under uncertainty

\- Safety constraints and formal verification approaches

\- Simulation-to-real transfer gaps

\- Embodied AI security: sensor spoofing, adversarial physical inputs



\### 8.5 LLMs and Foundation Models



Coverage targets:



\- Architecture comparisons (transformer variants, MoE, SSMs)

\- Benchmark performance and known evaluation limitations

\- Training data, fine-tuning approaches, alignment methods

\- Capability timelines and emergence patterns

\- Multimodal integration



\### 8.6 Secure Vibe Coding



Coverage targets:



\- Security risk patterns in LLM-generated code

\- Secure-by-default prompt patterns for coding agents

\- Validation strategies: static analysis, fuzzing, formal verification on generated code

\- Guardrail architectures for coding agent deployments

\- Case studies of agent-generated vulnerabilities



\---



\## 9. Query and Synthesis System



\### 9.1 Query Process



Queries operate over the wiki, not over raw sources.



```

receive query

→ read index.md to identify relevant domains and pages

→ retrieve candidate pages (BM25 or hybrid search)

→ optionally retrieve supporting source excerpts from /raw/normalized/

→ synthesize answer using LLM with wiki content as context

→ return answer with citations to wiki pages and original sources

```



\### 9.2 Synthesis Output Types



Query results may be materialized as:



| Output Type | Location | Trigger |

|-------------|----------|---------|

| Inline answer | stdout / UI | Default |

| New wiki page | `/wiki/synthesis/` | Agent decision or user request |

| Comparison page | `/wiki/comparisons/` | Multi-entity query |

| Design pattern | `/wiki/concepts/secure-coding/` | Actionable pattern identified |

| Event summary | `/wiki/events/` | Incident or release |



\### 9.3 Answer Attribution



Every synthesized answer includes:



\- Source wiki pages cited

\- Original sources those pages were derived from

\- Confidence assessment per claim

\- Explicit notes on gaps or uncertainty



\---



\## 10. Maintenance and Lint System



\### 10.1 Lightweight Lint (Daily)



Automated checks:



\- Broken internal cross-links

\- Pages missing required frontmatter fields

\- CVE pages missing status or CVSS score

\- Index entries pointing to non-existent pages



\### 10.2 Deep Lint (Weekly)



LLM-assisted checks:



\- Claim contradictions across pages

\- Outdated claims (sources more than N days old for fast-moving domains)

\- Structural gaps (e.g., attack patterns without mitigations)

\- Orphaned pages with no inbound links

\- Concept coverage gaps relative to AGENTS.md domain definitions



\### 10.3 Contradiction Handling



When a contradiction is detected:



1\. Both claims are preserved with source attribution

2\. A `\[CONFLICT]` tag is added to the affected section

3\. The conflict is logged in `log.md`

4\. A human review task is surfaced

5\. After human resolution, the losing claim is moved to a `## Historical Claims` section rather than deleted



\---



\## 11. Indexing, Logging, and Observability



\### 11.1 index.md



The global catalog and system entry point. Contains:



\- Domain-organized listing of all wiki pages

\- Per-page: title, one-line summary, last updated, confidence tier

\- Total page count and coverage statistics per domain

\- List of pages pending human review



Rebuilt automatically after each integration cycle.



\### 11.2 log.md



Append-only operation log. Format:



```markdown

\## \[2025-09-15T14:23:00Z] ingest | arxiv | "Mixture-of-Experts Security Survey" | id: a1b2c3d4

\## \[2025-09-15T14:25:12Z] integrate | updated /wiki/concepts/ai-security/prompt-injection.md | 3 claims added | 1 conflict flagged

\## \[2025-09-15T18:00:00Z] lint | lightweight | 0 broken links | 2 missing fields → /wiki/security/cve/CVE-2024-XXXX.md

\## \[2025-09-16T02:00:00Z] lint | deep | 1 contradiction flagged → /wiki/concepts/agentic-ai/planning.md

```



\### 11.3 System Logs



```

/logs/

&#x20; ingestion.log       ← Source discovery and fetch events

&#x20; normalization.log   ← Format conversion events

&#x20; extraction.log      ← LLM extraction calls and outputs

&#x20; integration.log     ← Wiki write events

&#x20; errors.log          ← All errors with stack traces

&#x20; model\_usage.log     ← LLM call counts, token usage, latency

```



\---



\## 12. Model Orchestration



\### 12.1 Reference Backend: Local OpenAI-Compatible APIs



The reference implementation uses locally hosted models served via an OpenAI-compatible API (e.g., Ollama, LM Studio, llama.cpp server, vLLM). This is an example configuration — any compatible API endpoint may be used, including hosted APIs.



\### 12.2 Model Routing by Task



| Task | Model Class | Rationale |

|------|-------------|-----------|

| Filtering and tagging | Small (3B–8B) | Low complexity, high frequency |

| Format normalization | Small-Medium (7B–14B) | Structured, rule-following |

| Knowledge extraction | Medium-Large (14B–70B) | Requires accurate entity recognition |

| Synthesis and reasoning | Large (30B–70B+) | Cross-domain reasoning |

| Contradiction detection | Large | Nuanced comparison |

| CVE analysis | Medium + security-tuned preferred | Domain expertise matters |



Model assignments are defined in AGENTS.md and can be overridden per run.



\### 12.3 Resource Management



\- Queue-based processing with configurable concurrency limits

\- GPU-aware scheduling: large model tasks batch during off-peak hours

\- Model load/unload managed by the orchestration layer

\- Token budget limits per task type defined in AGENTS.md

\- Fallback routing: if local resource unavailable, optionally route to remote API



\---



\## 13. Security, Trust, and Source Integrity



\### 13.1 Source Trust Tiers



| Tier | Description | Examples |

|------|-------------|---------|

| Tier 1 | Authoritative primary sources | NVD, vendor security advisories, peer-reviewed papers |

| Tier 2 | High-credibility secondary sources | arXiv preprints, established security blogs, official docs |

| Tier 3 | Community sources | GitHub issues, forum posts, unverified reports |



Tier assignment is configured in AGENTS.md. Knowledge from Tier 3 sources is marked as unverified and requires cross-validation before influencing high-confidence pages.



\### 13.2 Per-Claim Attribution



Every claim in a wiki page includes:



\- Source document ID (linking to `/raw/normalized/`)

\- Source tier

\- Confidence score (0.0–1.0)

\- Verification status: `unverified | cross-validated | human-confirmed`



\### 13.3 CVE-Specific Integrity



For security vulnerability entries:



\- Claims are cross-validated across a minimum of two independent sources before `verified: true`

\- Patch status is re-checked on a defined schedule

\- Disputed CVEs are explicitly marked with the nature of the dispute

\- Uncertainty is surfaced, never suppressed



\### 13.4 Agent Trust Boundary



The system does not allow agents to:



\- Modify raw source files

\- Suppress or delete conflicting claims without human approval

\- Auto-promote Tier 3 claims to high-confidence without validation

\- Make writes to the wiki with no source attribution



\---



\## 14. Event-Driven Triggers



Certain events bypass the standard ingestion queue and trigger immediate processing:



| Event Type | Trigger Condition | Action |

|------------|------------------|--------|

| New CVE | CVSS score ≥ 7.0 affecting a target system | Immediate ingest + extraction + integration |

| Critical CVE | CVSS ≥ 9.0 | Immediate + human alert |

| Major model release | GPT-5, Claude 4, Gemini Ultra, etc. | Prioritized queue |

| Security incident | Public breach or exploit involving agentic system | Immediate ingest |

| Significant research | Paper with >50 citations within 30 days | Elevated priority |

| Manual trigger | Human drops file to `/raw/manual/` | Immediate ingest |



\---



\## 15. Required Tooling: Obsidian Ecosystem



The wiki directory is an \*\*Obsidian vault\*\*. Obsidian is a required component of this system, not an optional interface. The following tools and plugins must be installed and configured as part of the initial deployment.



\---



\### 15.1 Obsidian Web Clipper (Browser Extension) — Required



\*\*Purpose:\*\* Convert web articles directly to markdown and deposit them into `/raw/manual/` in a single browser action. This is the primary human-driven ingestion mechanism for ad-hoc sources.



\*\*Install:\*\* Available for Chrome, Firefox, Safari, and Edge from the Obsidian website or browser extension stores.



\*\*Configuration:\*\*



\- Set the default save location to `/raw/manual/` within your vault

\- Configure the template to include the standard metadata frontmatter header (title, source URL, date clipped, domain tags)

\- Clipped content arrives as clean markdown, ready for the normalization pipeline without manual formatting



\*\*Why required:\*\* Without this, adding sources manually requires copy-paste and reformatting. The Web Clipper makes source capture a one-click action, which is essential for keeping the raw collection current during active research.



\---



\### 15.2 Local Image Download — Required Configuration



\*\*Purpose:\*\* Download all images referenced in a clipped article to local disk, so the LLM can inspect them directly rather than depending on URLs that may break or require network access.



\*\*Setup:\*\*



1\. In Obsidian: \*\*Settings → Files and links → Attachment folder path\*\* — set to `raw/assets/`

2\. In Obsidian: \*\*Settings → Hotkeys\*\* — search for "Download" to find \*\*"Download attachments for current file"\*\* and bind it to a hotkey (recommended: `Ctrl+Shift+D`)

3\. After clipping any article, immediately press the hotkey — all images in that page are downloaded to `raw/assets/` and the markdown links are updated to point to local paths



\*\*Important limitation:\*\* LLMs cannot natively process a markdown file with inline images in a single pass. The working pattern is: (1) agent reads the markdown text first, (2) agent separately views referenced images from `raw/assets/` to gain visual context. This is slightly clunky but reliable and keeps all assets local and permanent.



\*\*Why required:\*\* Remote image URLs break over time. Locally stored images make the raw collection durable and allow the agent to perform complete analysis including visual content.



\---



\### 15.3 Obsidian Graph View — Required



\*\*Purpose:\*\* The graph view is the primary tool for understanding the structural health of the wiki — which pages are well-connected hubs, which are isolated orphans, and where cross-linking is missing.



\*\*Usage:\*\*



\- Open with `Ctrl+G` (or via the left sidebar icon)

\- Filter by tag or folder to inspect specific domains

\- Orphan nodes (pages with no inbound links) are immediate lint targets

\- Dense hub nodes indicate synthesis opportunities or pages that may need splitting

\- Run graph view review as part of the weekly deep lint process



\*\*Configuration:\*\* Enable "Show attachments" and "Show orphans" in graph view settings so the full picture is visible.



\*\*Why required:\*\* No programmatic lint check substitutes for visual inspection of graph topology. Structural problems that are invisible in file listings become immediately obvious in the graph.



\---



\### 15.4 Marp Plugin — Required



\*\*Purpose:\*\* Generate slide decks directly from wiki content using markdown. Enables rapid production of presentations from synthesis pages without reformatting or copy-paste.



\*\*Install:\*\* In Obsidian → Community Plugins → search "Marp" → install \*\*Marp for VS Code\*\* or the Obsidian-native Marp plugin.



\*\*Usage:\*\*



\- Add `marp: true` to any wiki page frontmatter to mark it as a slide deck source

\- Use `---` as slide separators within the markdown

\- Export to PDF, HTML, or PPTX directly from within Obsidian

\- Agent can generate Marp-formatted synthesis pages on request, producing presentation-ready output as a natural byproduct of wiki maintenance



\*\*Why required:\*\* Conference presentations, workshop materials, and client briefings are core outputs of this research infrastructure. Marp eliminates the translation step between wiki knowledge and presentation format.



\---



\### 15.5 Dataview Plugin — Required



\*\*Purpose:\*\* Run structured queries over wiki page frontmatter to generate dynamic tables, dashboards, and filtered views. Enables real-time visibility into wiki coverage, freshness, and verification status without manual reporting.



\*\*Install:\*\* In Obsidian → Community Plugins → search "Dataview" → install and enable.



\*\*Required frontmatter fields for Dataview compatibility\*\* (agent must populate these on every page):



```yaml

\---

id: <content\_hash>

title: <string>

domain: \[agentic-ai, ai-security, llm, physical-ai, secure-coding]

source\_count: <integer>

confidence: <0.0–1.0>

verified: true | false

last\_updated: <YYYY-MM-DD>

status: current | outdated | conflict | review-needed

\---

```



\*\*Example queries (embed directly in wiki pages):\*\*



```dataview

TABLE title, confidence, last\_updated, status

FROM "/wiki/security/cve"

WHERE verified = false

SORT last\_updated ASC

```



```dataview

TABLE title, source\_count, confidence

FROM "/wiki"

WHERE status = "conflict"

```



```dataview

TABLE length(rows) as "Page Count"

FROM "/wiki"

GROUP BY domain

```



\*\*Why required:\*\* Dataview turns the wiki's frontmatter into a live operations dashboard. Coverage gaps, unverified CVEs, and stale pages are surfaced as dynamic tables rather than requiring a separate reporting tool.



\---



\### 15.6 Git Integration — Required



\*\*Purpose:\*\* The wiki is a git repository. Version history, branching, collaboration, and rollback are all provided by git with no additional infrastructure.



\*\*Setup:\*\*



\- Initialize the wiki root as a git repository: `git init`

\- Commit after every significant agent write cycle (configurable in AGENTS.md)

\- Use `.gitignore` to exclude `/logs/\*.log` (too noisy) but include `log.md`

\- For team use: push to a private remote (GitHub, GitLab, Gitea self-hosted)



\*\*Install Obsidian Git plugin:\*\* In Obsidian → Community Plugins → search "Obsidian Git" → install and enable. Configure auto-commit interval (recommended: every 30 minutes during active sessions).



\*\*Branching conventions:\*\*



| Branch | Purpose |

|--------|---------|

| `main` | Stable, human-reviewed wiki state |

| `agent/ingest-<date>` | Agent ingestion work in progress |

| `agent/lint-<date>` | Agent lint and repair cycles |

| `review/<topic>` | Human review of flagged contradictions |



\*\*Why required:\*\* Without git, wiki state is fragile — a bad agent write cycle can corrupt pages with no recovery path. Git provides the rollback safety net that makes autonomous agent writes acceptable.



\---



\### 15.7 Summary: Required Obsidian Stack



| Component | Type | Install Location |

|-----------|------|-----------------|

| Obsidian (core) | Desktop app | obsidian.md |

| Obsidian Web Clipper | Browser extension | Browser extension store |

| Download Attachments | Core Obsidian feature | Settings → Hotkeys |

| Graph View | Core Obsidian feature | Built-in |

| Marp | Community plugin | Obsidian Community Plugins |

| Dataview | Community plugin | Obsidian Community Plugins |

| Obsidian Git | Community plugin | Obsidian Community Plugins |



All components in this stack are free and open source.



\---



\## 16. Access and Interface Modes



The system supports multiple access patterns:



| Mode | Description | Use Case |

|------|-------------|---------|

| \*\*Continuous daemon\*\* | Agent runs as background process, polling and processing | Primary production mode |

| \*\*Scheduled batch\*\* | Cron-triggered ingestion and lint cycles | Resource-constrained environments |

| \*\*Interactive session\*\* | Agent operates in foreground, human in the loop | Research sessions, exploration |

| \*\*CLI query\*\* | `query.py "topic"` returns synthesized answer | Quick lookup |

| \*\*Obsidian vault\*\* | Full Obsidian ecosystem (see §15) | Visual navigation, clipping, presentations, dashboards |

| \*\*MCP tool\*\* | Wiki exposed as MCP server for use by other agents | Agent-to-agent knowledge sharing |



\---



\## 16. Deployment Model



\### 16.1 Reference Configuration



The reference deployment runs entirely locally:



\- \*\*Coding agent\*\*: Antigravity (reference) or any compatible agent

\- \*\*LLM backend\*\*: Local OpenAI-compatible API (Ollama, vLLM, LM Studio, etc.)

\- \*\*Storage\*\*: Local filesystem, git-backed for version history

\- \*\*Search\*\*: BM25 via `rank-bm25` + optional FAISS for semantic search

\- \*\*Interface\*\*: Obsidian vault (required — see §15) + CLI

\- \*\*Scheduling\*\*: cron or agent-native task loop



\### 16.2 Alternative Configurations



| Component | Alternatives |

|-----------|-------------|

| Coding agent | Claude Code, Cursor, Aider, Cline, Continue, custom harness |

| LLM backend | OpenAI API, Anthropic API, Azure OpenAI, Groq, any OpenAI-compatible endpoint |

| Storage | Local FS, S3-backed, shared NFS, Git remote |

| Search | Chroma, Weaviate, Qdrant, Elasticsearch |

| Interface | Obsidian, custom web UI, Notion sync, MCP server |



\### 16.3 System Requirements (Reference)



\- Python 3.11+

\- 16GB+ RAM (32GB recommended for large local models)

\- GPU with 24GB+ VRAM for local large model inference (optional; smaller models run on CPU/smaller GPU)

\- \~500GB storage for a mature knowledge base with raw sources



\---



\## 17. Success Metrics



| Metric | Target |

|--------|--------|

| Wiki pages created | 500+ within 90 days of deployment |

| Domain coverage | All 6 domains represented with ≥50 pages each within 60 days |

| Ingestion latency | CVE-triggered pages integrated within 4 hours of disclosure |

| Query answer quality | Synthesized answers cite ≥2 wiki pages and ≥1 primary source |

| Contradiction resolution | All flagged contradictions resolved within 7 days |

| Lint pass rate | ≥95% pages pass lightweight lint at all times |

| Research output support | System directly supports ≥1 publishable output (paper, framework, chapter) within 6 months |

| Redundant query reduction | ≥50% reduction in repeat raw-source lookups vs. baseline within 90 days |



\---



\## 18. Risk and Mitigations



| Risk | Likelihood | Impact | Mitigation |

|------|-----------|--------|------------|

| LLM hallucination in extraction | Medium | High | Confidence scoring, Tier 3 quarantine, human review triggers |

| Source ingestion at unsustainable rate | Medium | Medium | Priority filtering, configurable rate limits in AGENTS.md |

| Wiki structural drift over time | Medium | Medium | Weekly deep lint, schema enforcement via AGENTS.md |

| CVE data lag or inaccuracy | Low | High | Multi-source cross-validation, explicit uncertainty marking |

| Local model quality insufficient for synthesis | Medium | Medium | Model routing to remote API as fallback; configurable in AGENTS.md |

| Agent loop divergence (runaway writes) | Low | High | Write limits per cycle, human-in-the-loop checkpoints, log monitoring |

| Knowledge base grows too large to query efficiently | Low | Medium | Indexing strategy review at 10K pages; consider sharding by domain |



\---



\## 19. Future Extensions



\*\*Near-term (3–6 months)\*\*



\- MCP server exposing wiki as queryable knowledge tool for other agents

\- Automated draft generation: research summaries, threat model sections, book chapters

\- Integration with reference manager (Zotero, Readwise) for existing library import



\*\*Medium-term (6–12 months)\*\*



\- Multi-agent collaboration: shared team knowledge base with per-agent write namespaces

\- Automated paper outline generation from wiki synthesis pages

\- Advanced graph visualization of entity relationships



\*\*Long-term (12+ months)\*\*



\- Knowledge base federation across organizations (privacy-preserving)

\- Formal knowledge graph integration (RDF/OWL for semantic interoperability)

\- Automated framework contribution: MAESTRO, OWASP LLM Top 10 update drafts



\---



\## 20. Open Questions



\- \*\*Human review UX\*\*: What is the preferred interface for surfacing conflicts and low-confidence pages for human resolution? (CLI prompt, Obsidian comment, email digest?)

\- \*\*Knowledge expiry\*\*: Should claims in fast-moving domains (e.g., LLM benchmarks) have a TTL after which they are automatically flagged for re-validation?

\- \*\*Multi-user support\*\*: If the knowledge base is shared across a team, how are write conflicts and per-contributor trust levels handled?

\- \*\*Privacy\*\*: How are confidential sources (private agent logs, internal documents) handled in attribution and sharing contexts?

\- \*\*Versioning strategy\*\*: Is git sufficient for wiki versioning, or is a more granular per-claim version history needed?



\---



\## Appendix A: Directory Structure



```

/

├── AGENTS.md                       ← Behavioral schema for all agents

├── README.md

├── /raw/

│   ├── /auto\_ingest/               ← Automatically fetched sources

│   │   ├── /arxiv/

│   │   ├── /cve/

│   │   ├── /github/

│   │   └── /rss/

│   ├── /manual/                    ← Human-contributed sources

│   └── /normalized/                ← Converted markdown with metadata

│       ├── /agentic-ai/

│       ├── /ai-security/

│       ├── /llm/

│       ├── /physical-ai/

│       └── /secure-coding/

├── /wiki/

│   ├── index.md

│   ├── log.md

│   ├── /concepts/

│   │   ├── /agentic-ai/

│   │   ├── /ai-security/

│   │   ├── /llm-architectures/

│   │   ├── /physical-ai/

│   │   └── /secure-coding/

│   ├── /entities/

│   │   ├── /models/

│   │   ├── /tools/

│   │   ├── /frameworks/

│   │   └── /organizations/

│   ├── /security/

│   │   ├── /cve/

│   │   ├── /threat-models/

│   │   ├── /attack-patterns/

│   │   ├── /exploits/

│   │   └── /mitigations/

│   ├── /comparisons/

│   ├── /synthesis/

│   └── /events/

├── /tools/

│   ├── ingest.py

│   ├── normalize.py

│   ├── extract.py

│   ├── integrate.py

│   ├── query.py

│   ├── lint.py

│   ├── index.py

│   ├── cve\_monitor.py

│   ├── arxiv\_monitor.py

│   └── github\_monitor.py

└── /logs/

&#x20;   ├── ingestion.log

&#x20;   ├── normalization.log

&#x20;   ├── extraction.log

&#x20;   ├── integration.log

&#x20;   ├── errors.log

&#x20;   └── model\_usage.log

```



\---



\## Appendix B: AGENTS.md Schema Outline



The AGENTS.md file at the repository root is the behavioral specification for all agents. It must include the following sections:



```markdown

\# AGENTS.md — System Behavioral Schema



\## 1. Agent Identity and Role

\[Description of the expected agent capabilities and operating context]



\## 2. Page Templates

\[Templates for: concept, entity/model, entity/tool, cve, comparison, synthesis, event]



\## 3. Update Rules

\[When to create vs. update; how to handle contradictions; merge strategy]



\## 4. Cross-linking Requirements

\[Required links per page type; naming conventions; link validation rules]



\## 5. Source Attribution Standards

\[How to cite sources inline; minimum attribution requirements per claim]



\## 6. Confidence Scoring Rubric

\[How to assign 0.0–1.0 scores; what triggers human review]



\## 7. Source Trust Tiers

\[Tier definitions; tier assignment process; escalation rules]



\## 8. Model Routing Policies

\[Task → model class mapping; fallback rules; token budgets per task]



\## 9. Resource Constraints

\[Max concurrent operations; GPU budget; batch size limits; rate limits]



\## 10. Human Escalation Triggers

\[Conditions under which the agent must pause and surface to human]



\## 11. Prohibited Actions

\[What agents must never do]



\## 12. Logging Requirements

\[What must be logged; format; retention]

```



\---



\## Appendix C: Glossary



| Term | Definition |

|------|-----------|

| \*\*AGENTS.md\*\* | The behavioral schema file that configures agent operation for this system |

| \*\*AIVSS\*\* | AI Vulnerability Scoring System — a scoring framework for AI-specific vulnerabilities |

| \*\*Coding agent\*\* | A software agent capable of reading, writing, and executing code and shell commands |

| \*\*Cross-link\*\* | A wiki internal link connecting related pages |

| \*\*CVE\*\* | Common Vulnerabilities and Exposures — a public catalog of cybersecurity vulnerabilities |

| \*\*Deep lint\*\* | Weekly LLM-assisted consistency check of the wiki |

| \*\*Extraction\*\* | The process of identifying structured knowledge (entities, relationships, claims) from normalized text |

| \*\*Integration\*\* | The process of merging extracted knowledge into existing wiki pages |

| \*\*Knowledge graph\*\* | A network of entities and relationships; in this system, represented as cross-linked markdown pages |

| \*\*MAESTRO\*\* | Multi-Agent Environment Security Threat and Risk Ontology — an AI security framework |

| \*\*MCP\*\* | Model Context Protocol — a standard for connecting AI agents to tools and data sources |

| \*\*Normalization\*\* | Converting raw source formats into canonical structured markdown |

| \*\*OpenAI-compatible API\*\* | Any LLM inference server implementing the OpenAI `/v1/chat/completions` endpoint schema |

| \*\*RAG\*\* | Retrieval-Augmented Generation — a technique for answering questions by retrieving relevant document fragments at query time |

| \*\*Source trust tier\*\* | A classification (1–3) of a source's credibility and authoritativeness |

| \*\*Wiki\*\* | In this system, the persistent structured markdown knowledge base in `/wiki/` |

```



\---



\*This PRD is a living document. Updates should be version-tagged and reviewed against the deployed AGENTS.md to ensure alignment.\*

