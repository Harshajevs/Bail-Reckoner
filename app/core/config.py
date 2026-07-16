from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Bail Reckoner"
    debug: bool = False

    # SQLite by default so the project runs with zero setup;
    # point at PostgreSQL in production, e.g.
    # postgresql://user:password@host:5432/bail_reckoner
    database_url: str = "sqlite:///./bail_reckoner.db"

    secret_key: str = "insecure-dev-key-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720

    # Comma-separated list of allowed origins. Empty means same-origin only,
    # which is the normal mode since the app serves its own frontend.
    cors_origins: str = ""

    # AI provider selection: rule_based | ollama | openrouter | openai.
    # Whatever is selected, rule_based remains the final fallback so the
    # feature works with no credentials at all.
    ai_provider: str = "rule_based"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ai_timeout_seconds: float = 30.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
