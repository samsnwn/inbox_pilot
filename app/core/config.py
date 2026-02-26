from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    database_url: str
    redis_url: str
    gemini_api_key: str | None = None
    ai_model: str = "gemini-2.5-flash"
    ai_provider: str = "stub"

settings = Settings()