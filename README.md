# Advanced Financial Analyst RAG 📈

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

An enterprise-grade, multi-agent Retrieval-Augmented Generation (RAG) system designed specifically for financial analysis. Built to handle complex quantitative and qualitative queries against SEC 10-K reports.

## Overview
Standard RAG systems often fail in financial contexts because they treat all queries the same. This project solves that by implementing an **Agentic Router architecture (LangGraph)** that classifies user questions and dynamically routes them to specialized retrieval systems.

## Key Features & Architecture
- **LangGraph Agent Router**: Uses a Gemini 2.5 Flash LLM judge to route strategic questions to the Vector Store, and quantitative numerical questions to a structured SQL database.
- **Advanced Hybrid Search**: Combines Dense Vector Search (ChromaDB + `all-MiniLM-L6-v2` local embeddings) with Sparse Keyword Search (BM25) to ensure exact matches for financial tickers and product names.
- **Cross-Encoder Re-ranking**: Uses a local HuggingFace Cross-Encoder (`BAAI/bge-reranker-base`) to score and re-rank the retrieved chunks, dramatically increasing Context Precision before passing context to the LLM.
- **RAGAS Evaluation**: Includes a fully automated evaluation pipeline (`evaluate_rag.py`) to mathematically score the system on Faithfulness, Answer Relevance, and Context Precision.

## Tech Stack
| Component | Technology |
|---|---|
| **Language Model** | Google Gemini 2.5 Flash |
| **Orchestration** | LangGraph, LangChain |
| **Embeddings (Local)** | HuggingFace (`all-MiniLM-L6-v2`) |
| **Vector Database** | ChromaDB |
| **Re-Ranker (Local)** | HuggingFace (`BAAI/bge-reranker-base`) |
| **Backend API** | FastAPI |
| **Frontend UI** | Streamlit |
| **Evaluation** | RAGAS |

## Quick Start

1. **Clone and Install**
```bash
git clone https://github.com/yourusername/advanced-financial-rag.git
cd advanced-financial-rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Environment Variables**
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
```

3. **Run the Application**
Launch both the FastAPI backend and Streamlit frontend:
```bash
./run.sh
```

4. **Access the UI**
Open `http://localhost:8502` in your browser. Upload a financial PDF and start asking questions!
