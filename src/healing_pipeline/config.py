from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    TAX_API_BASE_URL: str = "https://api.example.com/v1"
    TAX_API_FAILOVER_URL: Optional[str] = None
    
    LLM_MODEL: str = "gpt-4-turbo"
    MAX_RETRIES: int = 3
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
