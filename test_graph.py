import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')
load_dotenv()

from app.hybrid_retriever import ingest_and_build_retriever
from app.graph import app_graph

def test_agent():
    print("\n🚀 Starting LangGraph End-to-End Test...\n")
    # First, build the retriever
    ingest_and_build_retriever("data/sample_docs/sample_financial_report.pdf")
    
    # Test 1: Qualitative Question (Should route to Vector/Hybrid)
    q1 = "What are the main risks associated with talent and the supply chain?"
    print(f"\n❓ Question 1: {q1}")
    result1 = app_graph.invoke({"question": q1})
    print(f"\n🧠 Final Agent Answer:\n{result1['generation']}")
    print("=" * 60)

    # Test 2: Quantitative Question (Should route to SQL)
    q2 = "What was the exact Q3 operating margin percentage?"
    print(f"\n❓ Question 2: {q2}")
    result2 = app_graph.invoke({"question": q2})
    print(f"\n🧠 Final Agent Answer:\n{result2['generation']}")
    print("=" * 60)

if __name__ == "__main__":
    test_agent()
