import sqlite3
import os
import re
from typing import Optional, Any
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from app.config import settings

def get_db_path() -> str:
    """Find the path to the financials.db SQLite file."""
    # Check local relative to app
    current_dir = Path(__file__).resolve().parent.parent
    local_path = current_dir / "data" / "financials.db"
    if local_path.exists():
        return str(local_path)
    
    # Fallback to scratch or desktop
    for candidate in [
        "/Users/SHAHID/.gemini/antigravity/scratch/advanced-financial-rag/data/financials.db",
        "/Users/SHAHID/Desktop/advanced-financial-rag/data/financials.db"
    ]:
        if os.path.exists(candidate):
            return candidate
            
    return str(local_path)

DB_SCHEMA = """
Table 1: financial_metrics
- company: TEXT (e.g. 'Apple Inc.')
- fiscal_year: INTEGER (e.g. 2024, 2023, 2022)
- total_net_sales_millions: REAL (in millions USD)
- cost_of_sales_millions: REAL (in millions USD)
- gross_margin_millions: REAL (in millions USD)
- research_and_development_millions: REAL (in millions USD)
- sga_millions: REAL (in millions USD)
- operating_income_millions: REAL (in millions USD)
- net_income_millions: REAL (in millions USD)
- diluted_eps: REAL (earnings per share in USD)

Table 2: segment_revenue
- company: TEXT (e.g. 'Apple Inc.')
- fiscal_year: INTEGER (e.g. 2024, 2023)
- segment_name: TEXT ('iPhone', 'Services', 'Wearables, Home & Accessories', 'Mac', 'iPad')
- net_sales_millions: REAL (in millions USD)
- contribution_percentage: REAL (percentage contribution to total net sales)
"""

def generate_sql_query(question: str, langfuse_handler: Optional[Any] = None) -> str:
    """Uses Gemini 2.5 Flash to convert natural language to a clean SQLite query."""
    prompt = ChatPromptTemplate.from_template("""You are an expert SQL database engineer.
Given the following SQLite database schema:
{schema}

Write a single valid SQLite SELECT query to answer the user's question.
Rules:
1. ONLY return the raw SQL query. Do NOT include markdown code blocks, backticks, or explanation.
2. Only write SELECT statements. Never write INSERT, UPDATE, or DELETE.
3. Case-insensitive segment matching: Use LIKE or LOWER(segment_name) if applicable.

Question: {question}
SQL Query:""")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.0
    )
    
    chain = prompt | llm | StrOutputParser()
    
    config = {}
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]
        
    raw_sql = chain.invoke({"schema": DB_SCHEMA, "question": question}, config=config if config else None)
    
    # Strip any backticks or markdown fences
    cleaned_sql = re.sub(r"```[a-zA-Z]*", "", raw_sql).replace("```", "").strip()
    return cleaned_sql

def execute_sql(sql_query: str) -> tuple[list[str], list[tuple]]:
    """Executes a SELECT query on the financials SQLite database."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return columns, rows
    finally:
        conn.close()

def query_financial_sql_database(question: str, langfuse_handler: Optional[Any] = None) -> str:
    """End-to-end Text-to-SQL engine: Question -> SQL -> Execution -> Formatted Answer."""
    try:
        sql_query = generate_sql_query(question, langfuse_handler=langfuse_handler)
        print(f"  [Text-to-SQL Generated]: {sql_query}")
        
        # Security guardrail: Ensure read-only query
        if not sql_query.strip().upper().startswith("SELECT"):
            return "Security Notice: Only read-only SELECT queries are permitted on this database."
            
        columns, rows = execute_sql(sql_query)
        
        if not rows:
            return f"Queried the financial database with:\n`{sql_query}`\nNo matching records were found."

        # Format rows into context
        results_str = f"Columns: {', '.join(columns)}\nRows:\n"
        for r in rows:
            results_str += f"- {r}\n"

        # Synthesize final natural response
        synthesis_prompt = ChatPromptTemplate.from_template("""You are a quantitative financial analyst.
Given the user question, the generated SQL query, and the exact database results, provide a clear, concise financial response.

Question: {question}
SQL Query: {sql_query}
Database Results:
{results_str}

Guidelines:
1. State the exact numbers clearly, noting if they are in millions or per-share amounts.
2. At the end of your response, display the executed SQL query in a markdown code block:
Executed SQL:
```sql
<sql_query>
```
""")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.1
        )
        
        chain = synthesis_prompt | llm | StrOutputParser()
        
        config = {}
        if langfuse_handler:
            config["callbacks"] = [langfuse_handler]
            
        answer = chain.invoke({
            "question": question,
            "sql_query": sql_query,
            "results_str": results_str
        }, config=config if config else None)
        
        return answer

    except Exception as e:
        print(f"Error in Text-to-SQL: {e}")
        return f"Database query failed: {str(e)}"
