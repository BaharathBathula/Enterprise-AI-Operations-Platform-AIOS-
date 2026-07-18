from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Enterprise AI Operations Platform"
    APP_VERSION: str = "0.1.0"

    API_V1_PREFIX: str = "/api/v1"

    ENVIRONMENT: str = "development"

    DATABASE_URL: str = (
        "postgresql://aios_user:password@localhost:5432/aios"
    )

    OPENAI_API_KEY: str = ""

    JWT_SECRET_KEY: str = ""

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()
