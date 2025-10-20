from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application
    app_name: str = "FastAPI Hexagonal Architecture"
    app_version: str = "1.0.0"
    debug: bool = False

    # Gemini API
    gemini_api_key: str = "your-gemini-api-key-here"
    gemini_model: str = "gemini-pro"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None

    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
