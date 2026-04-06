# LLM Wiki - Configuration Guide

**Quick Start:** Your system is almost ready! Just need to configure LM Studio.

---

## 🎯 What You Need to Do

Your code is already configured with the correct `max_tokens` settings. Now you just need to configure LM Studio to use a larger context window.

### Option 1: Automated (Recommended)
```bash
./configure_lms_max_context.sh
```

### Option 2: Manual CLI
```bash
lms server stop
lms server start google/gemma-4-26b-a4b:3 --context-length 16384 --gpu-layers -1
```

### Option 3: LM Studio UI
1. Open LM Studio
2. Click on your model
3. Set Context Length to 16384
4. Reload model

---

## 🧪 Test Your Configuration

### Quick Test
```bash
python test_current_config.py
```

This will run 3 tests:
- ✅ Short generation (500 words)
- ✅ Medium generation (2000 words)  
- ✅ Long generation (4000 words)

### Generate a Paper
```bash
python tools/paper_agent.py --focus agentic_ai_security
```

Expected: 4,000-6,000 word paper in `papers/` directory

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `CURRENT_STATUS_AND_NEXT_STEPS.md` | Complete status and action items |
| `LMS_CLI_CONFIGURATION.md` | Detailed CLI commands and options |
| `MODEL_CONTEXT_ANALYSIS.md` | Technical analysis of the issue |
| `configure_lms_max_context.sh` | Automated configuration script |
| `test_current_config.py` | Test suite for verification |

---

## ⚡ Quick Reference

### Your System
- **Hardware:** Mac Mini with 64GB RAM
- **Model:** google/gemma-4-26b-a4b:3 (26B, 4-bit)
- **Recommended Context:** 16K-32K tokens
- **Code Status:** ✅ Already configured

### What Was Fixed
- ✅ `max_tokens` increased to 8192 (local) and 16384 (OpenRouter)
- ✅ Timeout reduced to 60s (prevents hanging)
- ✅ 4 retries on local model before cloud fallback
- ✅ Automatic OpenRouter fallback on context errors

### What You Need to Do
- ⏳ Configure LM Studio context length (16K recommended)
- ⏳ Test with `test_current_config.py`
- ⏳ Generate a paper to verify

---

## 🔧 Troubleshooting

### Papers are still short
→ Run `./configure_lms_max_context.sh` and choose option 2 (16K)

### "lms: command not found"
→ Use full path: `/Applications/LM\ Studio.app/Contents/MacOS/lms`

### Out of memory
→ Reduce context to 8K: `lms server start google/gemma-4-26b-a4b:3 --context-length 8192`

### Server won't start
→ Kill existing: `kill -9 $(lsof -t -i:1234)` then restart

---

## 🎓 Understanding the Issue

**Problem:** Papers were only 21-551 words instead of 4,000-6,000 words

**Root Cause:** `max_tokens` limit (NOT context length)
- Model supports 8K-128K context
- But was limited by default max_tokens (~512-1024)
- This caused `finish_reason=length` (premature truncation)

**Solution:** Two-part fix
1. Code: Increased max_tokens ✅ (already done)
2. LM Studio: Increase context length ⏳ (you need to do this)

---

## 🚀 Next Steps

1. **Configure LM Studio** (5 minutes)
   ```bash
   ./configure_lms_max_context.sh
   ```

2. **Test Configuration** (5 minutes)
   ```bash
   python test_current_config.py
   ```

3. **Generate Paper** (3 minutes)
   ```bash
   python tools/paper_agent.py --focus agentic_ai_security
   ```

4. **Verify Results**
   ```bash
   ls -lh papers/
   wc -w papers/*.md
   ```

---

## 📊 Expected Results

### Before Configuration
- Paper length: 21-551 words
- Sections: Incomplete
- Status: ❌ Not usable

### After Configuration
- Paper length: 4,000-6,000 words
- Sections: Complete (Abstract, Intro, Methods, etc.)
- Status: ✅ Ready for submission

---

## 💡 Pro Tips

1. **Use 16K context** for best balance of speed and quality
2. **Use 32K context** if you want maximum quality (slower)
3. **Let OpenRouter handle it** if local model has issues (automatic)
4. **Monitor memory** with `top` to ensure you're not swapping

---

## 🎉 You're Almost There!

Your code is ready. Just configure LM Studio and you'll be generating full research papers!

**Start here:** `./configure_lms_max_context.sh`

---

**Questions?** Check `CURRENT_STATUS_AND_NEXT_STEPS.md` for detailed information.
