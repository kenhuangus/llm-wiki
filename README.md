# 🧠 LLM Wiki — Agentic Local-First Knowledge Infrastructure

> A self-maintaining, continuously evolving knowledge base for Agentic AI, AI Security, LLMs, Physical AI, and Secure Coding — powered by a local LLM and driven by coding agents.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Obsidian](https://img.shields.io/badge/Obsidian-Required-7C3AED)](https://obsidian.md)

---

## What Is This?

LLM Wiki replaces fragmented, stateless RAG workflows with a **stateful knowledge compilation engine**. Instead of searching raw documents at query time, every source is:

1. **Ingested** — fetched from arXiv, CVE feeds, GitHub, or dropped manually
2. **Normalized** — converted to structured Markdown with YAML frontmatter
3. **Extracted** — a local LLM pulls out entities, claims, and relationships as JSON
4. **Integrated** — knowledge is merged into a persistent, cross-linked wiki
5. **Queryable** — the wiki is searched with BM25 semantic ranking

The result is a knowledge base that **compounds over time** — every new source enriches the existing structure rather than existing in isolation.

---

## Architecture

```
source → ingest → normalize → extract (LLM) → integrate (LLM merge) → wiki
                                                                         ↑
                                                               lint · index · query
```

### Directory Layout

```
llm-wiki/
├── AGENTS.md                    ← Behavioral schema for all agents
├── .env                         ← Local secrets & config (never committed)
├── .env.example                 ← Safe template to copy
├── task.md                      ← Agent handover checklist
├── test_e2e.py                  ← End-to-end test runner
│
├── tools/
│   ├── common.py                ← Shared config, logging, LLM client
│   ├── ingest.py                ← Stage 1: fetch & enqueue sources
│   ├── normalize.py             ← Stage 2: convert to standard Markdown
│   ├── extract.py               ← Stage 3: LLM knowledge extraction → JSON
│   ├── integrate.py             ← Stage 4: LLM-assisted wiki merge
│   ├── query.py                 ← BM25 semantic search over the wiki
│   ├── lint.py                  ← Frontmatter validation + LLM deep lint
│   ├── index.py                 ← Rebuild wiki/index.md catalog
│   ├── arxiv_monitor.py         ← Poll arXiv cs.AI / cs.CR feeds
│   ├── cve_monitor.py           ← Poll CVE/NVD feeds
│   └── github_monitor.py        ← Poll GitHub releases
│
├── raw/
│   ├── auto_ingest/             ← Automatically fetched sources
│   │   ├── arxiv/
│   │   ├── cve/
│   │   ├── github/
│   │   └── manual/
│   ├── normalized/              ← Converted Markdown with frontmatter
│   │   ├── agentic-ai/
│   │   ├── ai-security/
│   │   ├── llm/
│   │   ├── physical-ai/
│   │   └── secure-coding/
│   └── assets/                  ← Locally downloaded images
│
├── wiki/
│   ├── index.md                 ← Auto-generated global catalog
│   ├── log.md                   ← Append-only operation log
│   ├── concepts/                ← Domain concept pages
│   │   ├── agentic-ai/
│   │   ├── ai-security/
│   │   ├── llm-architectures/
│   │   ├── physical-ai/
│   │   └── secure-coding/
│   ├── entities/                ← Named entities (models, tools, orgs)
│   │   ├── models/
│   │   ├── tools/
│   │   ├── frameworks/
│   │   └── organizations/
│   ├── security/                ← CVEs, threats, attack patterns
│   │   ├── cve/
│   │   ├── threat-models/
│   │   ├── attack-patterns/
│   │   ├── exploits/
│   │   └── mitigations/
│   ├── comparisons/
│   ├── synthesis/
│   └── events/
│
└── logs/                        ← System logs (gitignored)
```

---

## Requirements

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| [Obsidian](https://obsidian.md) | Latest | Vault interface (required) |
| Local LLM server | Any | Extraction & merge (e.g. LM Studio, Ollama) |
| `pyyaml` | ≥6.0 | YAML frontmatter parsing |
| `python-dotenv` | ≥1.0 | `.env` config loading |
| `rank-bm25` | ≥0.2 | Semantic search |
| `requests` | ≥2.31 | HTTP calls |
| `feedparser` | ≥6.0 | arXiv RSS parsing |

---

## Setup

### 1. Clone the repo

```bash
git clone <your-remote>
cd llm-wiki
```

### 2. Install Python dependencies

```bash
pip install pyyaml python-dotenv rank-bm25 requests feedparser
```

### 3. Configure your environment

```bash
cp .env.example .env
```

Then edit `.env` with your local values:

```dotenv
# Your local LLM server (LM Studio, Ollama, llama.cpp, vLLM, etc.)
LLM_BASE_URL=http://localhost:1234/api/v1/chat
LLM_MODEL=gemma-4-e2b-it
LLM_API_KEY=lm-studio

# How many results to fetch per monitor run
ARXIV_MAX_RESULTS=3
CVE_MAX_RESULTS=3
CVE_FEED_URL=https://cve.circl.lu/api/last

# Optional GitHub token for higher API rate limits
GITHUB_TOKEN=
```

> **Important:** `.env` is gitignored. Never commit it. Use `.env.example` as the committed template.

### 4. Open as an Obsidian vault

Open Obsidian → **"Open folder as vault"** → select this directory.

Required Obsidian plugins (bundled in `.obsidian/`):
- **Dataview** — live frontmatter dashboards
- **Obsidian Git** — auto-commit after write cycles
- **Marp** — export wiki pages as slide decks

---

## Usage

### Run the full pipeline on a file

```bash
# 1. Ingest a source
python tools/ingest.py manual path/to/document.md

# 2. Normalize it (pick domain: agentic-ai | ai-security | llm | physical-ai | secure-coding)
python tools/normalize.py raw/auto_ingest/manual/2026-04-05_document.md ai-security

# 3. Extract entities and claims using your local LLM
python tools/extract.py raw/normalized/ai-security/<hash>.md

# 4. Integrate into the wiki (category: concepts|entities|security; subcategory: e.g. models)
python tools/integrate.py raw/normalized/ai-security/<hash>.md.json concepts ai-security "My Topic"

# 5. Rebuild the index
python tools/index.py

# 6. Query
python tools/query.py "prompt injection"
```

### Run all monitors (fetch fresh sources)

```bash
python tools/arxiv_monitor.py      # Latest cs.AI / cs.CR papers
python tools/cve_monitor.py        # Latest CVEs
python tools/github_monitor.py     # Latest GitHub releases
```

### Lint the wiki

```bash
# Lightweight: check required frontmatter fields
python tools/lint.py

# Deep: LLM-assisted contradiction detection across pages
python tools/lint.py --deep
```

### Run the end-to-end test

```bash
python test_e2e.py
```

---

## Wiki Page Format

Every wiki page uses YAML frontmatter compatible with Obsidian Dataview:

```yaml
---
id: <sha256-hash-8chars>
title: "Page Title"
domain: ai-security
source_count: 2
confidence: 0.85
verified: false
last_updated: 2026-04-05
status: current   # current | outdated | conflict | review-needed
---
```

Conflicts are flagged as `status: conflict` and logged in `wiki/log.md`.

---

## Operation Log

Every action is appended to `wiki/log.md` in the format:

```markdown
## [2026-04-05T15:22:41Z] integrate | merged knowledge | Updated wiki/entities/models/gpt-5-eval.md (Status: conflict)
## [2026-04-05T15:22:41Z] lint | lightweight | Passed with 0 missing fields, 0 broken links
## [2026-04-05T15:22:41Z] index | rebuilt index.md | 2 pages indexed
```

---

## Local LLM Compatibility

The system targets any server serving the following endpoint:

```
POST http://<host>:<port>/api/v1/chat
Content-Type: application/json

{
  "model": "<model-id>",
  "system_prompt": "...",
  "input": "..."
}
```

This matches **LM Studio**'s local server format (the reference implementation). For **Ollama** or **OpenAI-compatible** servers, update `LLM_BASE_URL` in `.env` accordingly and adjust `call_local_model()` in `tools/common.py` to match the endpoint's response schema.

---

## Agent Behavioral Rules

All agents operating this system must obey `AGENTS.md`:

- ❌ Never modify files in `/raw/` once written
- ❌ Never delete conflicting claims without human approval
- ❌ Never auto-promote Tier 3 sources to `verified: true`
- ✅ Always attribute every claim to its source document
- ✅ Always log every write to `wiki/log.md`
- ✅ Surface conflicts with `status: conflict` for human review

---

## Roadmap

See [`task.md`](task.md) for the full prioritized checklist. Key upcoming items:

- [ ] **MCP server** — expose the wiki as a structured tool for other agents
- [ ] **Automated draft generation** — synthesis pages → papers, reports, slide decks
- [ ] **Zotero/Readwise import** — bring in existing library
- [ ] **Multi-agent namespacing** — shared team wiki with per-agent write isolation
- [ ] **RDF/OWL federation** — formal semantic interoperability

---

## License

MIT — see `LICENSE`.

---

*Built on the [llm-wiki.md PRD](llm-wiki.md) by DistributedApps.ai / Ken Huang.*
