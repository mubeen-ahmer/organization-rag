# Verano RAG — Hybrid Retrieval & Text-to-SQL Knowledge Assistant

A production-style RAG backend for Verano Apparel Ltd. that answers questions over both
unstructured documents (HR policy, FAQs, meeting notes, hiring postings) and structured
sales/inventory data — routing each question to the right engine automatically. Ships as
a FastAPI service, ready to be consumed by any frontend or client.

---

## Why I Built This

Most "RAG tutorials" stop at semantic search over a handful of PDFs. Real company data
isn't like that — it's a mix of prose (policies, FAQs, meeting notes) and tables (sales
transactions, inventory), and a single vector search can't answer "what's our return
policy" and "how many units of JKT-BMB-301 did we sell in June" equally well.

I built Verano RAG to solve that properly: a **hybrid retriever** (semantic + keyword)
for prose, a **separate Text-to-SQL agent** for tabular data, and an LLM-based **router**
that decides which engine a question needs — then wrapped the whole thing in a real
FastAPI backend with a warm-start lifecycle, so it behaves like an actual deployable
service instead of a notebook script.

---

## Tech Stack

- **LLM:** Google Gemini (`langchain-google-genai`)
- **Embeddings:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (local)
- **Vector Store:** Chroma (persisted locally)
- **Keyword Search:** BM25 (`langchain_community.retrievers.BM25Retriever`)
- **Hybrid Retrieval:** `EnsembleRetriever` (Reciprocal Rank Fusion over vector + BM25)
- **Tabular Engine:** SQLite + LLM-generated SQL via LangChain LCEL
- **Framework:** LangChain (LCEL chains, runnables, retrievers)
- **API Layer:** FastAPI + Pydantic + Server-Sent Events (SSE) streaming

---

## Features

- **Dual-engine routing** — an LLM classifier decides per-question whether to hit the
  hybrid document retriever or the SQL agent, with no manual switching.
- **Hybrid prose retrieval** — combines semantic similarity (Chroma) and keyword overlap
  (BM25) via rank fusion, so both "what's similar in meaning" and "exact term matches"
  contribute to results.
- **Text-to-SQL agent** — answers numeric/aggregate/transaction-level questions by
  generating and executing SQL against a live schema cache, no manual query writing.
- **Incremental ingestion** — a file-hash manifest means only new or changed documents
  get re-chunked, re-embedded, and re-indexed on each run — not the whole corpus.
- **Multi-format loaders** — `.txt`, `.pdf`, `.docx`, `.html` (structured FAQ parsing),
  `.csv`/`.xlsx` (routed into SQLite instead of the vector store).
- **Warm-start API** — a FastAPI `lifespan` handler loads the embedding model and
  vectorstore once at server boot, so per-request latency doesn't pay model-load cost.
- **Streaming responses** — `/api/chat/stream` streams tokens live via SSE, so any
  client (web widget, mobile app, another service) can render a real-time typing effect.
- **CORS-enabled** — ready to be called from a browser-based frontend hosted anywhere,
  with no backend code changes needed on the client side.

---

## Setup

### Prerequisites
- Python 3.10+
- A Google Gemini API key

### Clone the repo
```bash
git clone https://github.com/mubeen-ahmer/organization-rag.git
cd organization-rag
```

### Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Configure environment
Create a `.env` file in the project root using the provided `.env.example` as a template, and fill in your Google Gemini API key.


### Add your data
Drop source documents into `data/raw/` - prose files
(`.txt/.pdf/.docx/.html`) go to the vector store, tabular files (`.csv/.xlsx`)
go to SQLite automatically on ingestion.

---

## Usage

Verano RAG can be run two ways: as a one-off **console script**, or as a persistent
**backend API service** meant to be consumed by a frontend or another client.

### Option A — Run as a console script

For quick local testing without spinning up a server:
```bash
python main.py
```
This loads the vectorstore, ingests any new documents, and drops you into an
interactive terminal loop — type a question, get an answer, type `quit` to exit.
Every run re-loads the embedding model, so expect a few seconds of startup delay
each time.

### Option B — Run as a backend service (recommended)

This is the production path — the server loads everything **once** at startup and
stays warm, serving requests instantly after that.

```bash
uvicorn api.main:app --reload --port 8000
```

- API docs (interactive testing): `http://127.0.0.1:8000/docs`
- Health check: `GET http://127.0.0.1:8000/api/health`
- Ask a question (JSON): `POST http://127.0.0.1:8000/api/chat`
```json
  { "question": "What is the return policy?" }
```
- Ask a question (streamed): `GET http://127.0.0.1:8000/api/chat/stream?question=...`

Any frontend, widget, or client application can consume this service by sending
requests to these endpoints — CORS is already enabled, so a browser-based client
hosted on a completely different domain/port can call it directly.

---

## Project Structure

```
verano-rag/
├── data/
│   ├── raw/
│   ├── chroma_db/                  # persisted vector store (gitignored)
│   ├── company_data.db             # SQLite tabular store
│   ├── manifest.json               # file-hash ingestion manifest
│   ├── bm25_index.pkl              # cached BM25 index (gitignored)
│   └── schema_cache.txt            # cached SQL schema description
├── src/
│   ├── __init__.py
│   ├── api/
│   │   └── main.py                 # FastAPI app (routes, lifespan, CORS)
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── txtLoader.py
│   │   ├── pdfLoader.py
│   │   ├── docxLoader.py
│   │   ├── csvLoader.py
│   │   ├── htmlLoader.py
│   │   └── loaderRegistry.py       # maps file extension -> correct loader
│   │
│   ├── chunking/
│   │   ├── __init__.py
│   │   └── textChunker.py          # tiktoken-based recursive splitter
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── ingest.py               # orchestrates: load -> chunk -> embed -> store
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_retriever.py     # Chroma + HuggingFace embeddings
│   │   ├── keyword_retriever.py    # BM25
│   │   └── hybrid_retriever.py     # EnsembleRetriever (RRF)
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── ragChain.py             # prose RAG chain + router
│   │   └── sql_agent.py            # Text-to-SQL agent
│   │
│   └── config.py                   # paths, chunk sizes, model names
│
├── main.py                         # console/script entry point
├── requirements.txt
├── .env                            # GOOGLE_API_KEY (gitignored)
└── .gitignore
```