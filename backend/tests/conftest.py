import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401
from app.db.base import Base
from app.db.database import get_db
from app.main import app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/aios_test",
)


test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(
    scope="session",
    autouse=True,
)
def test_database_schema() -> Generator[
    None,
    None,
    None,
]:
    # AIOS uses pgvector for document embeddings.
    # The extension must exist before SQLAlchemy
    # creates the document_chunks table.
    with test_engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE EXTENSION IF NOT EXISTS vector"
        )

    Base.metadata.drop_all(
        bind=test_engine,
    )

    Base.metadata.create_all(
        bind=test_engine,
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine,
    )


@pytest.fixture()
def db_session() -> Generator[
    Session,
    None,
    None,
]:
    connection = test_engine.connect()

    transaction = connection.begin()

    session = TestingSessionLocal(
        bind=connection,
    )

    try:
        yield session

    finally:
        session.close()

        transaction.rollback()

        connection.close()


@pytest.fixture()
def client(
    db_session: Session,
) -> Generator[
    TestClient,
    None,
    None,
]:
    def override_get_db() -> Generator[
        Session,
        None,
        None,
    ]:
        yield db_session

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
