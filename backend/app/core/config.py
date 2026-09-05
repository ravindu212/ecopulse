from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "EcoPulse API"
    environment: str = "development"

    database_url: str
    frontend_origin: str = "http://localhost:3000"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    climate_http_timeout_seconds: float = 10.0
    climate_http_max_response_bytes: int = 2_000_000
    climate_co2_url: str = (
        "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_trend_gl.csv"
    )
    climate_co2_ttl_seconds: int = 21_600
    climate_co2_history_limit: int = 60
    climate_eonet_url: str = "https://eonet.gsfc.nasa.gov/api/v3/events"
    climate_events_ttl_seconds: int = 900

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIRECTORY / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
