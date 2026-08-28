import json
import logging
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import (
    unhandled_exception_handler,
)
from app.middleware.request_id import RequestIDMiddleware


REQUEST_ID_HEADER = "X-Request-ID"


def _create_test_client() -> TestClient:
    app = FastAPI()

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )

    app.add_middleware(
        RequestIDMiddleware,
    )

    @app.get("/explode")
    def explode() -> None:
        raise RuntimeError(
            "sensitive-internal-error"
        )

    return TestClient(
        app,
        raise_server_exceptions=False,
    )


def test_unhandled_exception_returns_500():
    client = _create_test_client()

    response = client.get(
        "/explode"
    )

    assert response.status_code == 500

    body = response.json()

    assert body["detail"] == (
        "Internal server error"
    )

    assert body["request_id"] is not None


def test_unhandled_exception_response_matches_request_id_header():
    client = _create_test_client()

    response = client.get(
        "/explode"
    )

    assert response.status_code == 500

    response_request_id = response.headers[
        REQUEST_ID_HEADER
    ]

    body_request_id = response.json()[
        "request_id"
    ]

    assert (
        body_request_id
        == response_request_id
    )

    parsed_request_id = uuid.UUID(
        body_request_id
    )

    assert (
        str(parsed_request_id)
        == body_request_id
    )


def test_unhandled_exception_preserves_incoming_request_id():
    client = _create_test_client()

    request_id = str(
        uuid.uuid4()
    )

    response = client.get(
        "/explode",
        headers={
            REQUEST_ID_HEADER: request_id,
        },
    )

    assert response.status_code == 500

    assert (
        response.headers[
            REQUEST_ID_HEADER
        ]
        == request_id
    )

    assert (
        response.json()["request_id"]
        == request_id
    )


def test_unhandled_exception_does_not_leak_internal_error():
    client = _create_test_client()

    response = client.get(
        "/explode"
    )

    assert response.status_code == 500

    serialized_body = json.dumps(
        response.json()
    )

    assert (
        "sensitive-internal-error"
        not in serialized_body
    )

    assert "RuntimeError" not in serialized_body

    assert "traceback" not in serialized_body.lower()


def test_unhandled_exception_is_logged_with_request_id(
    caplog,
):
    client = _create_test_client()

    caplog.set_level(
        logging.ERROR,
        logger="app.errors",
    )

    request_id = str(
        uuid.uuid4()
    )

    response = client.get(
        "/explode",
        headers={
            REQUEST_ID_HEADER: request_id,
        },
    )

    assert response.status_code == 500

    records = [
        record
        for record in caplog.records
        if record.name == "app.errors"
    ]

    assert records

    payload = json.loads(
        records[-1].getMessage()
    )

    assert payload["event"] == (
        "unhandled_exception"
    )

    assert (
        payload["request_id"]
        == request_id
    )

    assert payload["method"] == "GET"
    assert payload["path"] == "/explode"

    assert (
        payload["exception_type"]
        == "RuntimeError"
    )
