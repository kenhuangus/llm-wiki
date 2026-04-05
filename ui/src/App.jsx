import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Search, Loader2, Plus, List, Database, Globe, Info, ExternalLink, HelpCircle, FileText, Settings, Users, BookOpen, Clock, AlertTriangle, ShieldCheck, Mail, ArrowLeft, ChevronRight, Upload } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [view, setView] = useState('Home'); // Home, SearchResults, Contents, Article, Logs, Upload
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [articles, setArticles] = useState([]);
  const [currentArticle, setCurrentArticle] = useState(null);
  const [logs, setLogs] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [ingestUrls, setIngestUrls] = useState('');
  const [ingesting, setIngesting] = useState(false);
  const [message, setMessage] = useState(null);
  const [stats, setStats] = useState({ pageCount: 0, monitorCount: 0, conflictCount: 0, avgConfidence: 0 });

  const fetchStats = async () => {
    try {
      const resp = await axios.get(`${API_BASE}/stats`);
      setStats(resp.data);
    } catch (err) { console.error("Stats fail", err); }
  };

  const fetchAllContents = async () => {
    setLoading(true);
    setView('Contents');
    try {
      const resp = await axios.get(`${API_BASE}/articles`);
      setArticles(resp.data.articles || []);
    } catch (err) { setMessage({ type: 'error', text: 'Failed to fetch wiki contents.' });
    } finally { setLoading(false); }
  };

  const fetchLogs = async () => {
    setLoading(true);
    setView('Logs');
    try {
      const resp = await axios.get(`${API_BASE}/logs`);
      setLogs(resp.data.logs);
    } catch (err) { setMessage({ type: 'error', text: 'Failed to fetch logs.' });
    } finally { setLoading(false); }
  };

  const openArticle = async (path) => {
    setLoading(true);
    const normalizedPath = path.replace(/\\/g, '/');
    try {
      const resp = await axios.get(`${API_BASE}/article/${normalizedPath}`);
      if (resp.data.error) throw new Error(resp.data.error);
      setCurrentArticle(resp.data);
      setView('Article');
    } catch (err) {
      setMessage({ type: 'error', text: `Failed to load ${path}` });
    } finally { setLoading(false); }
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setView('SearchResults');
    try {
      const resp = await axios.post(`${API_BASE}/search`, { query });
      setResults(resp.data.results || []);
    } catch (err) {
      setMessage({ type: 'error', text: 'Search failed. Backend offline?' });
    } finally {
      setLoading(false);
    }
  };

  const handleIngest = async () => {
    const urlsList = ingestUrls.split('\n').map(u => u.trim()).filter(Boolean);
    if (!urlsList.length) return;
    setIngesting(true);
    try {
      await axios.post(`${API_BASE}/ingest`, { urls: urlsList });
      setMessage({ type: 'success', text: 'Batch queued safely.' });
      setIngestUrls('');
    } catch (err) {
      setMessage({ type: 'error', text: 'Ingestion failed.' });
    } finally {
      setIngesting(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/upload`, formData);
      setMessage({ type: 'success', text: `Successfully uploaded ${file.name}` });
    } catch (err) {
      setMessage({ type: 'error', text: 'File upload failed.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const timer = setInterval(fetchStats, 60000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex min-h-screen bg-[#f6f6f6]">
      <aside className="w-[176px] flex-shrink-0 bg-[#f6f6f6] border-r border-[#a2a9b1] px-2 py-4">
        <div className="flex flex-col items-center mb-6 cursor-pointer" onClick={()=>setView('Home')}>
          <Database className="text-[#3366cc]" size={64} />
          <span className="text-[1.2em] font-serif mt-2">LLM WIKI</span>
        </div>

        <SidebarSection title="Navigation">
          <SidebarLink onClick={()=>setView('Home')} active={view==='Home'} icon={<Database size={12}/>} label="Main page" />
          <SidebarLink onClick={fetchAllContents} active={view==='Contents'} icon={<FileText size={12}/>} label="Contents" />
          <SidebarLink onClick={()=>{
             // "Current events" = open curated-sources or simply search for newsletter
             openArticle('synthesis/curated-sources.md');
          }} active={false} icon={<Globe size={12}/>} label="Current events" />
          <SidebarLink onClick={()=>setView('About')} active={view==='About'} icon={<HelpCircle size={12}/>} label="About LLM Wiki" />
        </SidebarSection>

        <SidebarSection title="Contribute">
          <SidebarLink icon={<Plus size={12}/>} label="Community portal" />
          <SidebarLink onClick={fetchLogs} active={view==='Logs'} icon={<Users size={12}/>} label="Recent changes" />
          <SidebarLink onClick={()=>setView('Upload')} active={view==='Upload'} icon={<Settings size={12}/>} label="Upload file" />
        </SidebarSection>

        <SidebarSection title="Tools">
          <div className="p-2 border border-[#a2a9b1] rounded bg-white text-[0.8em]">
            <span className="font-bold block mb-1 text-[#3366cc]">Batch Ingest</span>
            <textarea value={ingestUrls} onChange={(e)=>setIngestUrls(e.target.value)} className="w-full h-24 text-[10px] p-1 border border-[#ccc] mb-2" placeholder="Enter URLs..."/>
            <button disabled={ingesting} onClick={handleIngest} className="w-full bg-[#f8f9fa] border border-[#a2a9b1] p-1 text-[#3366cc] cursor-pointer hover:bg-[#eee]">{ingesting?'Queueing...':'Ingest Sources'}</button>
          </div>
          <SidebarLink icon={<List size={12}/>} label="What links here" />
          <SidebarLink icon={<Mail size={12}/>} label="Contact us" />
        </SidebarSection>
      </aside>

      <div className="flex-1 flex flex-col min-w-0 bg-white border-l border-[#a2a9b1] -ml-[1px]">
        <header className="h-10 flex items-center justify-between px-4 bg-[#f6f6f6] text-[0.85em]">
          <div className="flex gap-4 text-[#54595d]">
            <span className="cursor-pointer hover:underline">Log in</span>
            <span className="cursor-pointer hover:underline">Create account</span>
          </div>
          <div className="flex items-center gap-2">
            <form onSubmit={handleSearch} className="flex">
              <input type="text" value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Search LLM Wiki" className="w-[200px] border border-[#a2a9b1] p-1 text-[0.9em] outline-none" />
              <button type="submit" className="bg-white border border-[#a2a9b1] border-l-0 px-2 cursor-pointer hover:bg-[#eee]"><Search size={14} className="text-[#54595d]"/></button>
            </form>
          </div>
        </header>

        <div className="flex items-end h-[41px] px-[2.5em] mt-1">
          <div className="flex gap-[2px]">
            <WikiTab label="Article" active={['Article','Home','SearchResults','About','Upload'].includes(view)} onClick={()=>{}}/>
            <WikiTab label="Talk" active={false} onClick={()=>{}}/>
          </div>
          <div className="flex-1 border-b border-[#a2a9b1] h-[33px]"></div>
          <div className="flex gap-[2px]">
            <WikiTab label="Read" active={true} onClick={()=>{}}/>
            <WikiTab label="Edit" active={false}/>
            <WikiTab label="View history" active={false}/>
          </div>
        </div>

        <main className="flex-1 p-[2.5em] pb-[10em] min-w-0 overflow-y-auto">
          {message && (
            <div className={`p-2 border mb-4 text-sm flex gap-2 items-center ${message.type==='error' ? 'bg-red-50 border-red-200 text-red-700':'bg-green-50 border-green-200 text-green-700'}`}>
              <Info size={14}/> {message.text}
            </div>
          )}

          {loading ? (
             <div className="flex flex-col items-center py-20 text-[#54595d]"><Loader2 size={48} className="animate-spin mb-4 text-[#3366cc]"/><span>Fetching graph data...</span></div>
          ) : (
            <>
              {view === 'Home' && <HomeView />}
              {view === 'SearchResults' && <SearchResultsView results={results} openArticle={openArticle} />}
              {view === 'Contents' && <ContentsView articles={articles} openArticle={openArticle} />}
              {view === 'Article' && <ArticleView article={currentArticle} onBack={fetchAllContents} />}
              {view === 'Logs' && <LogsView logs={logs} />}
              {view === 'About' && <AboutView />}
              {view === 'Upload' && <UploadView onUpload={handleFileUpload} />}
            </>
          )}
        </main>
      </div>

      <aside className="w-[250px] flex-shrink-0 bg-white p-4 border-l border-[#eaecf0]">
        <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-1 text-[0.8em]">
          <div className="text-center font-bold bg-[#eaecf0] py-2 mb-2">Wiki Statistics</div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[40%] font-bold">Pages</div><div className="w-[60%]">{stats.pageCount}</div></div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[40%] font-bold">Monitors</div><div className="w-[60%]">{stats.monitorCount} Active</div></div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[40%] font-bold">Conflicts</div><div className="w-[60%] text-red-600">{stats.conflictCount} Flagged</div></div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[40%] font-bold">Confidence</div><div className="w-[60%]">{stats.avgConfidence.toFixed(2)} Avg</div></div>
          <div className="mt-4 p-2 bg-yellow-50 border-t border-yellow-200"><div className="flex gap-2 text-yellow-800 font-bold mb-1"><ShieldCheck size={14}/> Local-First</div><span className="text-[0.9em]">Knowledge graph is localized. Encrypted storage active.</span></div>
        </div>
      </aside>
    </div>
  );
}

// Sub-components
function HomeView() {
  return (
    <>
      <h1 className="wiki-h1">Main Page</h1>
      <p className="sub-title">From LLM Wiki, the free encyclopedia</p>
      <div className="wiki-text border border-[#a2a9b1] p-8 bg-[#f8f9fa] rounded">
        <h2 className="text-[1.5em] mb-4">Welcome to LLM Wiki</h2>
        <p>This is your entry point to the <b>Agentic Knowledge Graph</b>. Explore synthesized models, research papers, and security advisories.</p>
        <p className="mt-4">Use the <b>Contents</b> to browse categories, <b>Recent Changes</b> to monitor the autonomous agent's activity, or <b>Upload</b> to manually process local documents.</p>
      </div>
    </>
  );
}

function ContentsView({ articles, openArticle }) {
  return (
    <>
      <h1 className="wiki-h1">Contents</h1>
      <p className="sub-title">All articles currently documented in the graph</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-4 gap-y-2">
        {articles.map((art, i) => (
          <div key={i} onClick={()=>openArticle(art.path)} className="flex items-center gap-2 text-[#3366cc] cursor-pointer hover:underline text-[0.9em]">
            <ChevronRight size={12} className="text-slate-400"/> {art.title}
          </div>
        ))}
      </div>
    </>
  );
}

function LogsView({ logs }) {
  return (
    <>
      <h1 className="wiki-h1">Recent changes</h1>
      <p className="sub-title">Tracks autonomous agent activities and system operations</p>
      <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-4 font-mono text-[0.8em] whitespace-pre-wrap leading-[1.4]">
        {logs}
      </div>
    </>
  );
}

function UploadView({ onUpload }) {
  return (
    <>
      <h1 className="wiki-h1">Upload file</h1>
      <p className="sub-title">Manually add local files to the ingestion pipeline</p>
      <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-10 flex flex-col items-center justify-center border-dashed border-2">
         <Upload size={48} className="text-slate-400 mb-4"/>
         <label className="bg-[#3366cc] text-white px-4 py-2 cursor-pointer rounded hover:bg-[#2a52a2]">
            Select Document to Process
            <input type="file" className="hidden" onChange={onUpload} />
         </label>
         <p className="text-[0.8em] mt-4 text-slate-500">File will be added to raw/manual and processed by the next extraction pass.</p>
      </div>
    </>
  );
}

function AboutView() {
  return (
    <>
      <h1 className="wiki-h1">About LLM Wiki</h1>
      <p className="sub-title">Synthesizing the evolution of intelligence</p>
      <div className="prose prose-slate">
         <p><b>LLM Wiki</b> is an autonomous, agent-maintained platform designed to monitor and synthesize the hyper-dynamic AI research landscape. It bridges the gap between disparate data sources (arXiv, GitHub, NVD) and a structured knowledge graph.</p>
         <h3>Our Mission</h3>
         <p>To provide a zero-telemetry, local-first intelligence environment for security researchers and AI engineers.</p>
      </div>
    </>
  );
}

function SearchResultsView({ results, openArticle }) {
  return (
    <>
      <h1 className="wiki-h1">Search results</h1>
      <div className="wiki-results-list">
        {results.map((res, i) => (
          <div key={i} className="mb-6">
            <h3 onClick={()=>openArticle(res.path)} className="link text-[1.2em] font-bold">{res.path.split('/').pop().replace('.md', '').title()}</h3>
            <p className="text-[0.85em] leading-[1.6] line-clamp-2 mt-1">{res.snippet}</p>
          </div>
        ))}
      </div>
    </>
  );
}

function ArticleView({ article }) {
  if (!article) return null;
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h1 className="wiki-h1">{article.path.split('/').pop().replace('.md', '').toUpperCase()}</h1>
      <p className="sub-title">Path: {article.path}</p>
      <div className="prose prose-slate max-w-none text-[0.95em] leading-[1.7] wiki-article-body">
         <ReactMarkdown remarkPlugins={[remarkGfm]}>{article.content}</ReactMarkdown>
      </div>
    </motion.div>
  );
}

function SidebarSection({ title, children }) {
  return (
    <div className="sidebar-section">
      <h3 className="sidebar-title">{title}</h3>
      <div className="flex flex-col pl-1">{children}</div>
    </div>
  );
}

function SidebarLink({ label, icon, onClick, active }) {
  return (
    <div onClick={onClick} className={`sidebar-link flex items-center gap-2 ${active?'font-bold text-black border-l-2 border-[#3366cc] pl-1':''}`}>
      {icon} {label}
    </div>
  );
}

function WikiTab({ label, active, onClick }) {
  return (
    <div onClick={onClick} className={`tab ${active ? 'active' : ''}`}>{label}</div>
  );
}

// Prototype Title formatting
String.prototype.title = function() {
  return this.replace(/-/g, ' ').replace(/(^|\s)\S/g, function(t) { return t.toUpperCase(); });
}

export default App;
