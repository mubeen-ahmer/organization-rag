from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from src.config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME

def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return Chroma(
        persist_directory=CHROMA_DB_DIR, 
        embedding_function=embeddings
    )

def retrieve_documents(query: str, k: int = 4):
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return retriever.get_relevant_documents(query)
