import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.config import LLM_MODEL_NAME
from src.retrieval.vector_retriever import get_vectorstore

load_dotenv()

PROMPT_TEMPLATE = """You are a helpful assistant for Verano Apparel Ltd.
Answer the question based ONLY on the following context. 
If the context does not contain enough information, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:"""

def _format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME)

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

def ask(question: str) -> str:
    chain = get_rag_chain()
    return chain.invoke(question)