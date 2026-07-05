from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
from pathlib import Path

from app.hybrid_retriever import ingest_and_build_retriever
from app.graph import app_graph

app = FastAPI(title="Advanced Financial Analyst RAG")

class QueryRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a PDF and builds the Advanced Hybrid Retriever."""
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Build the RAG system with the new PDF
        ingest_and_build_retriever(str(file_path))
        return {"message": f"Successfully ingested {file.filename} into Hybrid Retriever + Re-ranker"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: QueryRequest):
    """Routes the query through LangGraph and returns the answer."""
    try:
        # Pass the question to the LangGraph entry point
        state = app_graph.invoke({"question": request.question})
        return {
            "answer": state["generation"],
            "route_taken": state.get("datasource", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
