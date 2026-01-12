from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GROQ_API_KEY: str
    MODEL_NAME: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()  # type: ignore
