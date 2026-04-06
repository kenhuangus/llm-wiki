# LM Studio CLI Configuration for Maximum Context Length

**System:** Mac Mini with 64GB RAM  
**Model:** google/gemma-4-26b-a4b:3 (26B parameters, 4-bit quantized)  
**Goal:** Maximize context length for paper generation

---

## Quick Commands

### 1. Check Current Configuration
```bash
# Check if LM Studio CLI is available
lms --version

# If not found, use the full path
/Applications/LM\ Studio.app/Contents/MacOS/lms --version
```

### 2. List Loaded Models
```bash
lms ps
# or
/Applications/LM\ Studio.app/Contents/MacOS/lms ps
```

### 3. Configure Model with Maximum Context
```bash
# Stop current server
lms server stop

# Start with maximum context length (32K tokens)
lms server start google/gemma-4-26b-a4b:3 \
  --context-length 32768 \
  --gpu-layers -1 \
  --port 1234

# Alternative: 16K context (more stable)
lms server start google/gemma-4-26b-a4b:3 \
  --context-length 16384 \
  --gpu-layers -1 \
  --port 1234
```

---

## Detailed Configuration

### Option 1: Using LM Studio CLI (Recommended)

#### Step 1: Find LM Studio CLI
```bash
# Check if lms is in PATH
which lms

# If not found, add to PATH
echo 'export PATH="/Applications/LM Studio.app/Contents/MacOS:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Or create an alias
echo 'alias lms="/Applications/LM\ Studio.app/Contents/MacOS/lms"' >> ~/.zshrc
source ~/.zshrc
```

#### Step 2: Stop Current Server
```bash
lms server stop
```

#### Step 3: Start with Optimal Settings for 64GB RAM

**Maximum Context (32K tokens):**
```bash
lms server start google/gemma-4-26b-a4b:3 \
  --context-length 32768 \
  --gpu-layers -1 \
  --threads 8 \
  --port 1234 \
  --host 0.0.0.0
```

**Balanced (16K tokens - Recommended):**
```bash
lms server start google/gemma-4-26b-a4b:3 \
  --context-length 16384 \
  --gpu-layers -1 \
  --threads 8 \
  --port 1234 \
  --host 0.0.0.0
```

**Conservative (8K tokens):**
```bash
lms server start google/gemma-4-26b-a4b:3 \
  --context-length 8192 \
  --gpu-layers -1 \
  --threads 8 \
  --port 1234 \
  --host 0.0.0.0
```

#### Parameter Explanations:
- `--context-length`: Maximum context window in tokens
- `--gpu-layers -1`: Use all available GPU layers (Metal on Mac)
- `--threads 8`: Number of CPU threads (adjust based on your CPU)
- `--port 1234`: Server port (default)
- `--host 0.0.0.0`: Allow network access

---

### Option 2: Using Configuration File

#### Step 1: Create Configuration File
```bash
cat > ~/lm-studio-config.json << 'EOF'
{
  "model": "google/gemma-4-26b-a4b:3",
  "context_length": 32768,
  "gpu_layers": -1,
  "threads": 8,
  "port": 1234,
  "host": "0.0.0.0",
  "rope_freq_base": 10000,
  "rope_freq_scale": 1.0,
  "batch_size": 512,
  "ubatch_size": 128
}
EOF
```

#### Step 2: Start Server with Config
```bash
lms server start --config ~/lm-studio-config.json
```

---

### Option 3: Using llama.cpp Directly (Advanced)

If LM Studio CLI doesn't support all options, use llama.cpp directly:

#### Step 1: Find Model Path
```bash
# LM Studio models are typically stored here:
ls -la ~/Library/Application\ Support/LM\ Studio/models/

# Or check LM Studio settings for model path
```

