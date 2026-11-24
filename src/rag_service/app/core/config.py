from pydantic import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "rag_service"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "gemscout_knowledge"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
