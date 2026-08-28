from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import get_db
from app.main import app

REQUEST_ID_HEADER = "X-Request-ID"


class FailingSession:
    def execute(self, statement):
        raise SQLAlchemyError(
            "database connection failed"
        )


def override_get_db_with_failure():
    database = FailingSession()

    try:
        yield database
    finally:
        pass


def test_liveness_returns_200(
    client: TestClient,
):
    response = client.get(
        "/api/v1/health/live"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "alive",
        "service": "AIOS Backend",
    }

    assert (
        REQUEST_ID_HEADER
        in response.headers
    )


def test_readiness_returns_200_when_database_available(
    client: TestClient,
):
    response = client.get(
        "/api/v1/health/ready"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
        "service": "AIOS Backend",
        "database": "available",
    }

    assert (
        REQUEST_ID_HEADER
        in response.headers
    )


def test_readiness_returns_503_when_database_unavailable():
    app.dependency_overrides[
        get_db
    ] = override_get_db_with_failure

    client = TestClient(app)

    try:
        response = client.get(
            "/api/v1/health/ready"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503

    assert response.json() == {
        "status": "not_ready",
        "service": "AIOS Backend",
        "database": "unavailable",
    }

    assert (
        REQUEST_ID_HEADER
        in response.headers
    )


def test_readiness_failure_does_not_leak_database_error():
    app.dependency_overrides[
        get_db
    ] = override_get_db_with_failure

    client = TestClient(app)

    try:
        response = client.get(
            "/api/v1/health/ready"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503

    response_text = response.text.lower()

    assert (
        "database connection failed"
        not in response_text
    )

    assert "sqlalchemy" not in response_text
    assert "traceback" not in response_text
