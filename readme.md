# structure

RAG /
│
├── data/
│   ├── raw/                     # original source files, unmodified
│   │   ├── policies/
│   │   │   └── hr_policy.docx
│   │   ├── reports/
│   │   │   └── annual_report.pdf
│   │   ├── datasets/
│   │   │   └── q3_sales.csv
│   │   ├── wiki/
│   │   │   └── faq.html
│   │   └── notes/
│   │       └── meeting_notes.txt
│   │
│   └── chroma_db/               # persisted vector store (gitignored)
│
├── src/
│   ├── __init__.py
│   │
│   ├── loaders/                 # one file per format
│   │   ├── __init__.py
│   │   ├── txt_loader.py
│   │   ├── pdf_loader.py
│   │   ├── docx_loader.py
│   │   ├── csv_loader.py
│   │   ├── xlsx_loader.py
│   │   ├── html_loader.py
│   │   └── loader_registry.py   # maps file extension -> correct loader
│   │
│   ├── chunking/
│   │   ├── __init__.py
│   │   ├── text_chunker.py      # your existing tiktoken splitter, for prose
│   │   └── table_chunker.py     # row/summary-based, for csv/xlsx
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── ingest.py            # orchestrates: load -> chunk -> embed -> store
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_retriever.py
│   │   ├── keyword_retriever.py # BM25
│   │   └── hybrid_retriever.py  # combines both
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   └── rag_chain.py         # your LCEL chain, with citation prompting
│   │
│   └── config.py                # paths, chunk sizes, model names, etc.
│
├── cli.py                       # <-- your console entry point (Stage 1 focus)
│
├── api/                         # <-- built LATER, once cli.py works
│   └── main.py                  # FastAPI wrapping the same src/ modules
│
├── frontend/                    # <-- built LATER, your html/css/js
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md