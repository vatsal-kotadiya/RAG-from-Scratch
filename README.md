# RAG From Scratch: A Retrieval-Augmented Document Intelligence and Evaluation System

## 1. Project overview

Upload documents (PDF, DOCX, TXT, MD), index them into semantic vectors, ask
questions, and get grounded answers with source citations and retrieval scores.
Includes a retrieval inspector and an evaluation dashboard with real metrics.

## 2. Why RAG

LLMs hallucinate on private/domain documents they never saw. RAG grounds
generation in retrieved context: question → embedding → semantic search →
top-k chunks → context → LLM → answer + citations. An LLM-only baseline is
built in to show the difference.

## 3. Architecture

```
React (Vite + Tailwind) --REST--> FastAPI
  Dashboard | Documents | Chat | Evaluation
FastAPI: documents API / chat API / evaluation API
RAG services: loader -> cleaner -> chunker -> embeddings ->
  ChromaDB -> retriever -> reranker -> context builder ->
  prompt -> LLM provider -> citations
Data: ChromaDB (vectors+chunks) | SQLite (metadata) | filesystem (uploads)
```

## 4. How RAG works

1. Upload validates type/size, stores the file.
2. Text extracted per page (PyMuPDF) / paragraphs+tables (DOCX) / text (TXT/MD).
3. Cleaned, split into overlapping chunks (~500/50, configurable) with metadata.
4. Embedded with `all-MiniLM-L6-v2`, stored persistently in ChromaDB.
5. Question embedded, cosine search filtered by selected `document_id`s.
6. Chunks below `MIN_RETRIEVAL_SCORE` are dropped; the rest become `SOURCE n` blocks.
7. LLM answers using only that context, else abstains honestly.

## 5. Technology stack

Backend: Python, FastAPI, Pydantic, Uvicorn, LangChain (light use),
sentence-transformers, ChromaDB, SQLite, PyMuPDF, python-docx.
LLM providers: OpenAI, Gemini (`google.genai`), Ollama, echo (no-key fallback).
Frontend: React, Vite, Tailwind, Axios, React Router, lucide-react, Recharts.

## 6. Installation

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r backend\requirements.txt   # project-local only
cd frontend; npm install                                   # local node_modules only
cp backend\.env.example backend\.env
```

## 7. Environment variables

See `backend/.env.example`: chunk size/overlap, top-k, min score, embedding and
LLM provider/model, API keys, Chroma/SQLite paths, upload limits. Never commit
`backend/.env`.

## 8. Running backend

```powershell
cd backend
..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 9. Running frontend

```powershell
cd frontend
npm run dev    # http://localhost:5173 (proxies /api to :8000)
```

## 10. Uploading documents

Documents page → Upload (PDF/DOCX/TXT/MD, ≤20 MB). Watch status move
UPLOADING → PROCESSING → INDEXING → READY (or FAILED with a reason).
Re-index and delete (file + SQLite + vectors) are supported.

## 11. Asking questions

Chat page → tick READY documents → ask. Each answer shows sources
(file, page, similarity), provider, and expandable retrieval metadata.

## 12. Evaluation

Seed a document matching `evaluation_dataset/seed.json` (a sample
`company_policy.txt` is included), then Evaluation page → Run Evaluation.
Metrics persist and past runs are comparable.

## 13. Metrics

Retrieval: Precision@K, Recall@K, MRR, avg similarity (labels from dataset).
Generation: faithfulness, answer/context relevance, hallucination rate
(transparent heuristics; RAGAS-ready), abstention accuracy, plus an LLM-only
baseline for comparison. Nothing is fabricated — empty without a run.

## 14. Project structure

`backend/app/{api,core,models,schemas,ingestion,embeddings,vectorstore,retrieval,generation,rag,evaluation,database}`,
`backend/{tests,evaluation_dataset,data}`, `frontend/src/{components,pages,services}`.

## 15. Limitations

- No OCR (scanned PDFs extract no text); table-heavy PDFs are approximate.
- Word-count chunking approximates tokens; retrieval quality depends on it.
- Generation quality depends on the configured provider/key.
- Heuristic generation metrics (no LLM judge yet); single Chroma collection.

## 16. Future improvements

OCR, hybrid keyword+vector search, cross-encoder reranking, query rewriting,
conversation-aware retrieval, FAISS store option, multilingual embeddings.
