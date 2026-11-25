from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    countries_url: str = "https://countries.trevorblades.com/"
    geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    weather_url: str = "https://api.open-meteo.com/v1/forecast"
    nbu_url: str = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"

    timeout: float = 5
    redis_url: str = "redis://127.0.0.1:6379/0"
    cache_ttl: int = 600


settings = Settings()
