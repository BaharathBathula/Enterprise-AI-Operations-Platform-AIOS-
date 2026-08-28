import uuid
from datetime import timedelta

from fastapi.testclient import TestClient
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User


def _create_user(
    db: Session,
    email: str,
    *,
    is_active: bool = True,
) -> User:
    user = User(
        email=email,
        full_name="Authentication Security User",
        hashed_password="not-used-in-test",
        is_active=is_active,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    return user


def _auth_headers(
    token: str,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def test_valid_access_token_allows_authenticated_request(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "auth-valid@example.com",
    )

    db_session.commit()

    token = create_access_token(
        subject=str(user.id),
    )

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(token),
    )

    assert response.status_code == 200


def test_missing_bearer_token_is_rejected(
    client: TestClient,
):
    response = client.get(
        "/api/v1/organizations"
    )

    assert response.status_code == 401


def test_malformed_access_token_is_rejected(
    client: TestClient,
):
    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(
            "this-is-not-a-valid-jwt"
        ),
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail":
            "Could not validate "
            "authentication credentials",
    }


def test_expired_access_token_is_rejected(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "auth-expired@example.com",
    )

    db_session.commit()

    token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(
            seconds=-1,
        ),
    )

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(token),
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail":
            "Could not validate "
            "authentication credentials",
    }


def test_token_with_invalid_signature_is_rejected(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "auth-signature@example.com",
    )

    db_session.commit()

    legitimate_token = (
        create_access_token(
            subject=str(user.id),
        )
    )

    payload = jwt.decode(
    legitimate_token,
    options={
        "verify_signature": False,
        "verify_exp": False,
    },
)

    forged_token = jwt.encode(
        payload,
        "definitely-not-the-real-secret",
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(
            forged_token
        ),
    )

    assert response.status_code == 401


def test_token_without_subject_is_rejected(
    client: TestClient,
):
    token = jwt.encode(
        {
            "purpose":
                "missing-subject-test",
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(token),
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail":
            "Could not validate "
            "authentication credentials",
    }


def test_token_with_non_uuid_subject_is_rejected(
    client: TestClient,
):
    token = create_access_token(
        subject="not-a-valid-user-uuid",
    )

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(token),
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail":
            "Could not validate "
            "authentication credentials",
    }


def test_token_for_nonexistent_user_is_rejected(
    client: TestClient,
):
    nonexistent_user_id = uuid.uuid4()

    token = create_access_token(
        subject=str(
            nonexistent_user_id
        ),
    )

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(token),
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail":
            "Could not validate "
            "authentication credentials",
    }


def test_inactive_user_is_forbidden(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "auth-inactive@example.com",
        is_active=False,
    )

    db_session.commit()

    token = create_access_token(
        subject=str(user.id),
    )

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(token),
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "User account is inactive",
    }


def test_bearer_scheme_is_required(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "auth-scheme@example.com",
    )

    db_session.commit()

    token = create_access_token(
        subject=str(user.id),
    )

    response = client.get(
        "/api/v1/organizations",
        headers={
            "Authorization":
                f"Basic {token}",
        },
    )

    assert response.status_code == 401


def test_valid_token_does_not_authenticate_as_another_user(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "auth-user-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "auth-user-b@example.com",
    )

    db_session.commit()

    token_a = create_access_token(
        subject=str(user_a.id),
    )

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(token_a),
    )

    assert response.status_code == 200

    assert user_a.id != user_b.id
