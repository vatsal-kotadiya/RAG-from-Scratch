"""Central application configuration. All values come from environment variables."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BACKEND_DIR / ".env"), extra="ignore")

    APP_ENV: str = "development"
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    MIN_RETRIEVAL_SCORE: float = 0.3

    EMBEDDING_PROVIDER: str = "sentence_transformers"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    DATABASE_URL: str = "sqlite:///./data/app.db"

    MAX_FILE_SIZE_MB: int = 20
    UPLOAD_DIR: str = "./data/uploads"

    def resolve_path(self, value: str) -> Path:
        p = Path(value)
        return p if p.is_absolute() else (BACKEND_DIR / p)

    @property
    def chroma_dir(self) -> Path:
        return self.resolve_path(self.CHROMA_PERSIST_DIRECTORY)

    @property
    def upload_dir(self) -> Path:
        return self.resolve_path(self.UPLOAD_DIR)

    @property
    def sqlite_path(self) -> Path:
        url = self.DATABASE_URL
        path = url.split("sqlite:///", 1)[1] if url.startswith("sqlite:///") else "./data/app.db"
        return self.resolve_path(path)


settings = Settings()
