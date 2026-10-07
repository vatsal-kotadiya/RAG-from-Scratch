# RAG From Scratch — Complete Implementation Specification

## 1. Project Overview

### Project Name

**RAG From Scratch — Retrieval-Augmented Document Intelligence & Evaluation System**

### Project Goal

Build a complete Retrieval-Augmented Generation (RAG) application that allows users to upload documents, index their content, ask questions about those documents, retrieve semantically relevant information, and generate grounded answers with source citations.

The project must demonstrate the complete RAG pipeline rather than being only a basic "chat with PDF" application.

### Core Pipeline

```text
Documents
    ↓
Document Ingestion
    ↓
Text Extraction
    ↓
Text Cleaning
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Database
    ↓
User Question
    ↓
Query Embedding
    ↓
Semantic Retrieval
    ↓
Relevant Chunks
    ↓
Context Construction
    ↓
LLM
    ↓
Grounded Answer
    ↓
Source Citations
```

### Main Objective

The system should answer questions using information retrieved from the user's documents and should avoid inventing information when the answer cannot be found in the retrieved context.

---

# 2. Important Implementation Rule

This project should be implemented as a **real RAG system**, not as a fake UI around an LLM API.

The application must actually perform:

1. Document ingestion.
2. Text extraction.
3. Chunking.
4. Embedding generation.
5. Vector storage.
6. Semantic similarity search.
7. Retrieval of top-k chunks.
8. Context construction.
9. LLM generation using retrieved context.
10. Source citation.
11. Retrieval and generation evaluation.

Do not skip these steps by sending the entire document directly to the LLM.

---

# 3. Recommended Technology Stack

## Frontend

- React
- Vite
- Tailwind CSS
- Axios
- React Router
- Lucide React icons or another lightweight icon library
- Recharts or Chart.js for evaluation charts

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

## RAG Framework

- LangChain

Use LangChain where it improves modularity, but keep important RAG logic understandable and separated into project modules.

Do not hide the entire RAG pipeline behind a single high-level chain.

## Document Processing

- PyMuPDF / fitz for PDF
- python-docx for DOCX
- Standard Python file handling for TXT and Markdown

Supported formats:

- PDF
- DOCX
- TXT
- MD

## Embeddings

Primary local embedding option:

- sentence-transformers
- `all-MiniLM-L6-v2`

The embedding layer must be abstracted so another embedding model can be added later without rewriting the retrieval system.

## Vector Database

Primary:

- ChromaDB

The vector store layer must be abstracted so FAISS can optionally be added later.

## LLM

Implement an LLM provider abstraction.

Support at least one working provider initially, but structure the code so providers can be swapped.

Recommended providers:

- OpenAI API
- Gemini API
- Ollama/local models

Do not hard-code provider-specific logic throughout the application.

## Metadata / Application Database

Use SQLite initially for application metadata.

SQLite can store:

- documents
- document status
- chat sessions
- messages
- evaluation runs

ChromaDB stores embeddings and chunk metadata.

---

# 4. High-Level Architecture

```text
┌──────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│                                                          │
│  Dashboard │ Documents │ Chat │ Sources │ Evaluation     │
└──────────────────────────┬───────────────────────────────┘
                           │ REST API
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Document API                                            │
│  Chat API                                                │
│  Evaluation API                                          │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                    RAG Services                          │
│                                                          │
│  Document Loader                                         │
│  Text Cleaner                                            │
│  Chunking Service                                        │
│  Embedding Service                                       │
│  Vector Store                                             │
│  Retrieval Service                                       │
│  Reranking Service [optional/advanced]                   │
│  Context Builder                                         │
│  Prompt Manager                                          │
│  LLM Service                                             │
│  Citation Service                                        │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                     Data Layer                           │
│                                                          │
│  ChromaDB → embeddings + chunks + metadata               │
│  SQLite   → application metadata                         │
│  Filesystem → uploaded documents                         │
└──────────────────────────────────────────────────────────┘
```

---

# 5. Frontend Requirements

The frontend should look like a modern professional AI/data application.

Do not make it look like a generic template.

## Main Pages

### 5.1 Dashboard

Show:

- Total documents
- Total indexed chunks
- Total questions asked
- Average retrieval score
- Evaluation summary
- Recent documents
- Recent conversations

Example:

