from __future__ import annotations
from dataclasses import dataclass
import os


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "GROE")
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./groe.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "development-only-change-me")
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
    refresh_token_days: int = int(os.getenv("REFRESH_TOKEN_DAYS", "14"))
    cors_origins: tuple[str, ...] = tuple(filter(None, os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8000").split(",")))
    ai_provider: str = os.getenv("AI_PROVIDER", "none")
    ai_api_key: str | None = os.getenv("AI_API_KEY") or None
    open_meteo_base_url: str = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
    open_meteo_geocoding_url: str = os.getenv("OPEN_METEO_GEOCODING_URL", "https://geocoding-api.open-meteo.com/v1")
    auto_seed: bool = _bool("AUTO_SEED", True)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
