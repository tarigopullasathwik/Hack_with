"""
RecallDesk configuration — all settings loaded from environment variables.
"""
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os

# Resolve .env candidates relative to the repo rather than the current working
# directory, so the app picks up the root .env whether it is launched from
# backend/ (as the README instructs) or from the repository root.
_BACKEND_DIR = Path(__file__).resolve().parents[1]   # .../recalldesk/backend
_REPO_ROOT = _BACKEND_DIR.parent                    # .../recalldesk
_ENV_FILES = (str(_REPO_ROOT / ".env"), str(_BACKEND_DIR / ".env"))


class Settings(BaseSettings):
    # App
    APP_NAME: str = "RecallDesk"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # Database
    DATABASE_URL: str = "sqlite:///./recalldesk.db"

    # LLM Provider
    LLM_PROVIDER: str = "openai-compatible"
    LLM_MODEL: str = "qwen/qwen3.7-max:free"
    LLM_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_API_KEY", "API_KEY"),
    )
    LLM_BASE_URL: str = "https://api.xkiro.com/v1"             # OpenAI-compatible API base
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.3

    # Hindsight
    HINDSIGHT_BASE_URL: str = "http://localhost:8888"
    HINDSIGHT_API_KEY: str = ""      # For Hindsight Cloud; empty = local
    # embedded mode: start HindsightServer inside the process
    HINDSIGHT_EMBEDDED: bool = True
    # LLM for Hindsight memory extraction (can differ from main LLM)
    HINDSIGHT_LLM_PROVIDER: str = "openai-compatible"
    HINDSIGHT_LLM_MODEL: str = "qwen/qwen3.7-max:free"
    HINDSIGHT_LLM_API_KEY: str = ""  # falls back to LLM_API_KEY if empty
    HINDSIGHT_LLM_BASE_URL: str = ""  # falls back to LLM_BASE_URL if empty
    # Embedding + reranker backends for the Hindsight server. "local" (default)
    # downloads sentence-transformers models; use "openai" + "none" on machines
    # where the local ML stack is unavailable (e.g. blocked DLLs, no PyTorch).
    # "local" needs sentence-transformers + PyTorch; "onnx" needs onnxruntime +
    # transformers; "openai"/"gemini"/"cohere"/"tei" call an external service.
    HINDSIGHT_EMBEDDINGS_PROVIDER: str = "local"
    # "local" needs a cross-encoder (PyTorch); "rrf" is pure-Python and always
    # available, so it is the safe default when the local ML stack is missing.
    HINDSIGHT_RERANKER_PROVIDER: str = "rrf"
    # Seconds to wait for the embedded Hindsight server to come up.
    HINDSIGHT_START_TIMEOUT: float = 45.0

    # Company/product branding
    COMPANY_NAME: str = "Nexora Cloud"
    PRODUCT_NAME: str = "Nexora Workspace"

    class Config:
        env_file = _ENV_FILES
        env_file_encoding = "utf-8"
        extra = "ignore"

    def get_hindsight_llm_key(self) -> str:
        return self.HINDSIGHT_LLM_API_KEY or self.LLM_API_KEY

    def get_hindsight_llm_base_url(self) -> str | None:
        return self.HINDSIGHT_LLM_BASE_URL or self.LLM_BASE_URL or None

    def get_llm_base_url(self) -> str | None:
        return self.LLM_BASE_URL if self.LLM_BASE_URL else None


@lru_cache()
def get_settings() -> Settings:
    return Settings()
