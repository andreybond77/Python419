import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(
        "sqlite+aiosqlite:///./dark_moon.db",
        env="DATABASE_URL"
    )
    
    # JWT - ЕДИНЫЙ СТАНДАРТ (все поля в UPPER_CASE)
    SECRET_KEY: str = Field("your-secret-key-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Application
    DEBUG: bool = Field(True, env="DEBUG")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    CORS_ORIGINS: List[str] = Field(["http://localhost:3000", "http://localhost:8001"], env="CORS_ORIGINS")
    
    # Redis (опционально)
    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(10485760, env="MAX_UPLOAD_SIZE")
    ALLOWED_EXTENSIONS: List[str] = Field(["jpg", "jpeg", "png", "webp"], env="ALLOWED_EXTENSIONS")
    
    # File paths
    UPLOAD_DIR: str = "uploads"
    POTION_IMAGES_DIR: str = "uploads/potions"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()