```text
RAG Intelligence Dashboard

Documents        Indexed Chunks       Questions
   12                 1,248              86

Retrieval Quality
Precision@5    0.91
Recall@5       0.88
MRR            0.84

Recent Documents
- Student Handbook.pdf
- Company Policy.pdf
- Research Paper.pdf
```

---

# 6. Documents Page

Users should be able to:

- Upload documents
- See uploaded documents
- See processing status
- See number of pages
- See number of chunks
- See upload date
- Delete documents
- Re-index documents

Statuses:

```text
UPLOADING
PROCESSING
INDEXING
READY
FAILED
```

Example:

```text
Documents

[ + Upload Document ]

┌───────────────────────────────────────────────┐
│ Student Handbook.pdf                          │
│ 85 pages · 342 chunks                         │
│ Status: Ready                                 │
│ [View] [Re-index] [Delete]                    │
└───────────────────────────────────────────────┘
```

---

# 7. Chat Page

The primary user experience.

Users should be able to:

- Select one or more documents
- Ask questions
- Receive answers
- View sources
- View retrieval scores
- Start a new conversation
- See conversation history

Example:

```text
┌────────────────────────────────────────────────────────┐
│ RAG Assistant                                           │
├───────────────┬────────────────────────────────────────┤
│ Documents     │ What is the attendance requirement?    │
│               │                                        │
│ ☑ Handbook    │ AI:                                    │
│ ☑ Rules       │ The minimum attendance requirement     │
│               │ is 75%.                                 │
│               │                                        │
│               │ Sources                                 │
│               │ ┌────────────────────────────────────┐ │
│               │ │ Student Handbook.pdf               │ │
│               │ │ Page 42 · Similarity 0.91          │ │
│               │ └────────────────────────────────────┘ │
│               │                                        │
│               │ Ask a question...                  ➤  │
└───────────────┴────────────────────────────────────────┘
```

---

# 8. Retrieval Inspector

This is an important differentiating feature.

For each question, allow the user to inspect:

```text
Question
    ↓
Query Embedding
    ↓
Retrieved Chunks
    ↓
Similarity Scores
    ↓
Final Context
    ↓
LLM Answer
```

Example:

```text
Retrieval Results

Rank 1
Document: Student Handbook.pdf
Page: 42
Score: 0.91

"Students must maintain a minimum attendance
of 75% in each semester."

Rank 2
Document: Student Handbook.pdf
Page: 43
Score: 0.86

"Students falling below 75% attendance..."
```

This makes the system explainable and useful for learning/debugging.

---

# 9. Evaluation Dashboard

Create a dedicated evaluation page.

Show:

### Retrieval Metrics

- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Average similarity score

### Generation Metrics

- Faithfulness
- Answer relevance
- Context relevance
- Hallucination rate

### Comparison

Allow comparison between:

```text
LLM Only
vs
RAG
```

Use real results from the project's evaluation dataset.

Do not fabricate metric values.

---

# 10. Backend Folder Structure

Use a clean modular architecture.

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── documents.py
│   │   ├── chat.py
│   │   └── evaluation.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── models/
│   │   ├── document.py
│   │   ├── chat.py
│   │   └── evaluation.py
│   │
│   ├── schemas/
│   │   ├── document.py
│   │   ├── chat.py
│   │   └── evaluation.py
│   │
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── pdf_loader.py
│   │   ├── docx_loader.py
│   │   ├── text_loader.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   │
│   ├── embeddings/
│   │   ├── base.py
│   │   └── sentence_transformer.py
│   │
│   ├── vectorstore/
│   │   ├── base.py
│   │   └── chroma_store.py
│   │
│   ├── retrieval/
│   │   ├── retriever.py
│   │   ├── filters.py
│   │   └── reranker.py
│   │
│   ├── generation/
│   │   ├── llm.py
│   │   ├── providers/
│   │   └── prompts.py
│   │
│   ├── rag/
│   │   ├── pipeline.py
│   │   ├── context_builder.py
│   │   └── citations.py
│   │
│   ├── evaluation/
│   │   ├── dataset.py
│   │   ├── retrieval_metrics.py
│   │   ├── generation_metrics.py
│   │   └── evaluator.py
│   │
│   └── database/
│       ├── sqlite.py
│       └── repositories/
│
├── tests/
│   ├── test_chunking.py
│   ├── test_embeddings.py
│   ├── test_retrieval.py
│   ├── test_rag.py
│   └── test_api.py
│
├── data/
│   ├── uploads/
│   └── chroma/
│
├── evaluation_dataset/
│
├── requirements.txt
├── .env.example
└── README.md
```

---

# 11. Frontend Folder Structure

```text
frontend/
│
├── src/
│   ├── components/
│   │   ├── layout/
│   │   ├── documents/
│   │   ├── chat/
│   │   ├── sources/
│   │   └── evaluation/
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Documents.jsx
│   │   ├── Chat.jsx
│   │   └── Evaluation.jsx
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── hooks/
│   ├── utils/
│   ├── types/
│   ├── App.jsx
│   └── main.jsx
│
├── package.json
└── vite.config.js
```

---

# 12. Document Ingestion Pipeline

Implement the ingestion pipeline as follows:

```text
Upload
  ↓
