# task2.md — External Knowledge Source Integration & Cron Scheduling

Sub-task list linked from [task.md](task.md). This covers every external knowledge source integration and the cron scheduling layer needed for continuous ingestion.

---

## 🔑 API Keys & Credentials Needed

Before implementing, obtain the following. Instructions are included:

| Credential | How to Get | Where to Put |
|---|---|---|
| **GitHub Token** | [github.com/settings/tokens](https://github.com/settings/tokens) → New token (classic) → No scopes needed for public repos | `.env` → `GITHUB_TOKEN` |
| **NVD API Key** | [nvd.nist.gov/developers/request-an-api-key](https://nvd.nist.gov/developers/request-an-api-key) → Free, instant email delivery | `.env` → `NVD_API_KEY` |
| **Semantic Scholar API Key** | [api.semanticscholar.org](https://api.semanticscholar.org/api-docs/) → Free tier, no key required for basic; register for higher limits | `.env` → `S2_API_KEY` |

---

## 📡 Source 1: arXiv

- [x] **Basic feed polling** (`arxiv_monitor.py`) — implemented via Atom API
- [x] **Configurable categories** (`ARXIV_CATEGORIES` in `.env`) — cs.AI, cs.CR, cs.RO, cs.LG
- [x] **Full metadata capture** — title, authors, abstract, arxiv ID, categories, published date
- [x] **Deduplication by arXiv ID** — currently uses filename; should index ingested IDs in a sqlite state DB to survive file renames
- [x] **Full-text PDF download** — fetch `https://arxiv.org/pdf/<id>` and convert via `pypdf` for richer extraction
- [ ] **Citation count filter** — use Semantic Scholar API to skip papers with < N citations (configurable threshold)
- [ ] **Keyword relevance pre-filter** — score title+abstract against a configurable keyword list before saving (avoid noise)

**Cron:** Daily at 07:00
```
0 7 * * * cd /path/to/llm-wiki && python tools/arxiv_monitor.py >> logs/ingestion.log 2>&1
```

---

## 🔒 Source 2: CVE / NVD

- [x] **Basic CVE polling** (`cve_monitor.py`) — using CIRCL `cve.circl.lu` fallback endpoint
- [x] **Configurable feed URL and result count** via `.env`
- [ ] **Switch to official NVD API** (`services.nvd.nist.gov/rest/json/cves/2.0`) — requires `NVD_API_KEY`
  - Filter by `cvssV3Severity=HIGH,CRITICAL` and keyword filter for AI/agent-related products
  - Store `lastModStartDate` in a state file to only fetch new/modified CVEs per run
- [ ] **CVSS ≥ 7.0 alert trigger** — when ingested CVE has CVSS ≥ 7.0, immediately run normalize + extract + integrate pipeline and set `status: review-needed` in wiki page
- [ ] **CVSS ≥ 9.0 human escalation** — write a `CRITICAL_ALERT.md` at repo root and log to `wiki/log.md` with `[CRITICAL]` tag
- [ ] **Patch status re-check** — weekly job re-fetches existing CVE pages to update patch status

**Cron:** Every 4 hours (real-time priority source)
```
0 */4 * * * cd /path/to/llm-wiki && python tools/cve_monitor.py >> logs/ingestion.log 2>&1
```

**API key needed:** `NVD_API_KEY` — get free at https://nvd.nist.gov/developers/request-an-api-key

---

## 🐙 Source 3: GitHub Releases & Security Advisories

- [x] **Multi-repo release polling** (`github_monitor.py`) — configurable via `GITHUB_REPOS` in `.env`
- [x] **Full release notes capture**
- [x] **Auth header support** via `GITHUB_TOKEN`
- [x] **GitHub Security Advisories** — additionally poll `GET /repos/{owner}/{repo}/security-advisories` for each watched repo
- [ ] **Dependabot alerts** — poll `GET /repos/{owner}/{repo}/dependabot/alerts` for supply chain issues
- [ ] **State file for `etag` / `Last-Modified` headers** — avoid re-fetching unchanged releases

**Cron:** Daily at 08:00
```
0 8 * * * cd /path/to/llm-wiki && python tools/github_monitor.py >> logs/ingestion.log 2>&1
```

**API key needed:** `GITHUB_TOKEN` — https://github.com/settings/tokens (no scopes for public repos)

---

## 📰 Source 4: RSS / Blog Feeds

- [x] **RSS monitor created** (`rss_monitor.py`) — polls configurable feed list
- [x] **Default feed list** — Trail of Bits, OpenAI blog, Anthropic, DeepMind, Google Research
- [x] **Per-entry deduplication** by `entry.id`
- [ ] **Expand default feed list** — add: NIST, CISA, MITRE ATT&CK blog, HuggingFace blog, Papers With Code
- [ ] **Full article scraping** — for feeds that only provide summaries, use `newspaper3k` or `trafilatura` to fetch full article body
- [ ] **Relevance scoring** — only save items whose title/summary score above a keyword relevance threshold

**Cron:** Daily at 09:00
```
0 9 * * * cd /path/to/llm-wiki && python tools/rss_monitor.py >> logs/ingestion.log 2>&1
```

---

## 📄 Source 5: Manual Drop (Obsidian Web Clipper)

- [x] **Directory exists** (`raw/manual/`) — Obsidian Web Clipper deposits here
- [x] **Filesystem watch via `ingest.py`** — manually triggered CLI call
- [ ] **Watchdog daemon** — use `watchdog` Python library to auto-trigger `normalize.py` whenever a new file appears in `raw/manual/`
- [ ] **Obsidian Web Clipper template** — configure clipper to auto-populate frontmatter: `title`, `source_url`, `date_clipped`, `domain`

---

## ⚙️ Source 6: NVD API (Upgrade from CIRCL)

- [x] **Implement `nvd_monitor.py`** (merged into `cve_monitor.py`) as a dedicated, full-featured NVD client:
  - Endpoint: `https://services.nvd.nist.gov/rest/json/cves/2.0`
  - Params: `resultsPerPage`, `pubStartDate`, `cvssV3Severity` natively filtering `HIGH`
  - Auth: Optional checking for `NVD_API_KEY` dynamically.
- [x] Add `NVD_API_KEY` to `.env`

**API key needed:** `NVD_API_KEY` — same as CVE source above

---

## 📚 Source 7: Curated Weekly Sources

- [x] **Tracking file created** (`wiki/synthesis/curated-sources.md`) — initialized with the 10 core targets (MCP Auth, AgenticSeek, AIVSS, etc.)
- [x] **Implement `curated_monitor.py`** — utilizes `duckduckgo-search` bridging into the LLM intelligence engine to scrape weekly framework updates context.
- [x] **Registered in Task Scheduler** — appended to the weekly cron logic

**Cron:** Weekly on Monday at 06:00
```
0 6 * * 1 cd /path/to/llm-wiki && python tools/curated_monitor.py >> logs/ingestion.log 2>&1
```

---

## 🕐 Cron Scheduling Master Plan

Create a single `cron_setup.sh` script the user can run once to register all jobs:

- [x] **Create `tools/run_all_monitors.py`** — single entry point that runs all monitors sequentially with error isolation
- [ ] **Create `cron_setup.sh`** — registers all cron jobs via `crontab -e`
- [x] **Windows Task Scheduler alternative** — create `tasks/schedule_monitors.ps1` for Windows users

### Full Cron Table

```cron
# LLM Wiki — Continuous Ingestion Cron Jobs
# Edit with: crontab -e

# arXiv — daily at 07:00
0 7 * * * cd /path/to/llm-wiki && python tools/arxiv_monitor.py >> logs/ingestion.log 2>&1

# CVE/NVD — every 4 hours
0 */4 * * * cd /path/to/llm-wiki && python tools/cve_monitor.py >> logs/ingestion.log 2>&1

# GitHub releases — daily at 08:00
0 8 * * * cd /path/to/llm-wiki && python tools/github_monitor.py >> logs/ingestion.log 2>&1

# RSS blogs — daily at 09:00
0 9 * * * cd /path/to/llm-wiki && python tools/rss_monitor.py >> logs/ingestion.log 2>&1

# Lightweight lint — daily at 23:00
0 23 * * * cd /path/to/llm-wiki && python tools/lint.py >> logs/ingestion.log 2>&1

# Deep lint (LLM contradiction scan) — weekly Sunday 02:00
0 2 * * 0 cd /path/to/llm-wiki && python tools/lint.py --deep >> logs/ingestion.log 2>&1

# Curated sources (MCP, Security Frameworks) — weekly Monday 06:00
0 6 * * 1 cd /path/to/llm-wiki && python tools/curated_monitor.py >> logs/ingestion.log 2>&1

# Re-index wiki — daily at 23:30
30 23 * * * cd /path/to/llm-wiki && python tools/index.py >> logs/ingestion.log 2>&1

# Git auto-commit — every 30 minutes
*/30 * * * * cd /path/to/llm-wiki && git add -A && git commit -m "auto: wiki update $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> logs/ingestion.log 2>&1
```

---

## 📋 Priority Order for Next Agent

1. ✅ `ingest.py` — real file copy + URL download (done)
2. ✅ `github_monitor.py` — multi-repo, full release body (done)
3. ✅ `arxiv_monitor.py` — configurable categories, full metadata (done)
4. ✅ `rss_monitor.py` — created with defaults (done)
5. ✅ Curated sources tracker added to `wiki/` (done)
6. ✅ `cve_monitor.py` — upgraded from CIRCL to official NVD API natively (done)
7. ✅ `tools/run_all_monitors.py` — single entry point (done)
8. ✅ `tasks/schedule_monitors.ps1` — Windows Task Scheduler hookups (done)
9. ✅ `curated_monitor.py` — implement LLM-guided web check for the curated MCP/Security frameworks (done)
10. ✅ `watchdog_monitor.py` — setup background service script mapped to Powershell rules (`start_watchdog.ps1`) (done)
11. ✅ arXiv PDF download + text extraction (done)
12. ✅ GitHub Security Advisories polling (done)
13. ⬜ **AI Weekly Newsletter Agent**: Implement autonomous synthesis in `tools/newsletter_agent.py` to create `wiki/synthesis/newsletters/` weekly pulse reports. (planned)

---

## 🕐 Cron Scheduling Master Plan
