from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    Values are loaded from environment variables / a .env file.
    Never hardcode credentials here.
    """

    APP_ENV: str = "development"
    APP_PORT: int = 8000

    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
