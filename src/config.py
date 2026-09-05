import os

# Base directory paths
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)

# Data paths
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "company_data.db")
MANIFEST_PATH = os.path.join(DATA_DIR, "manifest.json")

# Chunking configurations
CHUNK_SIZE = 400
CHUNK_OVERLAP = 30

# Model configurations
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL_NAME = "gemini-3.5-flash-lite"
BM25_INDEX_PATH = os.path.join(DATA_DIR, "bm25_index.pkl")

SCHEMA_CACHE_PATH = os.path.join(DATA_DIR, "schema_cache.txt")