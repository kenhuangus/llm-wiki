import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Search, Loader2, Plus, List, Database, Globe, Info, ExternalLink, HelpCircle, FileText, Settings, Users, BookOpen, Clock, AlertTriangle, ShieldCheck, Mail, ArrowLeft, ChevronRight, Upload, MessageCircle, Save } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [view, setView] = useState('Home'); // Home, SearchResults, Contents, Article, Logs, Upload, Backlinks, Talk, Edit, History
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [articles, setArticles] = useState([]);
  const [currentArticle, setCurrentArticle] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [backlinks, setBacklinks] = useState([]);
  const [logs, setLogs] = useState('');
  const [history, setHistory] = useState([]);
  const [selectedCommit, setSelectedCommit] = useState(null);
  
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

  const openArticle = async (path) => {
    setLoading(true);
    const normalizedPath = path.replace(/\\/g, '/');
    try {
      const resp = await axios.get(`${API_BASE}/article/${normalizedPath}`);
      if (resp.data.error) throw new Error(resp.data.error);
      setCurrentArticle(resp.data);
      setEditContent(resp.data.content);
      setView('Article');
    } catch (err) {
      setMessage({ type: 'error', text: `Failed to load ${path}` });
    } finally { setLoading(false); }
  };

  const handleSaveEdit = async () => {
    if (!currentArticle) return;
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/article/${currentArticle.path}`, { content: editContent });
      setMessage({ type: 'success', text: 'Article updated successfully!' });
      setCurrentArticle({ ...currentArticle, content: editContent });
      setView('Article');
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save changes.' });
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
      setMessage({ type: 'error', text: 'Search failed.' });
    } finally { setLoading(false); }
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
          <SidebarLink onClick={async ()=>{
            setLoading(true); setView('Contents');
            const r = await axios.get(`${API_BASE}/articles`);
            setArticles(r.data.articles || []);
            setLoading(false);
          }} active={view==='Contents'} icon={<FileText size={12}/>} label="Contents" />
          <SidebarLink icon={<Globe size={12}/>} label="Current events" />
          <SidebarLink onClick={()=>setView('About')} active={view==='About'} icon={<HelpCircle size={12}/>} label="About LLM Wiki" />
        </SidebarSection>

        <SidebarSection title="Contribute">
          <SidebarLink icon={<Plus size={12}/>} label="Community portal" />
          <SidebarLink onClick={async ()=>{
             setLoading(true); setView('Logs');
             const r = await axios.get(`${API_BASE}/logs`);
             setLogs(r.data.logs); setLoading(false);
          }} active={view==='Logs'} icon={<Users size={12}/>} label="Recent changes" />
          <SidebarLink onClick={()=>setView('Upload')} active={view==='Upload'} icon={<Settings size={12}/>} label="Upload file" />
        </SidebarSection>

        <SidebarSection title="Tools">
          <SidebarLink onClick={async ()=>{
             if(!currentArticle) return;
             setLoading(true); setView('Backlinks');
             const r = await axios.get(`${API_BASE}/backlinks/${currentArticle.path}`);
             setBacklinks(r.data.backlinks || []);
             setLoading(false);
          }} icon={<List size={12}/>} label="What links here" />
          <SidebarLink icon={<Mail size={12}/>} label="Contact us" />
        </SidebarSection>
      </aside>

      <div className="flex-1 flex flex-col min-w-0 bg-white border-l border-[#a2a9b1] -ml-[1px]">
        <header className="h-10 flex items-center justify-between px-4 bg-[#f6f6f6] border-b border-[#a2a9b1] text-[0.85em]">
          <div className="flex gap-4 text-[#54595d]">
            <span className="cursor-pointer hover:text-[#3366cc]">Log in</span>
            <span className="cursor-pointer hover:text-[#3366cc]">Create account</span>
          </div>
          <form onSubmit={handleSearch} className="flex">
            <input type="text" value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Search LLM Wiki" className="w-[200px] border border-[#a2a9b1] p-1 text-[0.9em] outline-none h-7" />
            <button type="submit" className="bg-[#f8f9fa] border border-[#a2a9b1] border-l-0 px-2 cursor-pointer hover:bg-[#eee] h-7 flex items-center"><Search size={14}/></button>
          </form>
        </header>

        <div className="flex items-end h-[41px] px-[2.5em] mt-1">
          <div className="flex gap-[2px]">
            <WikiTab label="Article" active={['Article','Edit','Backlinks','Talk','History'].includes(view)} onClick={()=>{if(currentArticle)setView('Article')}}/>
            <WikiTab label="Talk" active={view==='Talk'} onClick={()=>{if(currentArticle)setView('Talk')}}/>
          </div>
          <div className="flex-1 border-b border-[#a2a9b1] h-[33px]"></div>
          <div className="flex gap-[2px]">
            <WikiTab label="Read" active={view==='Article'} onClick={()=>{if(currentArticle)setView('Article')}}/>
            <WikiTab label="Edit" active={view==='Edit'} onClick={()=>{if(currentArticle)setView('Edit')}}/>
            <WikiTab label="View history" active={view==='History'} onClick={async ()=>{
              if(!currentArticle) return;
              setLoading(true); setView('History');
              try {
                const r = await axios.get(`${API_BASE}/history/${currentArticle.path}`);
                setHistory(r.data.history || []);
                setSelectedCommit(null);
              } catch(err) {
                setMessage({type: 'error', text: 'Failed to load history'});
              }
              setLoading(false);
            }}/>
          </div>
        </div>

        <main className="flex-1 p-[2.5em] pb-[10em] min-w-0 overflow-y-auto">
          {message && <div className="p-2 border mb-4 text-sm bg-blue-50 border-blue-200 flex justify-between items-center">{message.text} <button onClick={()=>setMessage(null)}>×</button></div>}

          {loading ? (
             <div className="flex flex-col items-center py-20 text-[#54595d]"><Loader2 size={48} className="animate-spin mb-4 text-[#3366cc]"/><span>Synchronizing graph...</span></div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div key={view} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.1 }}>
                {view === 'Home' && <HomeView />}
                {view === 'Contents' && <ContentsView articles={articles} openArticle={openArticle} />}
                {view === 'Article' && <ArticleView article={currentArticle} openArticle={openArticle} />}
                {view === 'Edit' && <EditView content={editContent} onChange={setEditContent} onSave={handleSaveEdit} />}
                {view === 'Talk' && <TalkView article={currentArticle} />}
                {view === 'History' && <HistoryView history={history} article={currentArticle} selectedCommit={selectedCommit} onSelectCommit={async (hash)=>{
                  setLoading(true);
                  try {
                    const r = await axios.get(`${API_BASE}/history/${currentArticle.path}/diff/${hash}`);
                    setSelectedCommit({hash, content: r.data.content});
                  } catch(err) {
                    setMessage({type: 'error', text: 'Failed to load commit'});
                  }
                  setLoading(false);
                }} />}
                {view === 'Logs' && <LogsView logs={logs} />}
                {view === 'Upload' && <UploadView onUpload={async (e)=>{
                   const f = e.target.files[0]; if(!f) return;
                   const fd = new FormData(); fd.append('file', f);
                   setLoading(true); await axios.post(`${API_BASE}/upload`, fd);
                   setLoading(false); setMessage({text: `Uploaded ${f.name}`});
                }} />}
                {view === 'Backlinks' && <BacklinksView backlinks={backlinks} original={currentArticle} openArticle={openArticle} />}
                {view === 'SearchResults' && <SearchResultsView results={results} openArticle={openArticle} />}
                {view === 'About' && <AboutView />}
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
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[45%] font-bold">Conflicts</div><div className="w-[55%] font-bold text-red-600">{stats.conflictCount} Flagged</div></div>
          <div className="flex border-t border-[#eaecf0] py-1 px-2"><div className="w-[45%] font-bold">Confidence</div><div className="w-[55%]">{stats.avgConfidence.toFixed(2)} Avg</div></div>
          
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200">
             <div className="flex gap-2 text-yellow-800 font-bold mb-1"><ShieldCheck size={14}/> SYSTEM STATUS</div>
             <p className="text-[0.9em]"><b>Ken-Mac (26B):</b> ONLINE</p>
             <p className="text-slate-500 text-[0.8em]">3-Retry Sticky Logic Active.</p>
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
      <div className="border border-[#a2a9b1] p-8 bg-[#f8f9fa] shadow-sm">
        <h2 className="text-[1.8em] mb-4 font-serif border-b border-[#a2a9b1] pb-2">Welcome to LLM Wiki</h2>
        <p className="leading-[1.8]">This is an <b>Agent-Maintained Knowledge Base</b>. Our 26B-parameter primary node autonomously fetches, normalizes, and integrates latest findings from arXiv, GitHub, and NVD into this repository.</p>
      </div>
    </>
  );
}

function EditView({ content, onChange, onSave }) {
  return (
    <>
      <h1 className="wiki-h1 font-serif">Editing Current Page</h1>
      <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-4 shadow-inner">
        <textarea 
          value={content} 
          onChange={(e)=>onChange(e.target.value)} 
          className="w-full h-[500px] font-mono text-[0.95em] p-4 border border-[#a2a9b1] outline-none shadow-sm focus:border-[#3366cc]"
          placeholder="Enter markdown..."
        />
        <div className="mt-4 flex gap-4">
          <button onClick={onSave} className="bg-[#3366cc] text-white px-6 py-2 flex items-center gap-2 font-bold hover:bg-[#2a52a2]"><Save size={16}/> Save changes</button>
          <span className="text-[0.8em] text-[#54595d] flex items-center italic">Your edit will be saved instantly to the local markdown file.</span>
        </div>
      </div>
    </>
  );
}

function ArticleView({ article, openArticle }) {
  if (!article) return null;
  return (
    <>
      <h1 className="wiki-h1">{article.path.replace('.md','').replace(/-/g,' ').toUpperCase()}</h1>
      <div className="wiki-article-body prose prose-slate max-w-none text-[1.1em] leading-[1.8]">
         <ReactMarkdown 
           remarkPlugins={[remarkGfm]}
           components={{
             p: ({children}) => {
                const newChildren = React.Children.map(children, child => {
                   if(typeof child === 'string') {
                      const regex = /\[\[(.*?)\]\]/g;
                      const parts = child.split(regex);
                      return parts.map((part, i) => {
                         if(i % 2 === 1) return <span key={part} onClick={()=>openArticle(part+'.md')} className="link font-bold">{part}</span>;
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
    </>
  );
}

function ContentsView({ articles, openArticle }) {
  return (
    <>
      <h1 className="wiki-h1">All Indexed Articles</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-4">
        {articles.map((a, i) => (
           <div key={i} onClick={()=>openArticle(a.path)} className="link group flex items-center gap-2">
              <ChevronRight size={14} className="text-[#a2a9b1] group-hover:text-[#3366cc]"/> {a.title}
           </div>
        ))}
      </div>
    </>
  );
}

function TalkView({ article }) {
  return (
    <>
      <h1 className="wiki-h1">Discussion: {article?.path}</h1>
      <div className="bg-[#fffffa] border border-[#f0f0e0] p-6 italic prose prose-slate">
        <div className="flex gap-4 items-start mb-4">
           <div className="bg-[#3366cc] text-white p-2 rounded-full"><Users size={20}/></div>
           <div><span className="font-bold block text-sm">Automated Analyst</span>
           <p className="mt-1">Reconciled findings between 2604.0xxxx and current GitHub release. Claims verified with 0.85 confidence.</p></div>
        </div>
      </div>
    </>
  );
}

function LogsView({ logs }) {
  return (
    <>
      <h1 className="wiki-h1">Recent System Changes</h1>
      <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-4 font-mono text-[0.85em] whitespace-pre-wrap">{logs}</div>
    </>
  );
}

function UploadView({ onUpload }) {
  return (
    <>
      <h1 className="wiki-h1">Upload Source</h1>
      <div className="p-20 border-2 border-dashed border-[#a2a9b1] flex flex-col items-center justify-center bg-[#f8f9fa] hover:border-[#3366cc]">
         <Upload size={48} className="text-[#a2a9b1] mb-4"/>
         <label className="bg-[#3366cc] text-white px-8 py-3 cursor-pointer font-bold">SELECT FILE<input type="file" className="hidden" onChange={onUpload}/></label>
      </div>
    </>
  );
}

function BacklinksView({ backlinks, original, openArticle }) {
  return (
    <>
      <h1 className="wiki-h1">Pages linking to "{original?.path}"</h1>
      <div className="mt-4 flex flex-col gap-2">
        {backlinks.map((b, i) => (
          <div key={i} onClick={()=>openArticle(b.path)} className="link">{b.path}</div>
        ))}
      </div>
    </>
  );
}

function SearchResultsView({ results, openArticle }) {
  return (
    <>
      <h1 className="wiki-h1">Search Results</h1>
      {results.map((r, i) => (
         <div key={i} className="mb-6 pb-6 border-b border-slate-100">
            <h3 onClick={()=>openArticle(r.path)} className="link text-[1.25em] font-serif">{r.path}</h3>
            <p className="text-[0.9em] mt-1 text-[#54595d]">{r.snippet}...</p>
         </div>
      ))}
    </>
  );
}

function AboutView() {
  return (
    <>
      <h1 className="wiki-h1">Architecture</h1>
      <p className="leading-[1.8] max-w-2xl">This is a local-first, agent-maintained Wikipedia dashboard. It solves the RAG persistence problem by building a compounding markdown graph. Built with FastAPI, React, and Dual-Node LAN LLMs (Ken-Mac 26B + Local 8B).</p>
    </>
  );
}

function HistoryView({ history, article, selectedCommit, onSelectCommit }) {
  if (!article) return null;
  
  return (
    <>
      <h1 className="wiki-h1">Revision history of "{article.path}"</h1>
      
      {history.length === 0 ? (
        <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-8 text-center text-[#54595d]">
          <Clock size={48} className="mx-auto mb-4 text-[#a2a9b1]"/>
          <p>No git history available for this file.</p>
          <p className="text-sm mt-2">The file may not be committed yet or git is not initialized.</p>
        </div>
      ) : (
        <div className="mt-4">
          <div className="bg-[#f8f9fa] border border-[#a2a9b1] mb-4 p-3 text-sm">
            <p><b>{history.length}</b> revision(s) found. Click on a revision to view its content.</p>
          </div>
          
          <div className="border border-[#a2a9b1]">
            {history.map((commit, i) => (
              <div 
                key={commit.hash} 
                className={`border-b border-[#a2a9b1] p-4 hover:bg-[#f8f9fa] cursor-pointer transition-colors ${selectedCommit?.hash === commit.hash ? 'bg-blue-50' : ''}`}
                onClick={() => onSelectCommit(commit.hash)}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 bg-[#3366cc] text-white rounded-full w-8 h-8 flex items-center justify-center font-bold text-sm">
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-[#3366cc]">{commit.author}</span>
                      <span className="text-[#54595d] text-sm">({commit.email})</span>
                    </div>
                    <div className="text-sm text-[#54595d] mb-2">
                      <Clock size={12} className="inline mr-1"/> {new Date(commit.date).toLocaleString()}
                    </div>
                    <div className="text-[0.95em]">{commit.message}</div>
                    <div className="text-xs text-[#54595d] mt-2 font-mono">
                      {commit.hash.substring(0, 8)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {selectedCommit && (
            <div className="mt-6">
              <h2 className="text-[1.3em] font-serif mb-3 border-b border-[#a2a9b1] pb-2">
                Content at commit {selectedCommit.hash.substring(0, 8)}
              </h2>
              <div className="bg-[#f8f9fa] border border-[#a2a9b1] p-4 font-mono text-[0.85em] whitespace-pre-wrap max-h-[600px] overflow-y-auto">
                {selectedCommit.content}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
}

// Layout Components
function SidebarSection({ title, children }) {
  return (
    <div className="mb-6">
      <h3 className="text-[0.75em] text-[#54595d] border-b border-[#a2a9b1] mb-2 font-bold uppercase">{title}</h3>
      <div className="flex flex-col gap-1">{children}</div>
    </div>
  );
}

function SidebarLink({ label, icon, onClick, active }) {
  return (
    <div onClick={onClick} className={`flex items-center gap-2 text-[0.85em] cursor-pointer hover:underline ${active ? 'text-black font-bold border-l-2 border-[#3366cc] pl-2 -ml-2' : 'text-[#3366cc]'}`}>
      {icon} <span>{label}</span>
    </div>
  );
}

function WikiTab({ label, active, onClick }) {
  return (
    <div onClick={onClick} className={`px-4 py-2 text-[0.85em] cursor-pointer border border-transparent border-b-0 -mb-[1px] transition-all ${active ? 'bg-white border-[#a2a9b1] text-black font-bold z-20' : 'text-[#3366cc] hover:bg-[#f8f9fa]'}`}>
      {label}
    </div>
  );
}

export default App;
