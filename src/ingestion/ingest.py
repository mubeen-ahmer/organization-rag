import os
import hashlib
import json
from src.loaders.loaderRegistry import loadFile, LOADER_MAP
from src.chunking.textChunker import chunkText

from src.config import MANIFEST_PATH, RAW_DATA_DIR

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
        
def ingestNewFiles(vectorstore):
    manifest = _loadManifest()
    updatedManifest = manifest.copy()
    ingested_count = 0
    
    for root,_,files in os.walk(RAW_DATA_DIR):
        for file in files: 
            filepath = os.path.join(root,file)
            ext = os.path.splitext(filepath)[1].lower()
            if ext not in LOADER_MAP:
                continue
            currentHash = _getFileHash(filepath)
            if currentHash == manifest.get(filepath):
                continue
            docs = loadFile(filepath)
            chunks = chunkText(docs)
            
            vectorstore.add_documents(chunks)
            
            updatedManifest[filepath]=currentHash
            ingested_count += 1
    _saveManifest(updatedManifest)
            
    if ingested_count != 0:
        print(f"Ingested {ingested_count} file(s).")