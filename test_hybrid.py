import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

from app.hybrid_retriever import ingest_and_build_retriever

def test():
    print("\n🚀 Starting Advanced RAG Test...\n")
    retriever = ingest_and_build_retriever("data/sample_docs/sample_financial_report.pdf")
    
    question = "What was the net income in 2024?"
    print(f"\n❓ Question: {question}")
    
    print("\n🔍 Retrieving and Re-ranking...")
    results = retriever.invoke(question)
    
    print(f"\n✅ Top {len(results)} Chunks returned by Cross-Encoder:\n")
    for i, doc in enumerate(results):
        print(f"--- Rank {i+1} ---")
        print(doc.page_content.strip())
        print("-" * 50)

if __name__ == "__main__":
    test()
