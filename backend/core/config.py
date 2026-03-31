# backend/core/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # App
    app_name: str = "Enterprise AI Knowledge Assistant"
    app_version: str = "1.0.0"
    environment: str = "development"

    # API Keys — Gemini for embeddings, Groq for answers
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    # Paths
    documents_path: str = os.getenv("DOCUMENTS_PATH", "./documents")
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    collection_name: str = os.getenv("COLLECTION_NAME", "enterprise_docs")

    # Chunking
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # Server
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # Departments
    departments: list = ["HR", "Finance", "IT", "Legal", "Operations"]

    class Config:
        env_file = ".env"

# Single instance — import this everywhere
settings = Settings()