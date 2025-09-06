# In backend/app/config.py
"""
Configuration settings for the CROPS Price Tracker Backend
Path: backend/app/config.py
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # --- REQUIRED from your .env file ---
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    SECRET_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None # For AI features

    # --- OPTIONAL with default values ---
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Scraping Settings
    PLAYWRIGHT_HEADLESS: bool = True
    SCRAPING_TIMEOUT: int = 30000
    MAX_RETRIES: int = 3
    
    # Email Settings
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = "noreply@cropsegypt.com"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        # This tells Pydantic to look for a file named .env
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

@lru_cache()
def get_settings():
    """Get cached settings instance"""
    return Settings()

settings = get_settings()