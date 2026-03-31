# backend/core/config.py
# ─────────────────────────────────────────────
# This file is the single source of truth for
# all configuration in the app. Instead of 
# hardcoding values everywhere, we read them
# once here and import from here everywhere else.
# ─────────────────────────────────────────────

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

class Settings(BaseSettings):
    # App
    app_name: str = "Enterprise AI Knowledge Assistant"
    app_version: str = "1.0.0"
    environment: str = "development"

    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Paths
    documents_path: str = os.getenv("DOCUMENTS_PATH", "./documents")
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    collection_name: str = os.getenv("COLLECTION_NAME", "enterprise_docs")

    # Chunking settings
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # Server
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # Departments (used for RBAC)
    departments: list = ["HR", "Finance", "IT", "Legal", "Operations"]

    class Config:
        env_file = ".env"

# Create a single instance — import this everywhere
settings = Settings()