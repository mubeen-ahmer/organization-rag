import re
import os
import pickle
from langchain_community.retrievers import BM25Retriever
from src.retrieval.vector_retriever import get_vectorstore
from src.config import BM25_INDEX_PATH
_keyword_retriever = None

# Clean preprocessing to strip commas/punctuation from tokens (e.g. TRX-10006, -> trx, 10006)
    
def clean_tokenize(text: str):
    return re.findall(r'\w+', text.lower())

def _build_index(k: int = 4):
    vectorstore = get_vectorstore()
    stored_data = vectorstore.get()
    texts = stored_data.get("documents", [])
    metadatas = stored_data.get("metadatas", [])
    
    if not texts:
        raise ValueError("No documents found in the vectorstore to build BM25 index.")

    retriever = BM25Retriever.from_texts(
        texts=texts, 
        metadatas=metadatas,
        preprocess_func=clean_tokenize
    )
    retriever.k = k
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(retriever, f)
    return retriever

def get_keyword_retriever(k: int = 4):
    global _keyword_retriever

    if _keyword_retriever is not None:
        _keyword_retriever.k = k
        return _keyword_retriever

    if os.path.exists(BM25_INDEX_PATH):
        with open(BM25_INDEX_PATH, "rb") as f:
            _keyword_retriever = pickle.load(f)
        _keyword_retriever.k = k
        return _keyword_retriever

    _keyword_retriever = _build_index(k)
    return _keyword_retriever

def rebuild_keyword_index(k: int = 4):
    """
    Force a full rebuild of the BM25 index from current vectorstore contents.
    Call this only when new prose documents were actually ingested.
    """
    global _keyword_retriever
    _keyword_retriever = _build_index(k)
    return _keyword_retriever

# def retrieve_by_keywords(query: str, k: int = 4):
#     retriever = get_keyword_retriever(k=k)
#     return retriever.invoke(query)