from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/jobtracker"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "changeme"
    environment: str = "development"


settings = Settings()
