# LLM Wiki - Task Handover & Completion Record

This document records the exact state of the Agentic Local-First LLM Wiki project, matching the rules designated in `llm-wiki.md`. Coding agents can use this state checklist to resume execution or expand logic smoothly.

## 🟢 Phase 1: Completed Initialization (What has been done)
- [x] **Generate Directory Skeleton**: Bootstrapped `/raw`, `/wiki` and `/tools` mirroring the correct sub-domain structures (`auto_ingest`, `concepts`, `entities` etc.).
- [x] **System Behavioral Schema (`AGENTS.md`)**: Replicated rule configurations detailing confidence rubrics, cross-linking rules, trust tiers, and the logging contract.
- [x] **Git Repository Bootstrap**: Created `.gitignore` (excludes `/logs/*.log` and `.env`) and made initial commit tagging full Phase 1+2 milestone.
- [x] **`.env` Configuration**: All secrets and endpoints (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`, `GITHUB_TOKEN`, CVE/arXiv settings) moved to `.env` loaded via `python-dotenv`. `.env.example` committed as safe template.
- [x] **Obsidian Ecosystem Vault Configurations**: Safely bootstrapped the `.obsidian/` application settings:
  - Added constraints to pull all attachments strictly to `raw/assets/`.
  - Registered and downloaded core `community-plugins.json` targets (`dataview`, `marp`, and `obsidian-git`).
- [x] **Python Structural Handlers**: Built the base CLI orchestration utilities tracking cleanly back to `wiki/log.md` with explicit UTC ISO 8601 timestamps:
  - `tools/common.py`: Universal library for YAML/Markdown frontmatter, logging, and `call_local_model()` using `.env` config.
  - `tools/lint.py`: Lightweight (field check) and deep (LLM-assisted contradiction detection via `--deep` flag).
  - `tools/index.py`: Parses the repository and compiles `wiki/index.md` catalogs safely.
- [x] **Pipeline Executables (Live)**: `ingest.py`, `normalize.py`, `extract.py` (LLM), `integrate.py` (LLM merge+conflict), `query.py` (BM25).
- [x] **E2E Validation Test Runner**: Drafted and validated `test_e2e.py` — fully passes end-to-end.

## 🟡 Phase 2: Core System Expansion (What needs to be done)
- [x] **LLM Orchestration Layer Integration**: Upgrade `extract.py` & `integrate.py` from their static json mocks to invoke real local LLM APIs via `subprocess` (e.g. `llama.cpp` / `ollama`) or litellm.
  - LLM prompt generation needed to map extracted entity targets into the defined templates securely. 
- [x] **Deep Semantics in Queries**: Convert `query.py` from string-comparison to a localized vector database/BM25 (using `rank-bm25` or `chromadb`) resolving semantic hits.
- [x] **Monitor APIs implementation (`*_monitor.py`)**: 
  - `arxiv_monitor.py`: Call real `cs.AI`, `cs.CR` feed APIs and push newly discovered papers down the `ingest.py` boundary.
  - `cve_monitor.py`: Map raw NVD endpoints to pull down CVSS 7.0+ entries safely tracking into `security/cve/`.
  - `github_monitor.py`: Consume git webhooks or release trackers.
- [x] **[CONFLICT] Resolution & Deep Lint**: Build the "Weekly Deep Lint" pipeline (`lint.py`) designed to prompt LLMs for factual contradiction sweeps mapping claims across `/comparisons/`. 

## 🟣 Phase 3: Future Enhancements (Roadmap)
- [ ] **Model Context Protocol (MCP)**: Wrap the repository querying operations dynamically exposing the wiki context internally to agents as a registered tool server.
- [ ] **Automated Draft Engine / Publication Bridge**: Bind slide-deck compilation via `marp` explicitly producing reports, papers, or threat design documents cleanly from `/synthesis/`.
- [ ] **Literature Manager Webhook Sync**: Add Zotero/Readbase hooks dynamically ingesting PDF payloads safely. 
- [ ] **Autonomous Team Spaced Namespacing**: Support multiple independent local coding agents safely sharing wiki edits concurrently with Git conflict handling schemas.
- [ ] **Federated Knowledge Sub-repositories**: Integrate RDF/OWL formal topologies expanding the data-lake into organizational interoperability.
