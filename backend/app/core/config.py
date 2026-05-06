from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://meetingtools:meetingtools@localhost:6012/meetingtools"
    secret_key: str = "change-me-in-production"
    audio_storage_path: str = "/data/audio"
    export_storage_path: str = "/data/exports"
    log_level: str = "INFO"
    asr_provider: str = "mock"  # "mock" | "http"
    asr_http_url: str = "http://localhost:6013"


settings = Settings()
