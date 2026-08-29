import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.config import LLM_MODEL_NAME
from src.retrieval.hybrid_retriever import get_hybrid_retriever
from src.generation.sql_agent import query_database

load_dotenv()

PROMPT_TEMPLATE = """You are a helpful assistant for Verano Apparel Ltd.
Answer the question based ONLY on the following context. 
If the context does not contain enough information, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:"""

ROUTER_PROMPT = """Classify the following user question into one of two categories:
- 'tabular': If the question asks for numeric calculations (sums, averages, counts, math), lists of sales transactions, sales representatives, or specific details about transactions (e.g., TRX-XXXXX IDs) from the sales report.
- 'prose': If the question asks about company policies, documents, FAQs, hiring openings, HR rules, or meeting notes.

Respond with ONLY the word 'tabular' or 'prose'. Do not include punctuation, spaces, or any other explanation.

Question: {question}
"""

def _format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

def get_rag_chain():
    retriever = get_hybrid_retriever(k=4)
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
    """
    Fallback RAG chain for prose queries.
    """
    chain = get_rag_chain()
    return chain.invoke(question)

def route_and_ask(question: str) -> str:
    """
    Classifies the user query and routes it to either the SQL Database Agent or the Prose RAG chain.
    """
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=0.0)
    prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)
    chain = prompt | llm | StrOutputParser()
    
    route = chain.invoke({"question": question}).strip().lower()
    
    if "tabular" in route:
        return query_database(question)
    else:
        return ask(question)