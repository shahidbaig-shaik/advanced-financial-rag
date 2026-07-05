from pathlib import Path
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever

# We will build a custom Hybrid Retriever + Reranker class to avoid LangChain versioning issues
# and to show true ML Engineering depth (Reciprocal Rank Fusion).
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import Document

from app.config import settings

_retriever = None

class AdvancedHybridRetriever:
    def __init__(self, vector_retriever, bm25_retriever, cross_encoder):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.cross_encoder = cross_encoder
        
    def invoke(self, query: str):
        print("  -> Running Vector Search (Semantic)...")
        vector_docs = self.vector_retriever.invoke(query)
        
        print("  -> Running BM25 Search (Keyword)...")
        bm25_docs = self.bm25_retriever.invoke(query)
        
        # Combine documents (removing duplicates by page_content)
        unique_docs = {}
        for doc in vector_docs + bm25_docs:
            if doc.page_content not in unique_docs:
                unique_docs[doc.page_content] = doc
                
        docs_list = list(unique_docs.values())
        print(f"  -> Combined {len(docs_list)} unique chunks. Re-ranking now...")
        
        # Prepare inputs for Cross-Encoder: list of [query, doc_text] pairs
        pairs = [[query, doc.page_content] for doc in docs_list]
        
        # Score pairs
        scores = self.cross_encoder.score(pairs)
        
        # Sort documents by score descending
        scored_docs = list(zip(docs_list, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 3
        top_3 = [doc for doc, score in scored_docs[:3]]
        return top_3


def ingest_and_build_retriever(file_path: str):
    global _retriever
    
    print(f"Loading PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    print("Chunking documents...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(pages)

    print("Building Vector Search (Chroma) with Local Embeddings...")
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    BATCH_SIZE = 80
    vectorstore = None
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i: i + BATCH_SIZE]
        print(f"  Embedding batch {i // BATCH_SIZE + 1} ({len(batch)} chunks)...")
        if vectorstore is None:
            vectorstore = Chroma.from_documents(batch, embeddings, persist_directory=settings.chroma_persist_dir)
        else:
            vectorstore.add_documents(batch)
            
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": settings.top_k_results})

    print("Building Keyword Search (BM25)...")
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = settings.top_k_results

    print("Loading Cross-Encoder Re-ranker (BAAI/bge-reranker-base)...")
    # This downloads the model on first run
    cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
    
    _retriever = AdvancedHybridRetriever(vector_retriever, bm25_retriever, cross_encoder)
    
    print("✅ Advanced Retriever built successfully!")
    return _retriever

def get_retriever():
    if _retriever is None:
        raise ValueError("Retriever not built. Call ingest_and_build_retriever first.")
    return _retriever