Validate extension
  ↓
Store original file
  ↓
Extract text
  ↓
Clean text
  ↓
Split into chunks
  ↓
Attach metadata
  ↓
Generate embeddings
  ↓
Store vectors
  ↓
Mark document READY
```

If any step fails:

```text
Document status = FAILED
```

Store a useful error message for debugging.

---

# 13. Document Metadata

Every chunk should contain metadata such as:

```json
{
  "document_id": "uuid",
  "filename": "student_handbook.pdf",
  "page_number": 42,
  "chunk_id": "uuid",
  "source_type": "pdf"
}
```

For DOCX/TXT/MD, page number can be null if unavailable.

---

# 14. Chunking Strategy

Initial implementation:

```text
chunk_size: approximately 500 tokens
chunk_overlap: approximately 50 tokens
```

The values should be configurable.

Do not hard-code them throughout the codebase.

Create configuration:

```env
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
```

The system should preserve metadata for every chunk.

---

# 15. Embedding Service

Create an interface similar to:

```python
class EmbeddingService:
    def embed_documents(self, texts):
        pass

    def embed_query(self, text):
        pass
```

Implement:

```text
SentenceTransformerEmbeddingService
```

using:

```text
all-MiniLM-L6-v2
```

The system should not assume that the embedding dimension is fixed in application logic.

---

# 16. Vector Store

Create an abstraction:

```python
class VectorStore:
    def add_documents(self, chunks):
        pass

    def similarity_search(self, query, top_k):
        pass

    def delete_document(self, document_id):
        pass
```

Implement:

```text
ChromaVectorStore
```

The metadata must be preserved.

The vector database must support filtering by:

```text
document_id
```

so the user can query selected documents only.

---

# 17. Retrieval

Basic retrieval:

```text
Question
   ↓
Query Embedding
   ↓
Chroma similarity search
   ↓
Top K chunks
```

Default:

```text
TOP_K=5
```

Return:

```json
{
  "chunk_id": "...",
  "text": "...",
  "score": 0.91,
  "document_id": "...",
  "filename": "student_handbook.pdf",
  "page_number": 42
}
```

---

# 18. Similarity Score

Use the vector store's supported similarity/distance mechanism consistently.

Normalize scores if necessary before displaying them as user-friendly similarity scores.

Do not incorrectly label a raw distance as a similarity score.

---

# 19. Context Construction

Create a dedicated context builder.

Input:

```text
retrieved_chunks
```

Output:

```text
SOURCE 1
Document: student_handbook.pdf
Page: 42

Students must maintain a minimum attendance
of 75% in each semester.

SOURCE 2
...
```

Do not send unrelated chunks to the LLM.

---

# 20. Prompt Design

Use a controlled RAG system prompt.

Example:

```text
You are a document-grounded assistant.

Answer the user's question using only the
provided context.

Rules:
1. Do not invent facts.
2. Do not use outside knowledge when answering.
3. If the context does not contain enough information,
   clearly state that the answer cannot be found in
   the provided documents.
4. Keep the answer concise and directly relevant.
5. Cite the provided sources when appropriate.

Context:
{context}

Question:
{question}
```

The exact wording can be improved during testing.

---

# 21. Hallucination Handling

If retrieved context does not contain enough information:

```text
I couldn't find enough information in the
provided documents to answer this question.
```

The model must not confidently invent an answer.

Also implement a minimum retrieval relevance threshold where appropriate.

For example:

```env
MIN_RETRIEVAL_SCORE=...
```

The exact threshold must be determined experimentally rather than blindly assuming one universal value.

---

# 22. LLM Provider Abstraction

Create:

```python
class LLMProvider:
    def generate(self, prompt):
        pass
