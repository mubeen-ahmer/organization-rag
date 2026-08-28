from langchain_classic.retrievers import EnsembleRetriever
from src.retrieval.vector_retriever import get_vectorstore
from src.retrieval.keyword_retriever import get_keyword_retriever

def get_hybrid_retriever(k: int = 4, weights: list = [0.5, 0.5]):
    """
    Combines Vector Search (semantic) and BM25 Search (keyword)
    using EnsembleRetriever (Reciprocal Rank Fusion).
    """
    vectorstore = get_vectorstore()
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    keyword_retriever = get_keyword_retriever(k=k)

    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, keyword_retriever],
        weights=weights
    )
    return ensemble_retriever

def retrieve_hybrid(query: str, k: int = 4):
    """
    Retrieves documents using hybrid search (Vector + BM25).
    """
    retriever = get_hybrid_retriever(k=k)
    return retriever.invoke(query)