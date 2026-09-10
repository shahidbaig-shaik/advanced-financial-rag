import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    chroma_persist_dir: str = "./chroma_db"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 20  # Retrieve a lot for the re-ranker to filter down
    
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: Optional[str] = None
    langfuse_base_url: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
