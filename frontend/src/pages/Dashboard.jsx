import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listDocuments, listEvalRuns, listSessions } from '../services/api';

export default function Dashboard() {
  const [docs, setDocs] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [runs, setRuns] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([listDocuments(), listSessions(), listEvalRuns()])
      .then(([d, s, r]) => { setDocs(d); setSessions(s); setRuns(r); })
      .catch(() => setError('Backend unreachable. Start it with uvicorn first.'));
  }, []);

  const chunks = docs.reduce((n, d) => n + (d.chunk_count || 0), 0);
  const last = runs[0]?.metrics;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold">RAG Intelligence Dashboard</h1>
      {error && <div className="card text-red-600">{error}</div>}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          ['Documents', docs.length],
          ['Indexed Chunks', chunks],
          ['Questions', sessions.length],
          ['Eval Runs', runs.length],
        ].map(([label, v]) => (
          <div key={label} className="card text-center">
            <div className="text-3xl font-bold text-indigo-600">{v}</div>
            <div className="text-sm text-slate-500">{label}</div>
          </div>
        ))}
      </div>
      {last && (
        <div className="card">
          <h2 className="font-semibold mb-3">Latest Retrieval Quality (real eval run)</h2>
          <div className="flex gap-6 text-sm">
            {Object.entries(last.retrieval || {}).map(([k, v]) => (
              <div key={k}><span className="text-slate-500">{k}:</span> <b>{v}</b></div>
            ))}
          </div>
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="card">
          <h2 className="font-semibold mb-2">Recent Documents</h2>
          {docs.length === 0 && <p className="text-sm text-slate-500">No documents yet. <Link className="text-indigo-600" to="/documents">Upload one</Link>.</p>}
          {docs.slice(0, 5).map((d) => (
            <div key={d.id} className="text-sm py-1 border-b border-slate-100 last:border-0">
              {d.filename} <span className="text-slate-400">· {d.chunk_count} chunks · {d.status}</span>
            </div>
          ))}
        </div>
        <div className="card">
          <h2 className="font-semibold mb-2">Recent Conversations</h2>
          {sessions.length === 0 && <p className="text-sm text-slate-500">No questions asked yet.</p>}
          {sessions.slice(0, 5).map((s) => (
            <div key={s.id} className="text-sm py-1 border-b border-slate-100 last:border-0">{s.title}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
