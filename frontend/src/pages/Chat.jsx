import { useEffect, useState } from 'react';
import { Send } from 'lucide-react';
import { askQuestion, deleteSession, getSession, listDocuments, listSessions } from '../services/api';

export default function Chat() {
  const [docs, setDocs] = useState([]);
  const [selected, setSelected] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [showCtx, setShowCtx] = useState(false);

  useEffect(() => {
    listDocuments().then(setDocs).catch(() => setError('Backend unreachable.'));
    listSessions().then(setSessions).catch(() => {});
  }, []);

  const toggle = (id) =>
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));

  const ask = async (e) => {
    e?.preventDefault();
    if (!question.trim() || loading) return;
    setLoading(true);
    setError('');
    setAnswer(null);
    try {
      const res = await askQuestion({ question, document_ids: selected, top_k: 5, session_id: sessionId });
      setAnswer(res);
      setSessionId(res.session_id);
      listSessions().then(setSessions).catch(() => {});
    } catch (err) {
      setError(err.response?.data?.detail || 'Question failed.');
    } finally {
      setLoading(false);
    }
  };

  const newChat = async () => {
    if (sessionId) { try { await deleteSession(sessionId); } catch {} }
    setSessionId(null);
    setAnswer(null);
    setQuestion('');
    setShowCtx(false);
    listSessions().then(setSessions).catch(() => {});
  };

  const openSession = async (id) => {
    const data = await getSession(id);
    setSessionId(id);
    const last = [...data.messages].reverse().find((m) => m.role === 'assistant');
    setAnswer(last ? { answer: last.content, sources: [], retrieval_metadata: null } : null);
  };

  return (
    <div className="flex gap-4">
      <aside className="w-64 shrink-0 flex flex-col gap-3">
        <div className="card">
          <h3 className="font-semibold text-sm mb-2">Documents</h3>
          {docs.length === 0 && <p className="text-xs text-slate-500">Upload documents first.</p>}
          {docs.filter((d) => d.status === 'READY').map((d) => (
            <label key={d.id} className="flex items-center gap-2 text-sm py-1 cursor-pointer">
              <input type="checkbox" checked={selected.includes(d.id)} onChange={() => toggle(d.id)} />
              <span className="truncate">{d.filename}</span>
            </label>
          ))}
        </div>
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-sm">History</h3>
            <button className="btn-ghost text-xs" onClick={newChat}>New</button>
          </div>
          {sessions.map((s) => (
            <button key={s.id} onClick={() => openSession(s.id)} className="block w-full text-left text-xs py-1 truncate hover:text-indigo-600">
              {s.title}
            </button>
          ))}
        </div>
      </aside>

      <div className="flex-1 flex flex-col gap-4">
        <h1 className="text-2xl font-bold">RAG Assistant</h1>
        {error && <div className="card text-red-600 text-sm">{error}</div>}
        {loading && <div className="card text-sm text-slate-500">Retrieving chunks → building context → generating…</div>}
        {answer && (
          <div className="card flex flex-col gap-3">
            <div className="text-sm whitespace-pre-wrap">{answer.answer}</div>
            {answer.provider && <div className="text-xs text-slate-400">via {answer.provider}</div>}
            {answer.sources?.length > 0 && (
              <div>
                <h3 className="font-semibold text-sm mb-1">Sources</h3>
                {answer.sources.map((s, i) => (
                  <div key={i} className="text-xs border border-slate-200 rounded-lg p-2 mb-1">
                    <b>Rank {i + 1}</b> · {s.filename}
                    {s.page != null && <> · Page {s.page}</>} · Similarity {s.score?.toFixed(3)}
                    <div className="text-slate-500 mt-1">{s.text_preview}</div>
                  </div>
                ))}
              </div>
            )}
            {answer.retrieval_metadata && (
              <button className="text-xs text-indigo-600 text-left" onClick={() => setShowCtx((v) => !v)}>
                {showCtx ? 'Hide' : 'Show'} retrieval details
              </button>
            )}
            {showCtx && answer.retrieval_metadata && (
              <pre className="text-xs bg-slate-100 rounded-lg p-2 overflow-auto">
                {JSON.stringify(answer.retrieval_metadata, null, 2)}
              </pre>
            )}
          </div>
        )}
        <form onSubmit={ask} className="flex gap-2">
          <input
            className="input" placeholder="Ask a question… (Enter to send)"
            value={question} onChange={(e) => setQuestion(e.target.value)}
          />
          <button className="btn" type="submit" disabled={loading}><Send size={16} /></button>
        </form>
      </div>
    </div>
  );
}
