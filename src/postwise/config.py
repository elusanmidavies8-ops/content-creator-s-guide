"""Typed settings. The only place that reads environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="POSTWISE_",
        extra="ignore",
    )

    app_env: Literal["dev", "test", "prod"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    llm_provider: Literal["openai", "ollama", "fake"] = "fake"
    llm_model: str = Field(default="llama-3.1-8b-instruct", min_length=1)
    llm_base_url: str | None = None
    llm_api_key: SecretStr | None = None
    llm_timeout_s: int = Field(default=30, ge=1, le=300)
    llm_max_retries: int = Field(default=2, ge=0, le=5)

    @field_validator("llm_api_key", mode="before")
    @classmethod
    def _empty_key_is_none(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            return None
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings. Tests call `get_settings.cache_clear()` or
    construct `Settings(...)` directly."""
    return Settings()
