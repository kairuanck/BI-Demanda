"""Configuração da aplicação, lida a partir de variáveis de ambiente.

Ver DEPLOY.md, seção 3, para a lista completa de variáveis suportadas.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> core -> app -> backend -> raiz do repositório
REPO_ROOT_DIR: Path = Path(__file__).resolve().parents[3]
DEFAULT_DATABASE_PATH: Path = REPO_ROOT_DIR / "database" / "app.db"
DEFAULT_STORAGE_DIR: Path = REPO_ROOT_DIR / "imports"


class Settings(BaseSettings):
    """Configuração central da aplicação (Pydantic v2)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = f"sqlite:///{DEFAULT_DATABASE_PATH}"

    jwt_secret_key: str = "dev-secret-key-troque-em-producao"
    jwt_refresh_secret_key: str = "dev-refresh-secret-key-troque-em-producao"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    cors_allowed_origins: str = "http://localhost:5173"

    storage_dir: str = str(DEFAULT_STORAGE_DIR)

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
