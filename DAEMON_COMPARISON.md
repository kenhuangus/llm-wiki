# Daemon Comparison: daemon.py vs unified_daemon.py

## Quick Summary

| Feature | daemon.py | unified_daemon.py |
|---------|-----------|-------------------|
| **Purpose** | Basic processing only | Full autonomous system |
| **Components** | 1 (WikiDaemon) | 4 (WikiDaemon + Optimizer + Research + Validator) |
| **Scheduling** | Continuous processing only | Continuous + scheduled tasks |
| **Use Case** | Simple source processing | Complete autonomous research |
| **Complexity** | Simple | Advanced |

---

## daemon.py - Basic Processing Daemon

### What It Does
Continuously processes sources through the basic pipeline:
1. Poll monitors (arXiv, CVE, GitHub, RSS)
2. Normalize sources
3. Extract knowledge (LLM)
4. Integrate into wiki (LLM)
5. Run lint (periodic)
6. Rebuild index (periodic)

### Key Features
- ✅ Priority queue (CVSS-based)
- ✅ Continuous source processing
- ✅ Periodic lint checks (every 1 hour)
- ✅ Periodic index rebuilds (every 30 minutes)
- ✅ Critical CVE escalation (CVSS ≥ 9.0)
- ✅ Graceful shutdown
- ✅ Metrics tracking

### Scheduling
- **Continuous:** Monitor polling (every 5 minutes)
- **Continuous:** Source processing (as queue fills)
- **Every 1 hour:** Lint check
- **Every 30 minutes:** Index rebuild

### When to Use
- You only want basic source processing
- You don't need prompt optimization
- You don't need research hypothesis generation
- You don't need retrospective validation
- You want a simpler, more focused daemon

### Command
```bash
python tools/daemon.py
```

---

## unified_daemon.py - Complete Autonomous System

### What It Does
Integrates ALL Phase 3 components into a single autonomous system:
1. **WikiDaemon** - Basic processing (same as daemon.py)
2. **PromptOptimizer** - Meta-learning (improves extraction/integration prompts)
3. **ResearchAgent** - Proactive research (generates hypotheses, fills gaps)
4. **RetrospectiveValidator** - Quality assurance (validates old claims)

### Key Features
- ✅ Everything from daemon.py
- ✅ Prompt optimization with ratchet loop
- ✅ Research hypothesis generation
- ✅ Hypothesis execution
- ✅ Retrospective validation
- ✅ Confidence adjustment
- ✅ Contradiction detection
- ✅ Lazy initialization (components created only when needed)

### Scheduling
- **Continuous:** Source processing (WikiDaemon)
- **Every 4 hours:** Prompt optimization (1 cycle)
- **Every 6 hours:** Research hypotheses (generate 5, execute top 2)
- **Every 7 days:** Retrospective validation (validate all recent pages)

### When to Use
- You want the complete autonomous research system
- You want prompts to improve automatically
- You want the system to proactively find knowledge gaps
- You want quality assurance on existing content
- You want the full Phase 3 experience

### Command
```bash
python tools/unified_daemon.py
```

---

## Detailed Comparison

### 1. Architecture

**daemon.py:**
```
WikiDaemon
├── poll_monitors()
├── process_source()
│   ├── normalize_source()
│   ├── extract_knowledge()
│   └── integrate_knowledge()
├── run_lint()
└── rebuild_index()
```

**unified_daemon.py:**
```
UnifiedDaemon
├── WikiDaemon (basic processing)
├── PromptOptimizer (meta-learning)
├── ResearchAgent (proactive research)
└── RetrospectiveValidator (quality assurance)
```

---

### 2. Processing Flow

**daemon.py:**
```
Monitor → Queue → Normalize → Extract → Integrate → Done
                                                    ↓
                                            (Periodic lint/index)
```

**unified_daemon.py:**
```
Monitor → Queue → Normalize → Extract → Integrate → Done
                                                    ↓
                                    (Periodic lint/index)
                                                    ↓
                            (Every 4h: Optimize prompts)
                                                    ↓
                            (Every 6h: Generate hypotheses)
                                                    ↓
                            (Every 7d: Validate quality)
```

---

### 3. Resource Usage

**daemon.py:**
- Memory: ~200-500 MB
- CPU: Low (mostly idle, spikes during LLM calls)
- LLM calls: 2 per source (extract + integrate)
- Disk I/O: Moderate

**unified_daemon.py:**
- Memory: ~500-1000 MB (4 components)
- CPU: Low-Medium (more scheduled tasks)
- LLM calls: 2 per source + optimization + research + validation
- Disk I/O: Moderate-High

---

### 4. Initialization

**daemon.py:**
```python
daemon = WikiDaemon()
daemon.run()
```

