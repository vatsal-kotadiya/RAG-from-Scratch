import { useEffect, useState } from 'react';
import { Upload, Trash2, RefreshCw } from 'lucide-react';
import { deleteDocument, listDocuments, reindexDocument, uploadDocument } from '../services/api';

const badgeColor = (s) =>
  s === 'READY' ? 'bg-green-100 text-green-800'
  : s === 'FAILED' ? 'bg-red-100 text-red-800'
  : 'bg-yellow-100 text-yellow-800';

export default function Documents() {
  const [docs, setDocs] = useState([]);
  const [msg, setMsg] = useState('');
  const [busy, setBusy] = useState(false);

  const refresh = () => listDocuments().then(setDocs).catch(() => setMsg('Backend unreachable.'));

  useEffect(() => {
    refresh();
    const t = setInterval(() => {
      // Re-poll while anything is still indexing.
      setDocs((prev) => {
        if (prev.some((d) => !['READY', 'FAILED'].includes(d.status))) refresh();
        return prev;
      });
    }, 3000);
    return () => clearInterval(t);
  }, []);

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setMsg('');
    try {
      await uploadDocument(file);
      setMsg(`Uploaded ${file.name} — indexing started.`);
      refresh();
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setBusy(false);
      e.target.value = '';
    }
  };

  const onDelete = async (id) => {
    if (!confirm('Delete document, its vectors and metadata?')) return;
    await deleteDocument(id);
    refresh();
  };

  const onReindex = async (id) => {
    await reindexDocument(id);
    refresh();
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Documents</h1>
        <label className="btn cursor-pointer">
          <Upload size={16} /> {busy ? 'Uploading…' : 'Upload Document'}
          <input type="file" className="hidden" accept=".pdf,.docx,.txt,.md" onChange={onUpload} disabled={busy} />
        </label>
      </div>
      {msg && <div className="card text-sm">{msg}</div>}
      {docs.length === 0 && <div className="card text-slate-500 text-sm">No documents yet. Upload a PDF, DOCX, TXT or Markdown file.</div>}
      {docs.map((d) => (
        <div key={d.id} className="card flex items-center justify-between">
          <div>
            <div className="font-medium">{d.filename}</div>
            <div className="text-xs text-slate-500">
              {(d.file_size / 1024).toFixed(1)} KB · {d.page_count} pages · {d.chunk_count} chunks · {d.created_at?.slice(0, 10)}
            </div>
            {d.status === 'FAILED' && <div className="text-xs text-red-600">{d.error_message}</div>}
          </div>
          <div className="flex items-center gap-2">
            <span className={`badge ${badgeColor(d.status)}`}>{d.status}</span>
            <button className="btn-ghost" title="Re-index" onClick={() => onReindex(d.id)}><RefreshCw size={14} /></button>
            <button className="btn-ghost" title="Delete" onClick={() => onDelete(d.id)}><Trash2 size={14} /></button>
          </div>
        </div>
      ))}
    </div>
  );
}
