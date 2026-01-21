from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

# Point to .env file
ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class DatabaseSettings(BaseSettings):
    """Database configuration extracted from .env"""
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_ignore_empty=True,
        extra="ignore",
    )

    def POSTGRES_URL(self) -> str:
        """Generate PostgreSQL async connection URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    app_name: str = "FastAPI Template"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Security
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


@lru_cache()
def get_db_settings() -> DatabaseSettings:
    """Get cached database settings instance"""
    return DatabaseSettings()


settings = get_settings()
db_settings = get_db_settings()
