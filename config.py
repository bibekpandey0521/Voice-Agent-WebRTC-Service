"""Application settings loaded from .env."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings."""

    APP_PORT: int = 7860
    WHISPER_SIZE: str = "tiny.en"
    OLLAMA_MODEL: str = "llama3.2:1b"
    KOKORO_VOICE: str = "af_heart"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"


settings = Settings()
