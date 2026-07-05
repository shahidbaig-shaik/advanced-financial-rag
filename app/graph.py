from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from app.router import route_question
from app.hybrid_retriever import get_retriever
from app.config import settings

# 1. Define the Graph State
class GraphState(TypedDict):
    question: str
    generation: str
    documents: list
    datasource: str

# 2. Define the Nodes
def route_node(state: GraphState):
    """Routes the question."""
    print("---ROUTE QUESTION---")
    question = state["question"]
    datasource = route_question(question)
    print(f"  Routing to: {datasource}")
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
    """Mock node for SQL DB."""
    print("---SQL DATABASE---")
    # In a real app, this would use LangChain's SQLDatabaseChain
    return {"generation": "I am a mock SQL database. You asked for a number."}

def generate_node(state: GraphState):
    """Generates the final answer using Gemini 2.5 Flash."""
    print("---GENERATE ANSWER---")
    question = state["question"]
    documents = state["documents"]
    
    # Format documents
    context = "\n\n".join(doc.page_content for doc in documents)
    
    prompt = ChatPromptTemplate.from_template("""You are an advanced financial analyst AI.
Answer the question using ONLY the provided context.
If you cannot answer based on the context, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:""")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.1
    )
    
    chain = prompt | llm | StrOutputParser()
    generation = chain.invoke({"context": context, "question": question})
    
    return {"generation": generation}

# 3. Define the Edges
def route_after_decision(state: GraphState):
    if state["datasource"] == "sql_database":
        return "sql"
    elif state["datasource"] == "vectorstore":
        return "retrieve"

# 4. Build the Graph
workflow = StateGraph(GraphState)

workflow.add_node("router", route_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("sql", sql_node)
workflow.add_node("generate", generate_node)

workflow.set_entry_point("router")
workflow.add_conditional_edges(
    "router",
    route_after_decision,
    {
        "sql": "sql",
        "retrieve": "retrieve",
    }
)
workflow.add_edge("retrieve", "generate")
workflow.add_edge("sql", END)
workflow.add_edge("generate", END)

# Compile
app_graph = workflow.compile()
