from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    llm_api_key: str
    llm_model: str = "gpt-4o-mini-2024-07-18"

    log_level: str = "INFO"
    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
