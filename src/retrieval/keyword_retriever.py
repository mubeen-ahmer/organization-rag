import re
from langchain_community.retrievers import BM25Retriever
from src.retrieval.vector_retriever import get_vectorstore

def get_keyword_retriever(k: int = 4):
    vectorstore = get_vectorstore()
    stored_data = vectorstore.get()
    texts = stored_data.get("documents", [])
    metadatas = stored_data.get("metadatas", [])
    
    if not texts:
        raise ValueError("No documents found in the vectorstore to build BM25 index.")
    
    # Clean preprocessing to strip commas/punctuation from tokens (e.g. TRX-10006, -> trx, 10006)
    def clean_tokenize(text: str):
        return re.findall(r'\w+', text.lower())

    retriever = BM25Retriever.from_texts(
        texts=texts, 
        metadatas=metadatas,
        preprocess_func=clean_tokenize
    )
    retriever.k = k
    return retriever

def retrieve_by_keywords(query: str, k: int = 4):
    retriever = get_keyword_retriever(k=k)
    return retriever.invoke(query)