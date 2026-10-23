from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    secret_key: SecretStr
    access_token_expire_minutes: int = 30
    database_url: str = "postgresql+asyncpg://library:library@localhost:5432/library"
    debug: bool = False


settings = Settings()
