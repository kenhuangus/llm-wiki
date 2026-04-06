# Wiki UI Status

**Date:** 2026-04-06  
**Status:** ✅ Running

---

## 🌐 Access Your Wiki

### Wiki UI (Frontend)
**URL:** http://localhost:5173  
**Status:** ✅ Running  
**Technology:** React + Vite  
**Process ID:** 6

### API Server (Backend)
**URL:** http://localhost:8000  
**Status:** ✅ Running  
**Technology:** FastAPI + Python  
**Process ID:** 15  
**API Docs:** http://localhost:8000/docs

---

## 📊 Current Content Status

### Wiki Pages
- **Total Pages:** 13 pages
- **Location:** `wiki/` directory
- **Includes:** Concepts, entities, events, comparisons

### New Content Processing

**RSS Ingestion:** ✅ Complete
- 5 new items from OpenAI News
- 5 new arXiv papers

**Pipeline Status:**
- ✅ Normalization: Complete (93 documents)
- ⏳ Extraction: In progress (running in background)
- ⏳ Integration: Pending (will run after extraction)

**When will new content appear?**
- The extraction and integration steps are still processing
- Once complete, new pages will automatically appear in the wiki UI
- Estimated time: 10-30 minutes depending on content volume

---

## 🔄 How Content Flows to the UI

```
RSS Feeds → Ingestion → Normalization → Extraction → Integration → Wiki UI
   ✅           ✅            ✅             ⏳            ⏳          📱
```

1. **RSS Feeds** - Fetched from your configured feeds
2. **Ingestion** - Saved to `raw/auto_ingest/rss/`
3. **Normalization** - Cleaned and formatted → `raw/normalized/rss/`
4. **Extraction** - LLM extracts entities/concepts → `.json` files
5. **Integration** - Creates wiki pages → `wiki/` directory
6. **Wiki UI** - Displays pages via API at http://localhost:5173

---

## 📱 Using the Wiki UI

### Features Available

1. **Search** - Search across all wiki content
2. **Browse Articles** - View all pages organized by type
3. **View History** - See git history for each page
4. **Edit Pages** - Edit wiki content directly
5. **Upload Files** - Upload new sources for processing
6. **View Logs** - See system operation logs
7. **Stats Dashboard** - View wiki statistics

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/search` | POST | Search wiki content |
| `/api/articles` | GET | List all articles |
| `/api/article/{path}` | GET | Get article content |
| `/api/article/{path}` | POST | Save article |
| `/api/ingest` | POST | Ingest new sources |
| `/api/logs` | GET | View system logs |
| `/api/stats` | GET | Get wiki statistics |
| `/api/history/{path}` | GET | Get file history |
| `/api/backlinks/{path}` | GET | Get backlinks |

---

## 🔍 Checking New Content

### Option 1: Wait for Processing to Complete
The pipeline is running in the background. New content will appear automatically once extraction and integration complete.

### Option 2: Check Processing Status
```bash
# Check if extraction is complete
ls raw/normalized/rss/*.json | wc -l

# Check wiki pages
ls wiki/**/*.md | wc -l

# View logs
tail -f wiki/log.md
```

### Option 3: Force Refresh
If you want to see content immediately, you can:
1. Wait for current pipeline to finish
2. Refresh the wiki UI (http://localhost:5173)
3. New pages will appear in the articles list

---

## 🚀 Managing the Servers

### Check Server Status
```bash
# Both servers are running as background processes
# UI: Process ID 6
# API: Process ID 15
```

### View Server Logs
```bash
# View UI logs
# (Check terminal where npm run dev was started)

# View API logs
# (Check terminal where python api_server.py was started)
```

### Restart Servers (if needed)
```bash
# Stop servers
# (Use Ctrl+C in their respective terminals)

# Start UI
cd ui
npm run dev

# Start API (in separate terminal)
python api_server.py
```

---

## 📈 What You'll See

### Current Content (13 pages)
The wiki currently has 13 pages from previous ingestions:
- Concepts (AI models, security topics)
- Entities (models, tools, CVEs)
- Events (releases, advisories)
- Comparisons

### New Content (Coming Soon)
Once processing completes, you'll see:
- 5 new OpenAI articles
  - OpenAI acquires TBPN
  - Codex flexible pricing
  - Gradient Labs AI account manager
  - Accelerating AI phase
  - Disaster response AI
- 5 new arXiv papers
  - Federated learning robustness
  - Hierarchical planning
  - Intrusion detection
  - Medical AI framework
  - Coupled control systems

---

## 🎯 Quick Actions

### View Your Wiki Now
```
Open browser: http://localhost:5173
```

### Check API Status
```
Open browser: http://localhost:8000
```

### View API Documentation
```
Open browser: http://localhost:8000/docs
```

### Search for Content
```
1. Go to http://localhost:5173
2. Use the search bar
3. Enter keywords like "OpenAI", "security", "agent"
```

---

## 🔧 Troubleshooting

### UI Not Loading?
```bash
# Check if UI server is running
curl http://localhost:5173

# If not, start it
cd ui
npm run dev
```

### API Not Responding?
```bash
# Check if API server is running
curl http://localhost:8000

# If not, start it
python api_server.py
```

### New Content Not Showing?
```bash
# Check if extraction is complete
ls raw/normalized/rss/*.json | wc -l

# Check if integration ran
tail -20 wiki/log.md

# Force re-index
python tools/index.py
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     WIKI SYSTEM                              │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Frontend   │ ◄─────► │   Backend    │                 │
│  │  React + Vite│         │   FastAPI    │                 │
│  │  Port: 5173  │         │  Port: 8000  │                 │
│  └──────────────┘         └──────────────┘                 │
│         │                         │                         │
│         │                         ▼                         │
│         │                  ┌──────────────┐                │
│         │                  │  Wiki Files  │                │
│         │                  │  wiki/*.md   │                │
│         │                  └──────────────┘                │
│         │                         ▲                         │
│         │                         │                         │
│         │                  ┌──────────────┐                │
│         └─────────────────►│  Processing  │                │
│                            │   Pipeline   │                │
│                            └──────────────┘                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Summary

**Wiki UI:** http://localhost:5173 ✅ Running  
**API Server:** http://localhost:8000 ✅ Running  
**Current Pages:** 13 pages  
**New Content:** Processing (will appear automatically)  
**Status:** Fully operational

**Next Steps:**
1. Open http://localhost:5173 in your browser
2. Browse existing content
3. Wait for new RSS content to finish processing
4. Refresh to see new pages

---

**Your wiki is live and ready to use! 🎉**