#### Step 2: Start llama.cpp Server
```bash
# Navigate to llama.cpp directory (if installed)
cd /path/to/llama.cpp

# Start server with maximum context
./server \
  -m ~/Library/Application\ Support/LM\ Studio/models/google/gemma-4-26b-a4b-3.gguf \
  -c 32768 \
  -ngl -1 \
  -t 8 \
  --port 1234 \
  --host 0.0.0.0
```

---

## Memory Calculations for 64GB RAM

### Gemma 4 26B (4-bit quantized)

**Model Size:**
- Base model: ~14 GB (4-bit quantization)
- Context overhead: ~0.5 MB per 1K tokens

**Memory Usage by Context Length:**

| Context Length | Model | Context | Total | Available for OS |
|----------------|-------|---------|-------|------------------|
| 4K tokens | 14 GB | 2 GB | 16 GB | 48 GB ✅ |
| 8K tokens | 14 GB | 4 GB | 18 GB | 46 GB ✅ |
| 16K tokens | 14 GB | 8 GB | 22 GB | 42 GB ✅ |
| 32K tokens | 14 GB | 16 GB | 30 GB | 34 GB ✅ |
| 64K tokens | 14 GB | 32 GB | 46 GB | 18 GB ⚠️ |
| 128K tokens | 14 GB | 64 GB | 78 GB | -14 GB ❌ |

**Recommendation for 64GB RAM:** 32K tokens (safe), 64K tokens (risky)

---

## Optimal Configuration for Your System

### Recommended: 32K Context Length

```bash
#!/bin/bash
# save as: start_lms_32k.sh

# Stop any running server
lms server stop 2>/dev/null || true

# Wait for shutdown
sleep 2

# Start with 32K context
lms server start google/gemma-4-26b-a4b:3 \
  --context-length 32768 \
  --gpu-layers -1 \
  --threads 8 \
  --port 1234 \
  --host 0.0.0.0 \
  --rope-freq-base 10000 \
  --rope-freq-scale 1.0

echo "LM Studio server started with 32K context length"
echo "Server: http://localhost:1234"
```

Make it executable:
```bash
chmod +x start_lms_32k.sh
./start_lms_32k.sh
```

---

## Verification Commands

### Test 1: Check Server Status
```bash
curl http://localhost:1234/v1/models | python -m json.tool
```

### Test 2: Test Context Length
```bash
python3 << 'EOF'
import requests
import json

# Generate a long prompt (simulate large context)
long_text = "word " * 1000  # ~1000 tokens

response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    headers={"Content-Type": "application/json"},
    json={
        "model": "google/gemma-4-26b-a4b:3",
        "messages": [
            {"role": "user", "content": f"Summarize this: {long_text}"}
        ],
        "max_tokens": 500
    }
)

data = response.json()
if "usage" in data:
    print(f"Prompt tokens: {data['usage']['prompt_tokens']}")
    print(f"Completion tokens: {data['usage']['completion_tokens']}")
    print(f"Total tokens: {data['usage']['total_tokens']}")
else:
    print("Error:", data)
EOF
```

### Test 3: Test Long Generation
```bash
python3 << 'EOF'
import requests
import json

response = requests.post(
    "http://localhost:1234/v1/chat/completions",
    headers={"Content-Type": "application/json"},
    json={
        "model": "google/gemma-4-26b-a4b:3",
        "messages": [
            {"role": "user", "content": "Write a 2000-word essay about AI"}
        ],
        "max_tokens": 4096
    },
    timeout=120
)

data = response.json()
if "choices" in data:
    content = data["choices"][0]["message"]["content"]
    word_count = len(content.split())
    finish_reason = data["choices"][0]["finish_reason"]
    
    print(f"Generated: {word_count} words")
    print(f"Finish reason: {finish_reason}")
    print(f"Status: {'✅ Complete' if finish_reason == 'stop' else '⚠️ Cut off'}")
else:
    print("Error:", data)
EOF
```

---

## Troubleshooting

### Issue 1: "lms: command not found"

