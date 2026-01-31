from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application configuration loaded from .env file."""
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    TAX_API_BASE_URL: str = "https://api.example.com/v1"
    TAX_API_FAILOVER_URL: Optional[str] = None
    
    TAXJAR_API_KEY: Optional[str] = None
    TAXJAR_API_URL: Optional[str] = None
    
    # Ollama Configuration (Local LLM)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:1b"
    
    LLM_MODEL: str = "ollama"
    MAX_RETRIES: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables
    )

settings = Settings()
