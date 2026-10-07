import { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getEvalRun, listEvalRuns, runEvaluation } from '../services/api';

export default function Evaluation() {
  const [runs, setRuns] = useState([]);
  const [current, setCurrent] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const refresh = () => listEvalRuns().then((r) => { setRuns(r); if (r[0]) setCurrent(r[0]); });

  useEffect(() => { refresh().catch(() => setError('Backend unreachable.')); }, []);

  const run = async () => {
    setBusy(true);
    setError('');
    try {
      const res = await runEvaluation({ dataset_name: 'seed', top_k: 5, include_baseline: true });
      setCurrent(res);
      refresh();
    } catch (err) {
      setError(err.response?.data?.detail || 'Evaluation failed. Index company_policy.txt first.');
    } finally {
      setBusy(false);
    }
  };

  const retrievalData = current
    ? Object.entries(current.metrics.retrieval || {}).map(([name, value]) => ({ name, value }))
    : [];
  const compareData = current
    ? [
        { name: 'RAG faithfulness', value: current.metrics.generation_rag?.faithfulness ?? 0 },
        { name: 'Baseline faithfulness', value: current.metrics.generation_baseline_llm_only?.faithfulness ?? 0 },
      ]
    : [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Evaluation</h1>
        <button className="btn" onClick={run} disabled={busy}>{busy ? 'Evaluating…' : 'Run Evaluation'}</button>
      </div>
      {error && <div className="card text-red-600 text-sm">{error}</div>}
      {!current && <div className="card text-sm text-slate-500">No evaluation runs yet. Every metric shown here comes from a real run — nothing is fabricated.</div>}
      {current && (
        <>
          <div className="card">
            <h2 className="font-semibold mb-1">Run {current.id}</h2>
            <div className="text-xs text-slate-500 mb-3">
              {current.dataset_name} · {current.model_name} · {current.embedding_model} · top_k={current.top_k} · {current.metrics.num_questions} questions
            </div>
            <h3 className="text-sm font-semibold mb-2">Retrieval Metrics</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={retrievalData}>
                <XAxis dataKey="name" fontSize={12} />
                <YAxis domain={[0, 1]} fontSize={12} />
                <Tooltip />
                <Bar dataKey="value" fill="#4f46e5" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold mb-2">RAG vs LLM-Only Baseline</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={compareData}>
                <XAxis dataKey="name" fontSize={12} />
                <YAxis domain={[0, 1]} fontSize={12} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
            <div className="text-xs text-slate-500 mt-2">
              Hallucination rate: {current.metrics.generation_rag?.hallucination_rate} ·
              Answer relevance: {current.metrics.generation_rag?.answer_relevance} ·
              Context relevance: {current.metrics.generation_rag?.context_relevance}
              {current.metrics.abstention && (
                <> · Abstention accuracy: {current.metrics.abstention.abstention_accuracy} ({current.metrics.abstention.correctly_abstained}/{current.metrics.abstention.unanswerable_questions})</>
              )}
            </div>
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold mb-2">Past Runs</h3>
            {runs.map((r) => (
              <button key={r.id} onClick={() => getEvalRun(r.id).then(setCurrent)} className="block text-xs py-1 hover:text-indigo-600">
                {r.id} · {r.created_at?.slice(0, 16)} · P@5={r.metrics.retrieval?.['precision@5']}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
