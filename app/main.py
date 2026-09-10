from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
import uuid
import time
from pathlib import Path

from app.hybrid_retriever import ingest_and_build_retriever
from app.graph import app_graph
from app.observability import get_langfuse_handler

app = FastAPI(title="Advanced Financial Analyst RAG")

class QueryRequest(BaseModel):
    question: str
    user_id: str = "anonymous"

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a PDF and builds the Advanced Hybrid Retriever."""
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        ingest_and_build_retriever(str(file_path))
        return {"message": f"Successfully ingested {file.filename} into Hybrid Retriever + Re-ranker"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: QueryRequest):
    """Routes the query through LangGraph with full Langfuse observability."""
    session_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Create a Langfuse handler to trace this entire request
        langfuse_handler = get_langfuse_handler(
            user_id=request.user_id,
            session_id=session_id
        )
        
        # Pass the handler into the graph state so nodes can use it
        state = app_graph.invoke({
            "question": request.question,
            "langfuse_handler": langfuse_handler
        })
        
        latency_ms = round((time.time() - start_time) * 1000)
        
        # Flush traces to Langfuse
        langfuse_handler.flush()
        
        return {
            "answer": state["generation"],
            "route_taken": state.get("datasource", "unknown"),
            "session_id": session_id,
            "latency_ms": latency_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
