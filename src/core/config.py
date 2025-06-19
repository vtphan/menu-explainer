from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    database_url: str = "sqlite:///./menu_data.db"
    
    # API
    app_name: str = "Menu Explainer API"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))  # Use PORT env var for Render
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Pagination
    default_page_size: int = 100
    max_page_size: int = 500
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()