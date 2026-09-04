import sqlite3
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import LLM_MODEL_NAME, SQLITE_DB_PATH

load_dotenv()

def get_db_schema() -> str:
    """
    Retrieves the schemas and sample rows for all tables in the SQLite database.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_info = []
    for table_tuple in tables:
        table_name = table_tuple[0]
        # Skip sqlite internal tables
        if table_name.startswith("sqlite_"):
            continue
            
        # Get CREATE TABLE statement
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        create_sql = cursor.fetchone()[0]
        
        # Get a few sample rows
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        sample_rows = cursor.fetchall()
        
        # Get column headers
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]
        
        sample_str = "\n".join(str(dict(zip(columns, row))) for row in sample_rows)
        
        schema_info.append(f"Table: {table_name}\nSchema:\n{create_sql}\nSample Rows:\n{sample_str}\n")
        
    conn.close()
    return "\n---\n".join(schema_info)

SYSTEM_PROMPT = """You are a SQLite database assistant.
Given the tables and schemas below, write a read-only SQLite query to answer the user's question.

Database Schema:
{schema}

Rules:
1. Return ONLY the raw SQL query.
2. Do not wrap the SQL query in markdown code blocks or quotes.
3. Write only read-only queries (SELECT). Do not write INSERT, UPDATE, DELETE, or DROP.
4. For string comparison, use the LIKE operator with wildcards or case-insensitive matching if appropriate.
5. Do not include semicolons at the end of the query.

Question: {question}
"""

def query_database(question: str) -> str:
    schema = get_db_schema()
    if not schema:
        return "No tabular data is currently available in the database."
        
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME)
    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
    chain = prompt | llm | StrOutputParser()
    
    sql_query = chain.invoke({"schema": schema, "question": question}).strip()
    
    # Clean output wrapper codeblocks if the LLM generated them anyway
    if sql_query.startswith("```"):
        sql_query = sql_query.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if sql_query.startswith("sql"):
        sql_query = sql_query.replace("sql", "", 1).strip()
        
    # Execute the SQL query safely
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        # Get column headers
        headers = [description[0] for description in cursor.description]
        conn.close()
        
        if not results:
            return f"No results found matching that query.\nExecuted Query: {sql_query}"
            
        # Format the output rows
        formatted_rows = []
        for row in results:
            formatted_rows.append(", ".join(f"{h}: {val}" for h, val in zip(headers, row)))
        return "\n".join(formatted_rows)
    except Exception as e:
        conn.close()
        return f"Error executing SQL: {e}\nGenerated SQL: {sql_query}"
