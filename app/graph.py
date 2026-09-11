from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from app.router import route_question
from app.hybrid_retriever import get_retriever
from app.config import settings
from app.sql_engine import query_financial_sql_database
from app.market_tool import query_live_market_data

# 1. Define the Graph State
class GraphState(TypedDict):
    question: str
    generation: str
    documents: list
    datasource: str
    langfuse_handler: Optional[Any]

# 2. Define the Nodes
def route_node(state: GraphState):
    """Routes the question dynamically to vectorstore, sql_database, or live_market_data."""
    print("---ROUTE QUESTION---")
    question = state["question"]
    datasource = route_question(question)
    print(f"  Routing decision: {datasource}")
    return {"datasource": datasource}

def retrieve_node(state: GraphState):
    """Retrieves documents from the Hybrid Retriever + Re-ranker."""
    print("---RETRIEVE DOCUMENTS---")
    question = state["question"]
    retriever = get_retriever()
    documents = retriever.invoke(question)
    print(f"  Retrieved {len(documents)} high-quality chunks")
    return {"documents": documents}

def sql_node(state: GraphState):
    """Executes deterministic Text-to-SQL against the financials SQLite database."""
    print("---SQL DATABASE EXECUTION---")
    question = state["question"]
    langfuse_handler = state.get("langfuse_handler")
    generation = query_financial_sql_database(question, langfuse_handler=langfuse_handler)
    return {"generation": generation}

def market_node(state: GraphState):
    """Fetches real-time stock quotes and valuation metrics via yfinance."""
    print("---LIVE MARKET TOOL EXECUTION---")
    question = state["question"]
    langfuse_handler = state.get("langfuse_handler")
    generation = query_live_market_data(question, langfuse_handler=langfuse_handler)
    return {"generation": generation}

def generate_node(state: GraphState):
    """Generates the final answer using Gemini Flash."""
    print("---GENERATE ANSWER---")
    question = state["question"]
    documents = state["documents"]
    langfuse_handler = state.get("langfuse_handler")
    
    # Format documents
    context = "\n\n".join(doc.page_content for doc in documents)
    
    prompt = ChatPromptTemplate.from_template("""You are an advanced financial analyst AI.
Answer the question using ONLY the provided context.
If you cannot answer based on the context, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:""")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=settings.gemini_api_key,
            temperature=0.1
        )
    except Exception:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.1
        )
    
    chain = prompt | llm | StrOutputParser()
    
    invoke_kwargs = {"context": context, "question": question}
    config = {}
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]
    
    generation = chain.invoke(invoke_kwargs, config=config if config else None)
    return {"generation": generation}

# 3. Define the Edges
def route_after_decision(state: GraphState):
    if state["datasource"] == "live_market_data":
        return "market"
    elif state["datasource"] == "sql_database":
        return "sql"
    elif state["datasource"] == "vectorstore":
        return "retrieve"
    return "retrieve"

# 4. Build the Graph
workflow = StateGraph(GraphState)

workflow.add_node("router", route_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("sql", sql_node)
workflow.add_node("market", market_node)
workflow.add_node("generate", generate_node)

workflow.set_entry_point("router")
workflow.add_conditional_edges(
    "router",
    route_after_decision,
    {
        "sql": "sql",
        "retrieve": "retrieve",
        "market": "market",
    }
)
workflow.add_edge("retrieve", "generate")
workflow.add_edge("sql", END)
workflow.add_edge("market", END)
workflow.add_edge("generate", END)

# Compile
app_graph = workflow.compile()
