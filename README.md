# Agentic Local-First LLM Wiki

A persistent, agent-maintained, continuous-ingestion knowledge base focused on Agentic AI, AI Security, and related domains.

## Introduction

This repository serves as a stateful knowledge compilation engine. It operates autonomously to fetch, normalize, extract, and integrate intelligence from sources such as arXiv, NVD/CVE, and GitHub, maintaining a local structure of interconnected facts.

## Tooling

All tools are in the `tools/` directory and can be used directly or wrapped in cron/scripts:

- `python tools/ingest.py <source> <file>` - Ingests a new file
- `python tools/normalize.py <file> <domain>` - Converts raw files to standard Markdown schema
- `python tools/extract.py <file>` - Calls LLM to extract JSON intelligence
- `python tools/integrate.py <json_path> <category> <subcategory> <title>` - Ingests JSON intelligence into Wiki pages
- `python tools/query.py <term>` - Searches the wiki
- `python tools/lint.py` - Validates frontmatter and structure
- `python tools/index.py` - Rebuilds `wiki/index.md`

## Dependencies
Ensure you have the required Python modules. The primary requirement is `PyYAML`.
Install via `pip install pyyaml`

## Setup
1. Use Obsidian to open this repository folder.
2. Install the necessary Obsidian plugins as outlined in `llm-wiki.md`.
3. Set scheduled jobs to run the `_monitor.py` scripts.
