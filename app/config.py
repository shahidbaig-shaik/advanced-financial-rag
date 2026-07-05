import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    chroma_persist_dir: str = "./chroma_db"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 20  # Retrieve a lot for the re-ranker to filter down

    class Config:
        env_file = ".env"

settings = Settings()
