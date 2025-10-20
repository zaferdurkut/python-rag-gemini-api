from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RAG System with ChromaDB"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Gemini AI
    GEMINI_API_KEY: str = "your-gemini-api-key-here"
    GEMINI_MODEL: str = "gemini-pro"

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "documents"
    CHROMA_HOST: Optional[str] = None  # ChromaDB server host
    CHROMA_SERVER_PORT: int = 8000  # ChromaDB server port
    CHROMA_TELEMETRY_ANONYMIZED: bool = False  # Disable ChromaDB telemetry
    CHROMA_TELEMETRY: bool = False  # Disable ChromaDB telemetry

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
