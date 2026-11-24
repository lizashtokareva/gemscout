from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str
    s3_secret_key: SecretStr
    s3_bucket: str = "gemscout-images"
    s3_region: str = "us-east-1"


settings = Settings()