**unified_daemon.py:**
```python
unified = UnifiedDaemon()
# Creates WikiDaemon immediately
# Creates other components lazily (when first needed)
unified.run()
```

---

### 5. Shutdown Behavior

**daemon.py:**
- Stops processing
- Closes metrics DB
- Logs final stats

**unified_daemon.py:**
- Stops all components
- Closes all metrics DBs
- Logs final stats for all components

---

### 6. Output/Logging

**daemon.py:**
```
🤖 WikiDaemon started
📡 Polling arxiv_monitor.py...
📥 Queued: source.md (priority: 2)
🔄 Processing: source.md (priority: 2)
✅ Processed successfully (1 total)
📊 Status: Processed: 1, Failures: 0
```

**unified_daemon.py:**
```
🤖 Unified daemon started
📥 Processing sources...
   ✓ Processed 10 sources
🔬 Running prompt optimization...
   ✓ Optimization kept (improvement found)
💡 Generating research hypotheses...
   ✓ Generated 5 hypotheses, executed 2
📊 System Status: Sources processed: 10
⏰ Next scheduled tasks:
   Optimization: 3.8h
   Research: 5.7h
   Validation: 6.9d
```

---

### 7. Configuration

**daemon.py:**
```python
POLL_INTERVAL = 300      # 5 minutes
LINT_INTERVAL = 3600     # 1 hour
INDEX_INTERVAL = 1800    # 30 minutes
```

**unified_daemon.py:**
```python
optimization_interval = 3600 * 4      # 4 hours
research_interval = 3600 * 6          # 6 hours
validation_interval = 3600 * 24 * 7   # 7 days
```

---

### 8. Error Handling

**daemon.py:**
- Retries failed sources with lower priority
- Logs errors to wiki/log.md
- Continues on error

**unified_daemon.py:**
- Same as daemon.py for processing
- Additional error handling for optimizer/research/validator
- Logs component-specific errors
- Continues on error (doesn't crash entire system)

---

### 9. Metrics Tracking

**daemon.py:**
- Extraction success/failure
- Processing count
- Failure count
- Success rate

**unified_daemon.py:**
- Everything from daemon.py
- Optimization experiments
- Hypothesis generation/execution
- Validation results
- Confidence adjustments

---

## Use Case Recommendations

### Use daemon.py if:
- ✅ You're just starting out
- ✅ You want to test basic processing first
- ✅ You have limited resources
- ✅ You don't need advanced features
- ✅ You want faster processing (no overhead)
- ✅ You're debugging the pipeline

### Use unified_daemon.py if:
- ✅ You want the complete autonomous system
- ✅ You want prompts to improve over time
- ✅ You want proactive knowledge gap detection
- ✅ You want quality assurance
- ✅ You're ready for production deployment
- ✅ You want the full Phase 3 experience

---

## Migration Path

### Start with daemon.py
1. Run for 24 hours to process backlog
2. Verify pipeline works correctly
3. Check wiki pages for quality

### Upgrade to unified_daemon.py
1. Stop daemon.py
2. Start unified_daemon.py
3. Monitor for 1 week
4. Review optimization experiments
5. Review research hypotheses
6. Review validation reports

---

## Performance Comparison

| Metric | daemon.py | unified_daemon.py |
|--------|-----------|-------------------|
| Sources/hour | ~30-60 | ~30-60 (same) |
| Memory usage | 200-500 MB | 500-1000 MB |
| CPU usage | Low | Low-Medium |
| LLM calls/hour | ~60-120 | ~60-120 + scheduled |
| Disk I/O | Moderate | Moderate-High |
| Startup time | <1 second | ~2-3 seconds |

---

## Code Reuse

**unified_daemon.py reuses daemon.py:**
```python
from daemon import WikiDaemon

class UnifiedDaemon:
    def __init__(self):
        self.wiki_daemon = WikiDaemon()  # Reuses entire daemon
        # ... adds more components
```

This means:
- No code duplication
- Bug fixes in daemon.py automatically benefit unified_daemon.py
- Unified daemon is just a wrapper that adds scheduling

---

## Recommendation

### For Testing/Development
**Use daemon.py** - Simpler, faster, easier to debug

### For Production
**Use unified_daemon.py** - Complete system, self-improving, autonomous

### For Debugging
**Use daemon.py** - Isolates basic processing from advanced features

---

## Bottom Line

- **daemon.py** = Basic processing daemon (Week 2 deliverable)
- **unified_daemon.py** = Complete autonomous system (Week 6 deliverable)

Both are production-ready. Choose based on your needs:
- Simple processing → daemon.py
- Full autonomous research → unified_daemon.py

You can always start with daemon.py and upgrade to unified_daemon.py later!

---

**Last Updated:** 2026-04-05  
**Status:** Both daemons operational and tested
