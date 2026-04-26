from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    # API Keys
    kimi_api_key: str
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
    kimi_model: str = "kimi-2.6"
    kimi_api_base: str = "https://ark.cn-beijing.volces.com/api/v3/"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