**Solution:**
```bash
# Use full path
/Applications/LM\ Studio.app/Contents/MacOS/lms server start google/gemma-4-26b-a4b:3 --context-length 32768

# Or add to PATH
export PATH="/Applications/LM Studio.app/Contents/MacOS:$PATH"
```

### Issue 2: "Out of memory" Error

**Solution:** Reduce context length
```bash
# Try 16K instead of 32K
lms server start google/gemma-4-26b-a4b:3 --context-length 16384
```

### Issue 3: Server Won't Start

**Solution:** Check if port is in use
```bash
# Check what's using port 1234
lsof -i :1234

# Kill existing process
kill -9 $(lsof -t -i:1234)

# Start server again
lms server start google/gemma-4-26b-a4b:3 --context-length 32768
```

### Issue 4: Slow Generation

**Solution:** Optimize GPU layers
```bash
# Check GPU memory
system_profiler SPDisplaysDataType | grep VRAM

# Adjust GPU layers if needed (e.g., 40 layers instead of all)
lms server start google/gemma-4-26b-a4b:3 \
  --context-length 32768 \
  --gpu-layers 40
```

---

## Alternative: Using Python to Configure

If CLI doesn't work, configure via Python:

```python
#!/usr/bin/env python3
# save as: configure_lms.py

import subprocess
import time
import requests

def stop_server():
    """Stop LM Studio server."""
    try:
        subprocess.run(["lms", "server", "stop"], check=False)
        time.sleep(2)
    except:
        print("Could not stop server (may not be running)")

def start_server(context_length=32768):
    """Start LM Studio server with specified context length."""
    cmd = [
        "lms", "server", "start",
        "google/gemma-4-26b-a4b:3",
        "--context-length", str(context_length),
        "--gpu-layers", "-1",
        "--threads", "8",
        "--port", "1234",
        "--host", "0.0.0.0"
    ]
    
    print(f"Starting server with {context_length} context length...")
    subprocess.Popen(cmd)
    time.sleep(5)  # Wait for server to start

def test_server():
    """Test if server is responding."""
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
    except:
        pass
    print("❌ Server is not responding")
    return False

if __name__ == "__main__":
    stop_server()
    start_server(context_length=32768)
    test_server()
```

Run it:
```bash
chmod +x configure_lms.py
python3 configure_lms.py
```

---

## Performance Expectations

### With 32K Context Length:

| Metric | Value |
|--------|-------|
| Startup time | 10-20 seconds |
| First token latency | 1-2 seconds |
| Generation speed | 80-120 tokens/second |
| Memory usage | ~30 GB |
| Max paper length | ~20,000 words |

### Generation Time Estimates:

| Output Length | Time |
|---------------|------|
| 1,000 tokens | ~10 seconds |
| 2,000 tokens | ~20 seconds |
| 4,000 tokens | ~40 seconds |
| 8,000 tokens | ~80 seconds |
| 16,000 tokens | ~160 seconds (2.7 min) |

---

## Final Recommendation

**For your Mac Mini with 64GB RAM, use this command:**

```bash
# Stop current server
lms server stop

# Start with 32K context (maximum safe for 64GB RAM)
lms server start google/gemma-4-26b-a4b:3 \
  --context-length 32768 \
  --gpu-layers -1 \
  --threads 8 \
  --port 1234 \
  --host 0.0.0.0

# Verify it's working
curl http://localhost:1234/v1/models
```

**Then test paper generation:**
```bash
python tools/paper_agent.py --focus agentic_ai_security
```

This should give you complete papers with 4,000-6,000 words!

---

## Quick Reference Card

```bash
# Stop server
lms server stop

# Start with 32K context (recommended)
lms server start google/gemma-4-26b-a4b:3 --context-length 32768 --gpu-layers -1

# Check status
curl http://localhost:1234/v1/models

# Test generation
python tools/paper_agent.py --focus agentic_ai_security

# Monitor memory
top -l 1 | grep "PhysMem"
```

---

**Status:** Ready to configure  
**Next Step:** Run the commands above to maximize context length
