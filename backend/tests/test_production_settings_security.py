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
    )

    assert settings.ENVIRONMENT == "production"
