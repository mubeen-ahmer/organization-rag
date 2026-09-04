import os
import re
import hashlib
import json
import sqlite3
import pandas as pd
from src.loaders.loaderRegistry import loadFile, LOADER_MAP
from src.chunking.textChunker import chunkText
from src.config import MANIFEST_PATH, RAW_DATA_DIR, SQLITE_DB_PATH
from src.generation.sql_agent import rebuild_schema_cache
from src.retrieval.keyword_retriever import rebuild_keyword_index

# Supported tabular formats for SQLite ingestion
SQL_EXTENSIONS = {".csv", ".xlsx", ".xls"}

def _getFileHash(path : str):
    with open(path,"rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def _loadManifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    return {}

def _saveManifest(manifest):
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

def _ingest_to_sqlite(filepath: str):
    """
    Ingests a tabular file (CSV/Excel) into the SQLite database.
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(filepath)
    elif ext in {".xlsx", ".xls"}:
        df = pd.read_excel(filepath)
    else:
        return
        
    # Sanitize column names for SQL (replace non-word chars with underscores)
    df.columns = [re.sub(r'\W+', '_', col).strip('_') for col in df.columns]
    
    # Establish connection and write table
    conn = sqlite3.connect(SQLITE_DB_PATH)
    table_name = os.path.splitext(os.path.basename(filepath))[0]
    table_name = re.sub(r'\W+', '_', table_name).strip('_')
    
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"Ingested {os.path.basename(filepath)} into SQLite table '{table_name}'.")

def ingestNewFiles(vectorstore):
    manifest = _loadManifest()
    updatedManifest = manifest.copy()
    ingested_count = 0
    prose_changed = False
    tabular_changed = False  # NEW

    for root, _, files in os.walk(RAW_DATA_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            ext = os.path.splitext(filepath)[1].lower()

            is_tabular = ext in SQL_EXTENSIONS
            is_prose = ext in LOADER_MAP

            if not is_tabular and not is_prose:
                continue

            currentHash = _getFileHash(filepath)
            if currentHash == manifest.get(filepath):
                continue

            if is_tabular:
                _ingest_to_sqlite(filepath)
                tabular_changed = True  # NEW
            elif is_prose:
                docs = loadFile(filepath)
                if ext != ".html":
                    chunks = chunkText(docs)
                else:
                    chunks = docs
                vectorstore.add_documents(chunks)
                prose_changed = True

            updatedManifest[filepath] = currentHash
            ingested_count += 1

    _saveManifest(updatedManifest)

    if prose_changed:
        print("New prose documents detected — rebuilding BM25 keyword index...")
        rebuild_keyword_index()

    if tabular_changed:
        print("New tabular data detected — rebuilding SQL schema cache...")
        rebuild_schema_cache()

    if ingested_count != 0:
        print(f"Ingestion check complete. Updated {ingested_count} file(s).")