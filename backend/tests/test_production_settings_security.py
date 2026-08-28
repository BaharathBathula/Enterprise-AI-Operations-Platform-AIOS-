import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_development_allows_blank_jwt_secret():
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="development",
        JWT_SECRET_KEY="",
    )

    assert settings.JWT_SECRET_KEY == ""


def test_production_rejects_blank_jwt_secret():
    with pytest.raises(
        ValidationError,
        match="JWT_SECRET_KEY",
    ):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            JWT_SECRET_KEY="",
            DATABASE_URL=(
                "postgresql+psycopg2://"
                "prod_user:secure-db-password"
                "@database:5432/aios"
            ),
            CORS_ORIGINS=(
                "https://app.example.com"
            ),
        )


def test_production_rejects_development_secret():
    with pytest.raises(
        ValidationError,
        match="JWT_SECRET_KEY",
    ):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            JWT_SECRET_KEY=(
                "development-only-change-this-secret"
            ),
            DATABASE_URL=(
                "postgresql+psycopg2://"
                "prod_user:secure-db-password"
                "@database:5432/aios"
            ),
            CORS_ORIGINS=(
                "https://app.example.com"
            ),
        )


def test_production_rejects_placeholder_database():
    with pytest.raises(
        ValidationError,
        match="DATABASE_URL",
    ):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            JWT_SECRET_KEY="x" * 64,
            DATABASE_URL=(
                "postgresql+psycopg2://"
                "aios_user:"
                "replace-with-a-secure-password"
                "@database:5432/aios"
            ),
            CORS_ORIGINS=(
                "https://app.example.com"
            ),
        )


def test_production_rejects_wildcard_cors():
    with pytest.raises(
        ValidationError,
        match="CORS_ORIGINS",
    ):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            JWT_SECRET_KEY="x" * 64,
            DATABASE_URL=(
                "postgresql+psycopg2://"
                "prod_user:secure-db-password"
                "@database:5432/aios"
            ),
            CORS_ORIGINS="*",
        )


def test_production_rejects_localhost_cors():
    with pytest.raises(
        ValidationError,
        match="CORS_ORIGINS",
    ):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            JWT_SECRET_KEY="x" * 64,
            DATABASE_URL=(
                "postgresql+psycopg2://"
                "prod_user:secure-db-password"
                "@database:5432/aios"
            ),
            CORS_ORIGINS=(
                "http://localhost:3000"
            ),
        )


def test_production_rejects_empty_cors():
    with pytest.raises(
        ValidationError,
        match="CORS_ORIGINS",
    ):
        Settings(
            _env_file=None,
            ENVIRONMENT="production",
            JWT_SECRET_KEY="x" * 64,
            DATABASE_URL=(
                "postgresql+psycopg2://"
                "prod_user:secure-db-password"
                "@database:5432/aios"
            ),
            CORS_ORIGINS="",
        )


def test_production_accepts_secure_configuration():
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        JWT_SECRET_KEY="x" * 64,
        DATABASE_URL=(
            "postgresql+psycopg2://"
            "prod_user:secure-db-password"
            "@database:5432/aios"
        ),
        CORS_ORIGINS=(
            "https://app.example.com"
        ),
    )

    assert settings.ENVIRONMENT == "production"
    assert settings.cors_origins == [
        "https://app.example.com"
    ]


def test_multiple_production_cors_origins():
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        JWT_SECRET_KEY="x" * 64,
        DATABASE_URL=(
            "postgresql+psycopg2://"
            "prod_user:secure-db-password"
            "@database:5432/aios"
        ),
        CORS_ORIGINS=(
            "https://app.example.com,"
            "https://admin.example.com"
        ),
    )

    assert settings.cors_origins == [
        "https://app.example.com",
        "https://admin.example.com",
    ]
