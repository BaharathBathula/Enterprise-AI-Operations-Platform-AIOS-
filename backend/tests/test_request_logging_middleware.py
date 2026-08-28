import json
import logging
import uuid

from fastapi.testclient import TestClient

REQUEST_ID_HEADER = "X-Request-ID"


def _parse_http_request_log(
    caplog,
) -> dict:
    records = [
        record
        for record in caplog.records
        if record.name == "uvicorn.access"
    ]

    assert records

    payload = json.loads(
        records[-1].getMessage()
    )

    assert payload["event"] == "http_request"

    return payload


def test_request_log_contains_request_metadata(
    client: TestClient,
    caplog,
):
    caplog.set_level(
        logging.INFO,
        logger="uvicorn.access",
    )

    response = client.get("/")

    assert response.status_code == 200

    payload = _parse_http_request_log(
        caplog
    )

    assert payload["method"] == "GET"
    assert payload["path"] == "/"
    assert payload["status_code"] == 200

    assert isinstance(
        payload["duration_ms"],
        (int, float),
    )

    assert payload["duration_ms"] >= 0


def test_request_log_uses_response_request_id(
    client: TestClient,
    caplog,
):
    caplog.set_level(
        logging.INFO,
        logger="uvicorn.access",
    )

    response = client.get("/")

    assert response.status_code == 200

    response_request_id = response.headers[
        REQUEST_ID_HEADER
    ]

    payload = _parse_http_request_log(
        caplog
    )

    assert (
        payload["request_id"]
        == response_request_id
    )


def test_request_log_preserves_incoming_request_id(
    client: TestClient,
    caplog,
):
    caplog.set_level(
        logging.INFO,
        logger="uvicorn.access",
    )

    request_id = str(
        uuid.uuid4()
    )

    response = client.get(
        "/",
        headers={
            REQUEST_ID_HEADER: request_id,
        },
    )

    assert response.status_code == 200

    payload = _parse_http_request_log(
        caplog
    )

    assert payload["request_id"] == request_id

    assert (
        response.headers[REQUEST_ID_HEADER]
        == request_id
    )


def test_separate_requests_have_separate_log_ids(
    client: TestClient,
    caplog,
):
    caplog.set_level(
        logging.INFO,
        logger="uvicorn.access",
    )

    first_response = client.get("/")
    second_response = client.get("/")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    records = [
        record
        for record in caplog.records
        if record.name == "uvicorn.access"
    ]

    assert len(records) >= 2

    first_payload = json.loads(
        records[-2].getMessage()
    )

    second_payload = json.loads(
        records[-1].getMessage()
    )

    assert (
        first_payload["request_id"]
        != second_payload["request_id"]
    )

    assert (
        first_payload["request_id"]
        == first_response.headers[
            REQUEST_ID_HEADER
        ]
    )

    assert (
        second_payload["request_id"]
        == second_response.headers[
            REQUEST_ID_HEADER
        ]
    )


def test_request_log_does_not_include_sensitive_fields(
    client: TestClient,
    caplog,
):
    caplog.set_level(
        logging.INFO,
        logger="uvicorn.access",
    )

    response = client.get(
        "/?token=secret-value",
        headers={
            "Authorization":
                "Bearer secret-token",
        },
    )

    assert response.status_code == 200

    payload = _parse_http_request_log(
        caplog
    )

    assert "query" not in payload
    assert "headers" not in payload
    assert "authorization" not in payload
    assert "body" not in payload

    serialized_payload = json.dumps(
        payload
    )

    assert "secret-value" not in serialized_payload
    assert "secret-token" not in serialized_payload
