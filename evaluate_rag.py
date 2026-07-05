import os
import pandas as pd
from datasets import Dataset
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

# Import our Advanced RAG pipeline
from app.hybrid_retriever import ingest_and_build_retriever
from app.graph import app_graph
from app.config import settings

# Import RAGAS metrics and evaluators
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

def run_evaluation():
    print("\n🚀 Starting RAGAS Evaluation Pipeline...\n")
    
    # 1. Build the Retriever
    retriever = ingest_and_build_retriever("data/sample_docs/sample_financial_report.pdf")
    
    # 2. Define a golden dataset of test questions and ground truths
    test_cases = [
        {
            "question": "What was the total revenue for TechCorp in 2024?",
            "ground_truth": "TechCorp's total revenue reached $4.8 billion in 2024."
        },
        {
            "question": "What are the main regulatory risks facing the company?",
            "ground_truth": "Increasing AI regulation in the EU and US may limit the deployment of AI-powered products."
        },
        {
            "question": "How much was allocated to R&D?",
            "ground_truth": "TechCorp allocated $780M to R&D."
        }
    ]

    print("\n🤖 Running queries through Advanced RAG Agent...")
    results_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    for case in test_cases:
        question = case["question"]
        
        # We need the chunks that were retrieved to evaluate Context Precision
        # Since our LangGraph router abstract this away, we'll manually invoke the retriever
        # for the sake of gathering metrics, then invoke the graph for the answer.
        docs = retriever.invoke(question)
        contexts = [doc.page_content for doc in docs]
        
        # Get the final answer from our LangGraph agent
        state = app_graph.invoke({"question": question})
        answer = state["generation"]
        
        results_data["question"].append(question)
        results_data["answer"].append(answer)
        results_data["contexts"].append(contexts)
        results_data["ground_truth"].append(case["ground_truth"])

    # 3. Convert to HuggingFace Dataset (required by RAGAS)
    dataset = Dataset.from_dict(results_data)

    # 4. Setup RAGAS Judge LLMs (using Gemini to judge Gemini)
    print("\n⚖️ Initializing RAGAS Judge Models (Gemini 2.5 Flash)...")
    judge_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0
    )
    from langchain_huggingface import HuggingFaceEmbeddings
    judge_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. Run Evaluation
    print("\n📊 Calculating Metrics (Faithfulness, Relevance, Precision)...")
    # This sends the generated answers and context back to the LLM judge
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=judge_llm,
        embeddings=judge_embeddings,
    )
    
    # 6. Display Results
    print("\n" + "="*50)
    print("🏆 RAGAS EVALUATION RESULTS")
    print("="*50)
    df = result.to_pandas()
    print("\nOverall Scores:")
    print(df.mean(numeric_only=True))
    print("\nSaving detailed results to evaluation_results.csv...")
    df.to_csv("evaluation_results.csv", index=False)
    print("✅ Evaluation Complete!")

if __name__ == "__main__":
    run_evaluation()
