from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


APP_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = APP_ROOT.parent
API_DIR = APP_ROOT / "API" if (APP_ROOT / "API").exists() else APP_ROOT
DEFAULT_DATA_DIR = APP_ROOT / "data"
LEGACY_DATA_DIR = WORKSPACE_ROOT / "data"
DATA_DIR = DEFAULT_DATA_DIR if DEFAULT_DATA_DIR.exists() else LEGACY_DATA_DIR
DEFAULT_ASSETS_DIR = APP_ROOT / "assets"
LEGACY_ASSETS_DIR = WORKSPACE_ROOT / "assets"
ASSETS_DIR = DEFAULT_ASSETS_DIR if DEFAULT_ASSETS_DIR.exists() else LEGACY_ASSETS_DIR

load_dotenv(WORKSPACE_ROOT / ".env")
load_dotenv(APP_ROOT / ".env")
load_dotenv(API_DIR / ".env")


def _split_csv_env(name: str) -> tuple[str, ...]:
    raw = os.getenv(name)
    if not raw:
        return ()
    return tuple(item.strip() for item in raw.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    project_name: str = "SPBEBOT API"
    version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    app_root: Path = APP_ROOT
    base_dir: Path = APP_ROOT
    api_dir: Path = API_DIR
    data_dir: Path = DATA_DIR
    assets_dir: Path = ASSETS_DIR
    allowed_origins: tuple[str, ...] = tuple(
        dict.fromkeys(
            _split_csv_env("ALLOWED_ORIGINS")
            + _split_csv_env("FRONTEND_ORIGIN")
            + (
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:4173",
                "http://127.0.0.1:4173",
            )
        )
    )
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model_name: str = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    document_allow_key: str | None = os.getenv("KEY_DOCUMENT_ALLOW")
    blob_read_write_token: str | None = os.getenv("BLOB_READ_WRITE_TOKEN")
    blob_access: str = os.getenv("BLOB_ACCESS", "private")
    blob_prefix: str = os.getenv("BLOB_PREFIX", "spbebot-docs")
    pinecone_api_key: str | None = os.getenv("PINECONE_API_KEY")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "spbe-cohere")
    cohere_api_key: str | None = os.getenv("COHERE_API_KEY")
    ollama_api_key: str | None = os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_EMBEDDING_API")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "https://ollama.com")
    ollama_model_name: str = os.getenv("OLLAMA_MODEL_NAME", "nomic-embed-text:latest")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