```

Then implement provider-specific classes.

Example:

```text
OpenAIProvider
GeminiProvider
OllamaProvider
```

Only the selected provider should be initialized.

Credentials must come from environment variables.

Never expose API keys to the frontend.

---

# 23. API Design

## Upload Document

```http
POST /api/documents/upload
Content-Type: multipart/form-data
```

Response:

```json
{
  "id": "doc_123",
  "filename": "student_handbook.pdf",
  "status": "PROCESSING"
}
```

---

## List Documents

```http
GET /api/documents
```

---

## Get Document

```http
GET /api/documents/{document_id}
```

---

## Delete Document

```http
DELETE /api/documents/{document_id}
```

This must delete:

- File
- SQLite metadata
- Vector database chunks

---

## Re-index

```http
POST /api/documents/{document_id}/reindex
```

---

## Ask Question

```http
POST /api/chat
```

Request:

```json
{
  "question": "What is the minimum attendance requirement?",
  "document_ids": ["doc_123"],
  "top_k": 5
}
```

Response:

```json
{
  "answer": "The minimum attendance requirement is 75%.",
  "sources": [
    {
      "document_id": "doc_123",
      "filename": "student_handbook.pdf",
      "page": 42,
      "score": 0.91,
      "chunk_id": "chunk_123"
    }
  ],
  "retrieval": {
    "top_k": 5,
    "results": 5
  }
}
```

---

## Chat History

```http
GET /api/chat/sessions
POST /api/chat/sessions
GET /api/chat/sessions/{session_id}
DELETE /api/chat/sessions/{session_id}
```

---

## Evaluation

```http
POST /api/evaluation/run
GET /api/evaluation/runs
GET /api/evaluation/runs/{run_id}
```

---

# 24. SQLite Data Model

## Documents

```text
documents
---------
id
filename
file_path
file_type
file_size
page_count
chunk_count
status
error_message
created_at
updated_at
```

## Chat Sessions

```text
chat_sessions
-------------
id
title
created_at
updated_at
```

## Messages

```text
messages
--------
id
session_id
role
content
created_at
```

## Evaluation Runs

```text
evaluation_runs
---------------
id
dataset_name
model_name
embedding_model
top_k
metrics_json
created_at
```

---

# 25. Evaluation Dataset

Create a small real evaluation dataset.

Example JSON:

```json
[
  {
    "question": "What is the minimum attendance requirement?",
    "expected_answer": "75%",
    "relevant_document": "student_handbook.pdf",
    "relevant_pages": [42]
  }
]
```

Create at least 20–50 questions for meaningful evaluation.

Questions should cover:

- Direct fact questions
- Paraphrased questions
- Multi-sentence questions
- Questions requiring context from multiple chunks
- Questions whose answers do not exist in the documents

---

# 26. Retrieval Evaluation

Implement:

## Precision@K

Measures how many retrieved results are relevant.

## Recall@K

Measures how many relevant results were successfully retrieved.

## MRR

Mean Reciprocal Rank measures how high the first relevant result appears.

## Average Similarity

Track the average retrieval score.

Do not calculate metrics using fabricated relevance labels.

The evaluation dataset must define the expected relevant chunks/documents/pages.

---

# 27. Generation Evaluation

Measure:

### Faithfulness

Does the answer follow the retrieved context?

### Answer Relevance

Does the answer actually answer the question?

### Context Relevance

Was useful context retrieved?

### Hallucination Rate

How often does the model make unsupported claims?

Use an evaluation framework such as RAGAS where practical, but keep the metric implementation understandable.

---

# 28. Baseline Comparison

A major project requirement should be:

```text
Baseline:
Question → LLM → Answer

RAG:
Question → Retrieval → Context → LLM → Answer
```

Run the same evaluation questions against both.

Compare:

```text
Faithfulness
Answer relevance
Hallucination rate
```

This provides evidence for why RAG is useful.

---

# 29. Advanced Features

These should be implemented only after the basic system works.

## 29.1 Hybrid Search

Combine:

```text
Vector Search
+
Keyword Search
```

Possible architecture:

```text
Question
   ↓
 ┌───────────────┐
 │               │
 ▼               ▼
