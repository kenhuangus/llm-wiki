# Quick Start Guide - LLM Wiki Autonomous System

**Ready to deploy in 5 minutes!**

---

## Prerequisites

✅ Python 3.11+  
✅ Git  
✅ Local LLM server (Ken-Mac) OR OpenRouter API key  
✅ ~500GB storage  

---

## Step 1: Configuration (2 minutes)

### Check .env file
```bash
cat .env
```

**Required settings:**
```bash
# Local LLM (primary)
LLM_MAIN_URL=http://ken-mac.local:1234/v1/chat/completions
LLM_MAIN_MODEL=google/gemma-4-26b-a4b:3

# OpenRouter (fallback for context size issues)
OPENROUTER_API_KEY=sk-or-v1-...  # Your key here
```

**Optional but recommended:**
```bash
# GitHub monitoring
GITHUB_TOKEN=ghp_...  # For release monitoring

# NVD CVE feed
NVD_API_KEY=...  # For faster CVE updates
```

---

## Step 2: Test Components (2 minutes)

### Test LLM connection
```bash
python -c "import sys; sys.path.insert(0, 'tools'); from common import call_local_model; result = call_local_model('You are helpful', 'Say hello'); print('✓ LLM working!' if result else '✗ LLM failed')"
```

### Test metrics database
```bash
python tools/metrics_collector.py
```

### Test research agent
```bash
python tools/test_research_agent.py
```

---

## Step 3: Start the System (1 minute)

### Option A: Unified Daemon (Recommended)
**Runs everything: processing + optimization + research + validation**

```bash
python tools/unified_daemon.py
```

**Schedule:**
- Continuous: Source processing
- Every 4h: Prompt optimization
- Every 6h: Research hypotheses
- Every 7d: Retrospective validation

**Stop:** Press `Ctrl+C` (graceful shutdown)

---

### Option B: Individual Components

**Just process sources:**
```bash
python tools/daemon.py
```

**Just optimize prompts (10 cycles):**
```bash
python tools/prompt_optimizer.py --cycles 10
```

**Just generate hypotheses:**
```bash
python tools/research_agent.py --hypotheses 5 --execute 2
```

**Just validate quality:**
```bash
python tools/retrospective_validator.py --days 7
```

---

## Step 4: Monitor (Ongoing)

### Check logs
```bash
# Wiki operation log
cat wiki/log.md

# Experiment log
cat wiki/experiments.md

# Validation report
cat wiki/validation_report.md
```

### Check metrics
```bash
python -c "import sys; sys.path.insert(0, 'tools'); from metrics_collector import MetricsCollector; m = MetricsCollector(); print(f'Experiments: {m.get_experiment_count()}'); print(f'Hypotheses: {m.get_hypothesis_count()}'); m.close()"
```

### Check wiki growth
```bash
python tools/index.py
cat wiki/index.md
```

---

## Troubleshooting

### LLM fails with "Context size exceeded"
✅ **Expected behavior** - System automatically falls back to OpenRouter  
✅ Make sure `OPENROUTER_API_KEY` is set in `.env`

### Daemon stops processing
1. Check queue: `python tools/test_daemon.py`
2. Check monitors: Run individual monitors manually
3. Check logs: `cat wiki/log.md | tail -20`

### Prompt optimizer reverts all changes
✅ **Normal** - System is conservative, only keeps clear improvements  
✅ Run more cycles: `--cycles 50` to find improvements

### Research agent generates no hypotheses
✅ Check wiki has pages: `ls wiki/concepts/ wiki/entities/ wiki/security/`  
✅ System needs some initial content to detect gaps

---

## What to Expect

### First Hour
- Monitors poll sources (arXiv, CVE, GitHub, RSS)
- Queue fills with sources
- Processing begins (normalize → extract → integrate)
- Metrics start recording

### First Day
- 50-100 sources processed
- 1-2 prompt optimization cycles
- 2-4 research hypotheses generated
- Wiki grows by 10-20 pages

### First Week
- 500+ sources processed
- 10-20 optimization cycles
- 20-30 hypotheses tested
- Wiki grows to 200+ pages
- First retrospective validation runs

### First Month
- 2000+ sources processed
- 100+ optimization cycles
- 100+ hypotheses tested
- Wiki grows to 500+ pages
- Confidence scores stabilize
- System fully autonomous

---

## Success Indicators

✅ **System is working if:**
- Daemon runs without crashes
- Queue processes sources
- Metrics database grows
- Wiki pages increase
- Experiments log updates
- No critical errors in logs

✅ **System is improving if:**
- Avg extraction confidence increases
- Conflict rate decreases
- Lint pass rate increases
- Research hypotheses succeed
- Human interventions decrease

---

## Weekly Maintenance (15 minutes)

### Monday Morning Checklist
1. **Review experiment log:** `cat wiki/experiments.md | tail -50`
2. **Check validation report:** `cat wiki/validation_report.md`
3. **Review conflicts:** `grep -r "\[CONFLICT\]" wiki/`
4. **Check metrics:** Run metrics query (see above)
5. **Review critical alerts:** `cat CRITICAL_ALERT.md` (if exists)

### Actions
- Resolve flagged conflicts
- Approve/reject research hypotheses
- Adjust research agenda if needed
- Update `.env` if monitors need changes

---

## Advanced Usage

### Run overnight optimization (100 cycles)
```bash
nohup python tools/prompt_optimizer.py --cycles 100 > optimizer.log 2>&1 &
```

### Run 7-day research trial
```bash
# Start unified daemon in background
nohup python tools/unified_daemon.py > daemon.log 2>&1 &

# Check after 7 days
tail -100 daemon.log
cat wiki/experiments.md
```

### Export metrics for analysis
```bash
sqlite3 metrics.db "SELECT * FROM daily_summary ORDER BY date DESC LIMIT 30" > metrics.csv
```

---

## Getting Help

### Check documentation
- `PHASE3_FINAL_SUMMARY.md` - Complete overview
- `IMPLEMENTATION_STATUS.md` - Current status
- `PHASE3_AUTONOMOUS_RESEARCH_PLAN.md` - Technical details
- `research_agenda.md` - Research priorities

### Common issues
- **LLM timeout:** Increase timeout in `common.py`
- **Queue stuck:** Restart daemon
- **Metrics not recording:** Check `metrics.db` permissions
- **Git conflicts:** System auto-reverts, check `git log`

---

## That's It!

**You're now running an autonomous research system that:**
- Monitors 4 source types continuously
- Processes with priority queue
- Optimizes its own prompts
- Generates research hypotheses
- Validates quality automatically
- Tracks all metrics comprehensively

**Enjoy your autonomous research partner! 🚀**

---

**Questions?** Check `PHASE3_FINAL_SUMMARY.md` for complete details.
