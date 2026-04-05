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
  - `arxiv_monitor.py`: Configurable categories, full metadata (authors, abstract, arXiv ID).
  - `cve_monitor.py`: Live CVE feed with configurable URL and result count.
  - `github_monitor.py`: Multi-repo, full release notes, optional auth.
  - `rss_monitor.py`: NEW — polls configurable blog/news feeds.
- [x] **[CONFLICT] Resolution & Deep Lint**: LLM-assisted contradiction scan via `lint.py --deep`.
- [x] **`ingest.py` real implementation**: Actual file copy + URL download (no more stub writes).
- [x] **Professional Web UI Dashboard**: 
  - **Sleek React/Vite Interface**: Modern dashboard using Lucide icons, glassmorphism, and Framer Motion micro-animations.
  - **Interactive Semantic Search**: Full-text semantic search with relevance scoring, mapping results back to the local wiki corpus.
  - **Batch Ingest Controls**: Single-click batch URL ingestion via high-performance FastAPI/Uvicorn backend.
  - **Real-time Status Monitoring**: Active monitoring of backend API and search engine availability.
- [x] **AI Weekly Newsletter Agent**: 
  - Autonomous agent in `tools/newsletter_agent.py` queries wiki pages modified in the last N days.
  - Categorizes sources by type (CVE, arXiv, GitHub, RSS) for structured sections.
  - Generates `wiki/synthesis/newsletters/YYYY-MM-DD_pulse.md` with frontmatter.
  - Supports `--days N` flag. Re-indexes wiki after generation.

## 🟢 Phase 2: Improvement Tasks (Completed)

- [x] **SQLite deduplication state DB** (`state.db`): All monitors now use `is_already_ingested()` / `mark_ingested()` from `common.py` — survives file renames, shared across arXiv, CVE, GitHub, RSS.
- [x] **arXiv keyword relevance pre-filter**: `ARXIV_KEYWORDS` in `.env` — scores title+abstract before saving. Zero-match entries are skipped.
- [x] **arXiv citation count filter**: `ARXIV_MIN_CITATIONS` + `S2_API_KEY` in `.env` — queries Semantic Scholar API before saving.
- [x] **CVE `lastModStartDate` state file** (`state_cve_last_run.txt`): Only fetches CVEs modified since last run.
- [x] **CVE CVSS ≥ 7.0 immediate pipeline trigger**: Runs normalize → extract → integrate → index automatically.
- [x] **CVE CVSS ≥ 9.0 human escalation**: Writes `CRITICAL_ALERT.md` at repo root + `[CRITICAL]` log tag.
- [x] **GitHub ETag/Last-Modified state** (`state_github_etags.json`): Avoids re-fetching unchanged releases (304 Not Modified).
- [x] **GitHub Dependabot alerts polling**: Polls `/repos/{owner}/{repo}/dependabot/alerts` per repo (requires `security_events` token scope).
- [x] **RSS expanded feed list**: Added NIST, CISA, HuggingFace, Papers With Code, The Hacker News to defaults.
- [x] **RSS full article scraping**: Uses `trafilatura` for summary-only feeds (graceful fallback if not installed).
- [x] **RSS relevance scoring pre-filter**: `RSS_KEYWORDS` in `.env` — skips off-topic entries.
- [x] **`index.py` coverage stats**: Now includes per-domain avg confidence, total page count, and "Pending Human Review" section.
- [x] **`lint.py` conflict tag propagation**: Deep lint now writes `[CONFLICT]` tags back to affected pages and sets `status: conflict` in frontmatter.
- [x] **Confidence propagation check**: Lightweight lint warns when unverified pages have confidence > 0.6.

> 📋 **Sub-task detail:** See [task2.md](task2.md) for the full external knowledge source integration checklist, API keys needed, and cron scheduling plan.

## 🟣 Phase 3: Future Enhancements (Roadmap)
- [ ] **Model Context Protocol (MCP)**: Wrap the repository querying operations dynamically exposing the wiki context internally to agents as a registered tool server.
- [ ] **Automated Draft Engine / Publication Bridge**: Bind slide-deck compilation via `marp` explicitly producing reports, papers, or threat design documents cleanly from `/synthesis/`.
- [ ] **Literature Manager Webhook Sync**: Add Zotero/Readbase hooks dynamically ingesting PDF payloads safely. 
- [ ] **Autonomous Team Spaced Namespacing**: Support multiple independent local coding agents safely sharing wiki edits concurrently with Git conflict handling schemas.
- [ ] **Federated Knowledge Sub-repositories**: Integrate RDF/OWL formal topologies expanding the data-lake into organizational interoperability.
