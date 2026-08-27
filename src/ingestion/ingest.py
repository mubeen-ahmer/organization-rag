import os
import hashlib
import json
from src.loaders.loaderRegistry import loadFile
from src.chunking.textChunker import chunkText

MANIFEST_PATH = "data/manifest.json"
RAW_DATA_PATH = "data/raw"

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
    
    for root,_,files in os.walk(RAW_DATA_PATH):
        # print(root,files)
        for file in files: 
            filepath = os.path.join(root,file)
            currentHash = _getFileHash(filepath)
            if currentHash == manifest.get(filepath):
                continue
            docs = loadFile(filepath)
            chunks = chunkText(docs)
            
            vectorstore.add_documents(chunks)
            
            updatedManifest[filepath]=currentHash
            
    _saveManifest(updatedManifest)
            
        