Vector Search    Keyword Search
 │               │
 └───────┬───────┘
         ▼
      Combine
         ↓
      Reranker
```

---

## 29.2 Reranking

Initial retrieval:

```text
Top 20
```

Reranker:

```text
Top 20
 ↓
Reranker
 ↓
Top 5
```

This can improve retrieval quality.

Keep reranking modular.

---

## 29.3 Query Rewriting

For ambiguous questions:

```text
Original question
      ↓
Query rewriting
      ↓
Improved search query
      ↓
Retrieval
```

Do not enable query rewriting by default if it adds unnecessary latency.

---

## 29.4 Multi-Document Retrieval

Allow:

```text
Document A
+
Document B
+
Document C
```

The user can ask questions across selected documents.

---

## 29.5 Conversation-Aware Retrieval

For follow-up questions:

```text
User:
What is the attendance requirement?

Assistant:
75%.

User:
What happens if I don't meet it?
```

The second query should understand the previous conversation context.

Do not blindly send the entire chat history into retrieval.

Use a query rewriting or conversation-aware retrieval strategy.

---

# 30. Security Requirements

Implement:

- File type validation
- File size limits
- Safe filenames
- Path traversal protection
- API key protection
- Environment variables
- No secrets in frontend
- Input validation
- Error handling
- CORS configuration
- Safe file deletion

Do not execute uploaded files.

Only process supported document formats.

---

# 31. Performance Requirements

The system should:

- Avoid loading unnecessary full documents into memory.
- Batch embedding operations where practical.
- Persist ChromaDB data.
- Avoid rebuilding embeddings on every question.
- Cache/reuse document embeddings.
- Use asynchronous FastAPI endpoints where beneficial.
- Keep LLM provider calls isolated.
- Provide processing status for document indexing.

---

# 32. Error Handling

Frontend should display useful errors.

Examples:

```text
Unsupported file format.
Maximum file size exceeded.
Document extraction failed.
Document indexing failed.
LLM provider unavailable.
Embedding model failed to load.
No relevant information found.
```

Backend logs should contain detailed technical information without exposing secrets.

---

# 33. Configuration

Create `.env.example`.

Example:

```env
APP_ENV=development

BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5

EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

LLM_PROVIDER=openai
LLM_MODEL=...

OPENAI_API_KEY=

CHROMA_PERSIST_DIRECTORY=./data/chroma

DATABASE_URL=sqlite:///./data/app.db

MAX_FILE_SIZE_MB=20
```

Never commit `.env`.

---

# 34. Logging

Create structured logs for:

```text
Document upload
Document extraction
Chunk creation
Embedding generation
Vector indexing
Query retrieval
LLM request
Evaluation
Errors
```

Never log API keys or sensitive document content unnecessarily.

---

# 35. Testing Requirements

Create unit tests for:

### Ingestion

- PDF extraction
- DOCX extraction
- TXT extraction
- Invalid file
- Empty document

### Chunking

- Chunk size
- Overlap
- Metadata preservation

### Embeddings

- Embedding generation
- Query embedding
- Dimension consistency

### Retrieval

- Relevant chunk returned
- Top-k behavior
- Document filtering

### RAG

- Context construction
- Prompt construction
- No-context behavior
- Citation generation

### API

- Upload
- List
- Delete
- Chat
- Evaluation

---

# 36. Expected User Flow

## First-time user

```text
Open application
      ↓
Dashboard
      ↓
Upload PDF
      ↓
Processing
      ↓
Indexing
      ↓
Ready
      ↓
Open Chat
      ↓
Select document
      ↓
Ask question
      ↓
Retrieve relevant chunks
      ↓
Generate answer
      ↓
Display answer
      ↓
Display sources
```

---

# 37. Example End-to-End Scenario

Document:

```text
company_policy.pdf
```

Question:

```text
"What is the work-from-home allowance?"
```

Pipeline:

```text
Question
    ↓
Embedding
    ↓
Vector Search
    ↓
Top 5 chunks
    ↓
Relevant chunk:
"Employees may work remotely up to
2 days per week."
    ↓
Context Builder
    ↓
LLM
    ↓
Answer:
"Employees may work remotely up to
2 days per week."
    ↓
Citation:
company_policy.pdf — Page 7
```

---

# 38. Out-of-Context Scenario

Question:

```text
"What is the company's maternity leave policy?"
```

If the uploaded documents do not contain this information:

```text
Answer:

