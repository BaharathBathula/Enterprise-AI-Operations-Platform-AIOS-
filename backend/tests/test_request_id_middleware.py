import uuid

from fastapi.testclient import TestClient

REQUEST_ID_HEADER = "X-Request-ID"


def test_request_without_request_id_receives_generated_id(
    client: TestClient,
):
    response = client.get("/")

    assert response.status_code == 200

    request_id = response.headers.get(
        REQUEST_ID_HEADER
    )

    assert request_id is not None

    parsed_request_id = uuid.UUID(
        request_id
    )

    assert str(parsed_request_id) == request_id


def test_request_id_is_different_for_separate_requests(
    client: TestClient,
):
    first_response = client.get("/")
    second_response = client.get("/")

    first_request_id = first_response.headers.get(
        REQUEST_ID_HEADER
    )

    second_request_id = second_response.headers.get(
        REQUEST_ID_HEADER
    )

    assert first_request_id is not None
    assert second_request_id is not None

    assert first_request_id != second_request_id


def test_existing_request_id_is_preserved(
    client: TestClient,
):
    request_id = str(uuid.uuid4())

    response = client.get(
        "/",
        headers={
            REQUEST_ID_HEADER: request_id,
        },
    )

    assert response.status_code == 200

    assert (
        response.headers[REQUEST_ID_HEADER]
        == request_id
    )
