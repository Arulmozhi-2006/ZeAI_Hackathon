from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "AI Prompt Firewall"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # Database
    SUPABASE_DB_URL: str
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-flash-latest"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # ML
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    MODEL_ARTIFACT_DIR: str = "app/ml/models_store"
    RISK_BLOCK_THRESHOLD: float = 70.0

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()