I couldn't find enough information about the
maternity leave policy in the provided documents.
```

Do not invent a policy.

---

# 39. UI/UX Requirements

The application should be:

- Clean
- Professional
- Responsive
- Fast
- Easy to understand
- Suitable for an academic/portfolio project

Use a consistent design system.

Include:

- Loading states
- Skeleton states
- Empty states
- Error states
- Toast notifications where appropriate
- Accessible buttons
- Keyboard-friendly chat input
- Responsive layout

Do not overload the UI with unnecessary animations.

---

# 40. Important UX Detail: Explainability

Every generated answer should make it possible to understand:

```text
Where did this answer come from?
```

Therefore provide:

```text
Answer
Sources
Retrieval scores
Document
Page
```

An optional expandable section can show:

```text
Retrieved Context
```

---

# 41. RAG Pipeline Service

Create one main orchestrator:

```python
class RAGPipeline:

    def ask(
        self,
        question,
        document_ids=None,
        top_k=5
    ):
        # 1. Embed query
        # 2. Retrieve chunks
        # 3. Filter/rerank
        # 4. Build context
        # 5. Generate answer
        # 6. Attach citations
        # 7. Return structured result
        pass
```

Keep each operation delegated to its own service.

Do not create one huge file containing the entire project.

---

# 42. Response Schema

The backend should return structured data:

```json
{
  "answer": "The minimum attendance requirement is 75%.",
  "sources": [
    {
      "filename": "student_handbook.pdf",
      "page": 42,
      "score": 0.91,
      "chunk_id": "chunk_123"
    }
  ],
  "retrieval_metadata": {
    "top_k": 5,
    "retrieved_count": 5,
    "average_score": 0.84
  }
}
```

This allows the frontend to visualize the retrieval process.

---

# 43. Development Phases

## Phase 1 — Project Setup

Create:

```text
frontend
backend
database
data directories
environment configuration
```

Make sure frontend and backend run independently.

---

## Phase 2 — Document Processing

Implement:

```text
Upload
PDF/DOCX/TXT/MD extraction
Cleaning
Chunking
Metadata
```

Test this before implementing the LLM.

---

## Phase 3 — Embeddings + ChromaDB

Implement:

```text
Embedding service
ChromaDB persistence
Document indexing
Vector search
```

Test retrieval using simple queries.

---

## Phase 4 — RAG Generation

Implement:

```text
Question
 ↓
Retrieval
 ↓
Context
 ↓
LLM
 ↓
