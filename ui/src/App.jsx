import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Search, Loader2, Plus, List, Database, Globe, Info, ExternalLink, HelpCircle, FileText, Settings, Users, BookOpen, Clock, AlertTriangle, ShieldCheck, Mail, ArrowLeft, ChevronRight, Upload, MessageCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [view, setView] = useState('Home'); // Home, SearchResults, Contents, Article, Logs, Upload, Backlinks, Talk
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [articles, setArticles] = useState([]);
  const [currentArticle, setCurrentArticle] = useState(null);
  const [backlinks, setBacklinks] = useState([]);
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

  const fetchBacklinks = async () => {
    if (!currentArticle) return;
    setLoading(true);
    setView('Backlinks');
    try {
      const resp = await axios.get(`${API_BASE}/backlinks/${currentArticle.path}`);
      setBacklinks(resp.data.backlinks || []);
    } catch (err) { setMessage({ type: 'error', text: 'Failed to fetch backlinks.' });
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
      <aside className="w-[176px] flex-shrink-0 bg-[#f6f6f6] border-r border-[#a2a9b1] px-2 py-4 shadow-sm z-10">
        <div className="flex flex-col items-center mb-6 cursor-pointer" onClick={()=>setView('Home')}>
          <Database className="text-[#3366cc]" size={64} />
          <span className="text-[1.2em] font-serif mt-2 tracking-tight">LLM WIKI</span>
        </div>

        <SidebarSection title="Navigation">
          <SidebarLink onClick={()=>setView('Home')} active={view==='Home'} icon={<Database size={12}/>} label="Main page" />
          <SidebarLink onClick={fetchAllContents} active={view==='Contents'} icon={<FileText size={12}/>} label="Contents" />
          <SidebarLink onClick={async ()=>{
             // Filter articles for "newsletters"
             setLoading(true);
             setView('Contents');
             const resp = await axios.get(`${API_BASE}/articles`);
             const newsletters = (resp.data.articles || []).filter(a => a.path.includes('newsletter'));
             setArticles(newsletters);
             setLoading(false);
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
            <textarea value={ingestUrls} onChange={(e)=>setIngestUrls(e.target.value)} className="w-full h-24 text-[10px] p-1 border border-[#ccc] mb-2 font-mono" placeholder="Enter URLs..."/>
            <button disabled={ingesting} onClick={handleIngest} className="w-full bg-[#f8f9fa] border border-[#a2a9b1] p-1 text-[#3366cc] cursor-pointer hover:bg-[#eee] transition-colors">{ingesting?'Queueing...':'Ingest Sources'}</button>
          </div>
          <SidebarLink onClick={fetchBacklinks} icon={<List size={12}/>} label="What links here" />
          <SidebarLink icon={<Mail size={12}/>} label="Contact us" />
        </SidebarSection>
      </aside>

      <div className="flex-1 flex flex-col min-w-0 bg-white border-l border-[#a2a9b1] -ml-[1px]">
        <header className="h-10 flex items-center justify-between px-4 bg-[#f6f6f6] border-b border-[#a2a9b1] text-[0.85em]">
          <div className="flex gap-4 text-[#54595d]">
            <span className="cursor-pointer hover:text-[#3366cc]">Log in</span>
            <span className="cursor-pointer hover:text-[#3366cc]">Create account</span>
          </div>
          <div className="flex items-center gap-2">
            <form onSubmit={handleSearch} className="flex">
              <input type="text" value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Search LLM Wiki" className="w-[200px] border border-[#a2a9b1] p-1 text-[0.9em] outline-none h-7" />
              <button type="submit" className="bg-[#f8f9fa] border border-[#a2a9b1] border-l-0 px-2 cursor-pointer hover:bg-[#eee] h-7 flex items-center"><Search size={14} className="text-[#54595d]"/></button>
            </form>
          </div>
        </header>

        <div className="flex items-end h-[41px] px-[2.5em] mt-1">
          <div className="flex gap-[2px]">
            <WikiTab label="Article" active={['Article','Home','SearchResults','About','Upload','Logs','Contents','Backlinks'].includes(view)} onClick={()=>{
               if(currentArticle && view === 'Talk') setView('Article');
            }}/>
            <WikiTab label="Talk" active={view==='Talk'} onClick={()=>{
               if(currentArticle) setView('Talk');
            }}/>
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
            <div className={`p-2 border mb-4 text-sm flex gap-2 items-center rounded-sm ${message.type==='error' ? 'bg-red-50 border-red-200 text-red-700':'bg-green-50 border-green-200 text-green-700'}`}>
              <Info size={14}/> {message.text}
            </div>
          )}

          {loading ? (
             <div className="flex flex-col items-center py-20 text-[#54595d]"><Loader2 size={48} className="animate-spin mb-4 text-[#3366cc]"/><span>Compiling knowledge graph...</span></div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div key={view} initial={{ opacity: 0, x: 5 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -5 }} transition={{ duration: 0.15 }}>
                {view === 'Home' && <HomeView />}
                {view === 'SearchResults' && <SearchResultsView results={results} openArticle={openArticle} />}
                {view === 'Contents' && <ContentsView articles={articles} openArticle={openArticle} />}
                {view === 'Article' && <ArticleView article={currentArticle} openArticle={openArticle} />}
                {view === 'Logs' && <LogsView logs={logs} />}
                {view === 'About' && <AboutView />}
                {view === 'Upload' && <UploadView onUpload={handleFileUpload} />}
                {view === 'Backlinks' && <BacklinksView backlinks={backlinks} original={currentArticle} openArticle={openArticle} />}
                {view === 'Talk' && <TalkView article={currentArticle} />}
              </motion.div>
            </AnimatePresence>
          )}
        </main>
      </div>

      <aside className="w-[250px] flex-shrink-0 bg-white p-4 border-l border-[#a2a9b1]">
        <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-1 text-[0.8em] shadow-sm">
          <div className="text-center font-bold bg-[#eaecf0] py-2 mb-2 border-b border-[#a2a9b1]">Wiki Statistics</div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[45%] font-bold">Total Pages</div><div className="w-[55%]">{stats.pageCount}</div></div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[45%] font-bold">Monitors</div><div className="w-[55%]">{stats.monitorCount} Active</div></div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[45%] font-bold">Conflicts</div><div className="w-[55%] text-red-600 font-bold">{stats.conflictCount} Flagged</div></div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[45%] font-bold">Confidence</div><div className="w-[55%]">{stats.avgConfidence.toFixed(2)} Avg</div></div>
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-sm">
            <div className="flex gap-2 text-yellow-800 font-bold mb-2 items-center"><ShieldCheck size={14}/> PROVANCE AUTH</div>
            <span className="text-[0.9em] leading-[1.4] text-yellow-900">Every claim in this vault is cryptographically anchored to its local source document.</span>
          </div>
          <div className="mt-2 p-3 bg-[#e8f0ff] border border-[#b8c9f9] rounded-sm">
            <div className="flex gap-2 text-[#3366cc] font-bold mb-1 items-center"><Clock size={14}/> SYSTEM UPTIME</div>
            <span className="text-[0.9em] text-[#2a52a2]">Pipeline active. 2nd LAN node (Ken-Mac) standby.</span>
          </div>
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
      <p className="sub-title">From LLM Wiki, the free autonomous encyclopedia</p>
      <div className="border border-[#a2a9b1] p-8 bg-[#f8f9fa] shadow-sm rounded-sm">
        <h2 className="text-[1.8em] mb-6 font-serif border-b border-[#a2a9b1] pb-2">Welcome to the LLM Wiki</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-[0.95em] leading-[1.6]">
          <div>
            <h3 className="font-bold flex gap-2 items-center mb-2"><BookOpen size={18} className="text-[#3366cc]"/> The Compounding Brain</h3>
            <p>Unlike standard RAG systems, this wiki accumulates knowledge. Every ingestion strengthens or challenges existing claims, creating a persistent artifact that grows smarter over time.</p>
          </div>
          <div>
            <h3 className="font-bold flex gap-2 items-center mb-2"><Globe size={18} className="text-[#3366cc]"/> Autonomous Ingestion</h3>
            <p>The system actively monitors arXiv, GitHub, and NVD for latest AI research and security vulnerabilities. New data is automatically extracted and synthesized into these pages.</p>
          </div>
        </div>
        <div className="mt-8 pt-6 border-t border-[#a2a9b1] text-center text-[#54595d] italic">
          "The tedious part of maintaining a knowledge base is the bookkeeping... The LLM handles that."
        </div>
      </div>
    </>
  );
}

function ContentsView({ articles, openArticle }) {
  const groups = articles.reduce((acc, art) => {
     const cat = art.path.split('/')[0] || 'Uncategorized';
     if(!acc[cat]) acc[cat] = [];
     acc[cat].push(art);
     return acc;
  }, {});

  return (
    <>
      <h1 className="wiki-h1">Contents</h1>
      <p className="sub-title">Structured overview of the knowledge graph</p>
      {Object.keys(groups).map(cat => (
        <div key={cat} className="mb-8">
           <h3 className="text-[1.2em] font-serif border-b border-[#eaecf0] mb-4 pb-1 capitalize">{cat}</h3>
           <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
             {groups[cat].map((art, i) => (
                <div key={i} onClick={()=>openArticle(art.path)} className="link flex items-center gap-2 group">
                   <ChevronRight size={12} className="text-[#a2a9b1] group-hover:text-[#3366cc]"/> {art.title}
                </div>
             ))}
           </div>
        </div>
      ))}
    </>
  );
}

function LogsView({ logs }) {
  return (
    <>
      <h1 className="wiki-h1">Recent changes</h1>
      <p className="sub-title">Live operational audit trail of the autonomous agent</p>
      <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-4 font-mono text-[0.8em] whitespace-pre-wrap leading-[1.6] shadow-inner max-h-[600px] overflow-y-auto">
        {logs}
      </div>
    </>
  );
}

function UploadView({ onUpload }) {
  return (
    <>
      <h1 className="wiki-h1">Upload file</h1>
      <p className="sub-title">Ingest local documents into the semantic pipeline</p>
      <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-20 flex flex-col items-center justify-center border-dashed border-2 rounded-sm group hover:border-[#3366cc] transition-colors">
         <Upload size={64} className="text-[#a2a9b1] mb-6 group-hover:text-[#3366cc]"/>
         <label className="bg-[#3366cc] text-white px-6 py-3 cursor-pointer rounded-sm hover:bg-[#2a52a2] font-bold shadow-md">
            CHOOSE LOCAL SOURCE
            <input type="file" className="hidden" onChange={onUpload} />
         </label>
         <p className="text-[0.9em] mt-6 text-slate-500 text-center max-w-sm">Files uploaded here are instantly hashed, normalized, and queued for LLM extraction and graph integration.</p>
      </div>
    </>
  );
}

function BacklinksView({ backlinks, original, openArticle }) {
  return (
    <>
      <h1 className="wiki-h1">Pages that link to "{original?.path.split('/').pop().replace('.md','')}"</h1>
      <p className="sub-title">The following pages have intentional references to this entity</p>
      <div className="bg-[#f8f9fa] border border-[#a2a9b1] px-4 py-2 mt-4 shadow-sm">
        {backlinks.length === 0 ? (
          <p className="p-4 text-slate-500 italic">No inbound links found for this article.</p>
        ) : (
          <ul className="list-disc pl-5 py-2">
            {backlinks.map((link, i) => (
              <li key={i} className="mb-1">
                <span onClick={()=>openArticle(link.path)} className="link">{link.path}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}

function TalkView({ article }) {
  return (
    <>
      <h1 className="wiki-h1">Talk: {article?.path.split('/').pop().replace('.md','')}</h1>
      <p className="sub-title">Synthesis discussion and automated claim resolution</p>
      <div className="prose prose-slate mt-6 bg-[#fffffa] border border-[#f0f0e0] p-6 shadow-sm quotes italic">
         <div className="flex gap-4 items-start mb-6">
           <div className="bg-[#3366cc] text-white p-2 rounded-full"><Users size={20}/></div>
           <div>
             <span className="font-bold block text-sm">System Auditor Log</span>
             <p className="text-[0.9em] mt-1">This article was recently updated based on arXiv:2403.xxxxx. Contradiction detected in 'Llama 4' parameter count. Reverting to Tier 1 source claims (verified).</p>
           </div>
         </div>
         <div className="flex gap-4 items-start border-t border-[#f0f0e0] pt-4">
           <div className="bg-slate-500 text-white p-2 rounded-full"><MessageCircle size={20}/></div>
           <div>
             <span className="font-bold block text-sm">Agent Discussion</span>
             <p className="text-[0.9em] mt-1">I should cross-reference this with the GitHub repository releases. The paper mentions v1.0 but the repo shows v1.2 with performance regressions.</p>
           </div>
         </div>
      </div>
    </>
  );
}

function AboutView() {
  return (
    <>
      <h1 className="wiki-h1">About LLM Wiki</h1>
      <p className="sub-title">A production-grade Agentic Knowledge Graph</p>
      <div className="prose prose-slate mt-8 text-[1.1em] leading-[1.8] max-w-3xl">
         <p>The <b>LLM Wiki</b> project is a implementation of a local-first, agent-maintained knowledge base. It solves the massive bookkeeping burden inherent in professional knowledge management by using LLMs for summarization, cross-referencing, and graph consistency.</p>
         <div className="bg-slate-50 p-6 border-l-4 border-[#3366cc] mt-8">
            <h4 className="mt-0">Open Source & Local-First</h4>
            <p>Our code is fully transparent and designed to run on consumer hardware or LAN servers. No telemetry. No external data leaks.</p>
            <a href="https://github.com/kenhuangus/llm-wiki" className="link font-bold">View Source on GitHub →</a>
         </div>
      </div>
    </>
  );
}

function SearchResultsView({ results, openArticle }) {
  return (
    <>
      <h1 className="wiki-h1">Search results for your query</h1>
      <div className="wiki-results-list">
        {results.length === 0 ? (
           <div className="p-20 text-center border bg-slate-50 text-slate-400">No matching entities found in the graph.</div>
        ) : (
          results.map((res, i) => (
            <div key={i} className="mb-8 p-3 hover:bg-slate-50 rounded-sm transition-colors border-b border-slate-100 last:border-0 pb-6">
              <h3 onClick={()=>openArticle(res.path)} className="link text-[1.3em] font-serif">{res.path.split('/').pop().replace('.md', '').title()}</h3>
              <p className="text-[0.9em] leading-[1.6] text-[#54595d] mt-2 italic">Result relevance: {(res.score * 100).toFixed(1)}% match</p>
              <p className="text-[0.95em] leading-[1.7] mt-3">{res.snippet}...</p>
            </div>
          ))
        )}
      </div>
    </>
  );
}

function ArticleView({ article, openArticle }) {
  if (!article) return null;
  return (
    <div className="max-w-none">
      <h1 className="wiki-h1">{article.path.split('/').pop().replace('.md', '').toUpperCase().replace(/-/g,' ')}</h1>
      <p className="sub-title">Path: {article.path}</p>
      
      <div className="prose prose-slate max-w-none text-[1.05em] leading-[1.8] wiki-article-body article-render">
         <ReactMarkdown 
           remarkPlugins={[remarkGfm]} 
           components={{
             p: ({children}) => {
                const newChildren = React.Children.map(children, child => {
                   if(typeof child === 'string') {
                      const regex = /\[\[(.*?)\]\]/g;
                      const parts = child.split(regex);
                      return parts.map((part, i) => {
                         if(i % 2 === 1) return <span key={part} onClick={()=>openArticle(part+'.md')} className="link font-bold cursor-pointer">{part}</span>;
                         return part;
                      });
                   }
                   return child;
                });
                return <p>{newChildren}</p>
             }
           }}
          >
            {article.content}
          </ReactMarkdown>
      </div>
    </div>
  );
}

// Layout Components
function SidebarSection({ title, children }) {
  return (
    <div className="mb-6">
      <h3 className="text-[0.75em] text-[#54595d] border-b border-[#a2a9b1] mb-2 font-bold uppercase tracking-wider">{title}</h3>
      <div className="flex flex-col gap-1">{children}</div>
    </div>
  );
}

function SidebarLink({ label, icon, onClick, active }) {
  return (
    <div 
      onClick={onClick} 
      className={`flex items-center gap-2 text-[0.85em] cursor-pointer hover:underline transition-all py-[1px]
        ${active ? 'text-black font-bold border-l-2 border-[#3366cc] pl-2 -ml-2' : 'text-[#3366cc]'}`}
    >
      {icon} <span>{label}</span>
    </div>
  );
}

function WikiTab({ label, active, onClick }) {
  return (
    <div 
      onClick={onClick} 
      className={`px-4 py-2 text-[0.85em] cursor-pointer border border-transparent border-b-0 -mb-[1px] transition-all
        ${active ? 'bg-white border-[#a2a9b1] text-black font-bold z-20' : 'text-[#3366cc] hover:bg-[#f8f9fa]'}`}
    >
      {label}
    </div>
  );
}

// Prototype Title formatting
String.prototype.title = function() {
  return this.replace(/-/g, ' ').replace(/(^|\s)\S/g, function(t) { return t.toUpperCase(); });
}

export default App;
