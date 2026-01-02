from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    admin_email: str
    api_key: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore

print(f"App Name: {settings.app_name}")
print(f"Admin: {settings.admin_email}")
print(f"Secret Key: {settings.api_key}")
