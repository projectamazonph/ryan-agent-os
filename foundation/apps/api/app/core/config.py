from __future__ import annotations

from functools import lru_cache
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAOS_", env_file=".env", extra="ignore")

    env: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    owner_email: str = "ryan.d@goodwitcommerce.com"
    owner_password: str = "change-me-now"
    jwt_secret: str = "development-secret-change-me-please"
    jwt_ttl_minutes: int = 720

    database_url: str = "sqlite+aiosqlite:///./.data/raos.db"
    redis_url: str = "redis://localhost:6379/0"
    auto_create_tables: bool = True
    auto_process_captures: bool = False

    model_provider: str = "rules"
    model_base_url: str = "http://localhost:8080/v1"
    model_name: str = "hermes-3"
    model_api_key: str = ""
    model_timeout_seconds: float = 60.0
    max_upload_bytes: int = 25 * 1024 * 1024
    cors_origins: str = "http://localhost:3000"

    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "raos"
    s3_secret_key: str = "raos-local-secret"
    s3_bucket: str = "raos-local"
    s3_region: str = "us-east-1"
    s3_secure: bool = False

    @model_validator(mode="after")
    def validate_production_secrets(self) -> Self:
        if self.model_provider not in {"rules", "hermes", "cloud"}:
            raise ValueError("RAOS_MODEL_PROVIDER must be rules, hermes, or cloud")
        if self.model_provider == "cloud" and not self.model_api_key:
            raise ValueError("RAOS_MODEL_API_KEY is required for the cloud provider")
        if self.env == "production":
            if self.owner_password == "change-me-now":
                raise ValueError("RAOS_OWNER_PASSWORD must be changed in production")
            if len(self.jwt_secret) < 32:
                raise ValueError("RAOS_JWT_SECRET must contain at least 32 characters")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
