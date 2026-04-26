from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    # API Keys
    anthropic_api_key: str
    spotify_client_id: str
    spotify_client_secret: str
    openweather_api_key: str
    
    # Database
    database_url: str = "sqlite:///./claudio.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Environment
    environment: str = "development"
    
    # Music data
    music_data_path: str = "./data"
    
    # Model
    anthropic_model: str = "claude-3-opus-20240229"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