Answer
```

Add source citations.

---

## Phase 5 — Frontend

Build:

```text
Dashboard
Documents
Chat
Sources
```

Connect to backend APIs.

---

## Phase 6 — Evaluation

Implement:

```text
Evaluation dataset
Precision@K
Recall@K
MRR
Faithfulness
Answer relevance
Hallucination testing
```

Create evaluation dashboard.

---

## Phase 7 — Advanced RAG

Only after the base system is stable:

```text
Hybrid retrieval
Reranking
Query rewriting
Conversation-aware retrieval
```

---

## Phase 8 — Testing + Documentation

Complete:

- Unit tests
- Integration tests
- README
- Architecture diagram
- API documentation
- RAG explanation
- Evaluation report
- Setup instructions
- Limitations

---

# 44. README Requirements

The final README must explain:

1. Project overview
2. Why RAG
3. Architecture
4. How RAG works
5. Technology stack
6. Installation
7. Environment variables
8. Running backend
9. Running frontend
10. Uploading documents
11. Asking questions
12. Evaluation
13. Metrics
14. Project structure
15. Limitations
16. Future improvements

---

# 45. Academic/Project Documentation

Prepare documentation sections:

## Abstract

Explain the problem, RAG approach, implementation, and results.

## Introduction

Explain:

- LLM limitations
- hallucination
- knowledge limitations
- document search
- RAG

## Problem Statement

Traditional LLMs may generate plausible but unsupported information when asked about private or domain-specific documents.

## Objectives

- Build document ingestion pipeline.
- Generate semantic embeddings.
- Store document vectors.
- Retrieve relevant context.
- Generate grounded answers.
- Provide source citations.
- Evaluate retrieval and generation quality.
- Compare RAG against an LLM-only baseline.

## Methodology

Explain the complete RAG pipeline.

## System Architecture

Include architecture diagram.

## Implementation

Explain every module.

## Evaluation

Report actual experimental results.

## Limitations

Examples:

- OCR is not initially supported.
- Table-heavy PDFs may be difficult.
- Retrieval quality depends on chunking.
- LLM output depends on the provider.
- Embedding quality affects retrieval.
- Large document collections may require more advanced indexing.

## Future Work

Possible:

- OCR
- multimodal RAG
- hybrid retrieval
- advanced reranking
- knowledge graph integration
- multilingual embeddings
- local LLM deployment

---

# 46. Important Engineering Principles

Antigravity must follow these principles:

### Do not over-engineer the first version.

Build the simplest working RAG pipeline first.

### Do not hide the core RAG logic.

The project should clearly show:

```text
embedding
retrieval
context
generation
```

### Do not fabricate evaluation metrics.

Every displayed metric must come from an actual evaluation run.

### Do not hard-code API keys.

Use environment variables.

### Do not couple frontend to a specific LLM provider.

The backend owns LLM integration.

### Do not couple retrieval to ChromaDB.

Use a vector store abstraction.

### Do not rebuild embeddings for every question.

Embeddings should be generated during indexing.

---

# 47. Definition of Done

The project is considered complete when all of the following work:

## Document Management

- [ ] Upload PDF
- [ ] Upload DOCX
- [ ] Upload TXT
- [ ] Upload Markdown
- [ ] Validate files
- [ ] Process documents
- [ ] Show indexing status
- [ ] Delete documents
- [ ] Re-index documents

## RAG

- [ ] Text extraction
- [ ] Chunking
- [ ] Embeddings
- [ ] ChromaDB
- [ ] Semantic retrieval
- [ ] Top-k retrieval
- [ ] Context construction
- [ ] LLM generation
- [ ] Source citations
- [ ] Out-of-context handling

## Frontend

- [ ] Dashboard
- [ ] Documents page
- [ ] Chat page
- [ ] Source viewer
- [ ] Retrieval inspector
- [ ] Evaluation dashboard
- [ ] Responsive design
- [ ] Loading/error states

## Evaluation

- [ ] Evaluation dataset
- [ ] Precision@K
- [ ] Recall@K
- [ ] MRR
- [ ] Faithfulness
- [ ] Answer relevance
- [ ] Hallucination analysis
- [ ] LLM-only baseline
- [ ] RAG comparison

## Engineering

- [ ] Modular architecture
- [ ] Environment variables
- [ ] Logging
- [ ] Error handling
- [ ] Unit tests
- [ ] API tests
- [ ] README
- [ ] Setup documentation

---

# 48. Suggested Final Project Title

Use:

**"RAG From Scratch: A Retrieval-Augmented Document Intelligence and Evaluation System"**

Alternative academic title:

**"Design and Implementation of a Retrieval-Augmented Generation System for Grounded Document Question Answering"**

---

# 49. Final Implementation Instruction for Antigravity

Implement this project as a complete, production-quality academic portfolio project.

Important:

1. Do not create only a frontend mockup.
2. Do not create only a chatbot.
3. Do not bypass semantic retrieval.
4. Do not send complete documents directly to the LLM.
5. Implement actual document chunking.
6. Implement actual embeddings.
7. Implement persistent ChromaDB storage.
8. Implement actual semantic retrieval.
9. Implement source metadata and citations.
10. Implement an LLM abstraction.
11. Implement evaluation.
12. Implement an LLM-only baseline for comparison.
13. Implement proper error handling.
14. Implement tests.
15. Keep the architecture modular.
16. Make configuration environment-based.
17. Do not expose secrets.
18. Build the basic RAG pipeline before advanced features.
19. Add advanced retrieval only after the basic pipeline is stable.
20. Do not fabricate results or evaluation metrics.

The final application should clearly demonstrate:

```text
DOCUMENT
   ↓
INGEST
   ↓
CHUNK
   ↓
EMBED
   ↓
INDEX
   ↓
RETRIEVE
   ↓
RERANK (optional)
   ↓
CONTEXT
   ↓
LLM
   ↓
ANSWER
   ↓
CITATIONS
   ↓
EVALUATION
```

The goal is not simply to make a chatbot.

The goal is to build and demonstrate a complete, explainable, measurable Retrieval-Augmented Generation system from the ground up.
