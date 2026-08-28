from typing import Self

from pydantic import model_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    # Application
    APP_NAME: str = (
        "Enterprise AI Operations Platform"
    )
    APP_VERSION: str = "0.1.0"

    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Storage
    STORAGE_PATH: str = "storage"

    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg2://"
        "aios_user:password@localhost:5432/aios"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Embeddings
    EMBEDDING_MODEL: str = (
        "text-embedding-3-small"
    )
    EMBEDDING_DIMENSIONS: int = 1536

    # Document Processing
    DOCUMENT_CHUNK_SIZE: int = 1200
    DOCUMENT_CHUNK_OVERLAP: int = 200

    # RAG / Chat
    CHAT_MODEL: str = "gpt-4.1-mini"
    RAG_TOP_K: int = 5

    # Authentication
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @model_validator(mode="after")
    def validate_production_security(
        self,
    ) -> Self:
        environment = (
            self.ENVIRONMENT.strip().lower()
        )

        if environment not in {
            "production",
            "prod",
        }:
            return self

        jwt_secret = self.JWT_SECRET_KEY.strip()

        insecure_jwt_secrets = {
            "",
            "development-only-change-this-secret",
            "replace-with-a-long-random-secret",
        }

        if (
            len(jwt_secret) < 32
            or jwt_secret in insecure_jwt_secrets
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be at least "
                "32 characters and must not use "
                "a development placeholder in "
                "production"
            )

        insecure_database_markers = (
            "replace-with-a-secure-password",
            "aios_user:aios_password@",
            "aios_user:password@",
            "postgres:postgres@",
        )

        if any(
            marker in self.DATABASE_URL
            for marker in insecure_database_markers
        ):
            raise ValueError(
                "DATABASE_URL must not use "
                "development placeholder "
                "credentials in production"
            )

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
