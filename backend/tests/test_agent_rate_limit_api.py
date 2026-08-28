import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.models.organization import Organization
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User
from app.services.rate_limit_service import (
    RateLimitResult,
)


def _create_user(
    db_session,
) -> User:
    user = User(
        email=f"rate-limit-{uuid.uuid4()}@example.com",
        full_name="Rate Limit Test User",
        hashed_password="not-used",
        is_active=True,
        is_superuser=False,
    )

    db_session.add(user)
    db_session.flush()

    return user


def _create_organization(
    db_session,
) -> Organization:
    organization = Organization(
        name="Rate Limit Test Organization",
        slug=f"rate-limit-{uuid.uuid4()}",
    )

    db_session.add(organization)
    db_session.flush()

    return organization


def _create_membership(
    db_session,
    *,
    user: User,
    organization: Organization,
) -> OrganizationMember:
    membership = OrganizationMember(
        user_id=user.id,
        organization_id=organization.id,
        role=OrganizationRole.member,
    )

    db_session.add(membership)
    db_session.flush()

    return membership


def _auth_headers(
    user: User,
) -> dict[str, str]:
    from app.core.security import create_access_token

    token = create_access_token(
        subject=str(user.id),
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_agent_rate_limit_denied_returns_429(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(
        db_session
    )

    organization = _create_organization(
        db_session
    )

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    denied_result = RateLimitResult(
        allowed=False,
        limit=100,
        remaining=0,
        retry_after_seconds=37,
    )

    check_mock = MagicMock(
        return_value=denied_result
    )

    monkeypatch.setattr(
        "app.api.v1.agent.rate_limiter.check",
        check_mock,
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Run an expensive task",
        },
        headers=_auth_headers(user),
    )

    assert response.status_code == 429

    assert response.json() == {
        "detail": "Rate limit exceeded",
    }

    assert response.headers[
        "Retry-After"
    ] == "37"

    assert response.headers[
        "X-RateLimit-Limit"
    ] == "100"

    assert response.headers[
        "X-RateLimit-Remaining"
    ] == "0"

    check_mock.assert_called_once_with(
        key=(
            f"agent:"
            f"{organization.id}:"
            f"{user.id}"
        )
    )


def test_agent_rate_limit_without_retry_after(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(
        db_session
    )

    organization = _create_organization(
        db_session
    )

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    denied_result = RateLimitResult(
        allowed=False,
        limit=50,
        remaining=0,
        retry_after_seconds=None,
    )

    monkeypatch.setattr(
        "app.api.v1.agent.rate_limiter.check",
        MagicMock(
            return_value=denied_result
        ),
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Run task",
        },
        headers=_auth_headers(user),
    )

    assert response.status_code == 429

    assert (
        "Retry-After"
        not in response.headers
    )

    assert response.headers[
        "X-RateLimit-Limit"
    ] == "50"

    assert response.headers[
        "X-RateLimit-Remaining"
    ] == "0"


def test_denied_agent_request_does_not_create_orchestrator(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(
        db_session
    )

    organization = _create_organization(
        db_session
    )

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    monkeypatch.setattr(
        "app.api.v1.agent.rate_limiter.check",
        MagicMock(
            return_value=RateLimitResult(
                allowed=False,
                limit=100,
                remaining=0,
                retry_after_seconds=60,
            )
        ),
    )

    orchestrator_mock = MagicMock()

    monkeypatch.setattr(
        "app.api.v1.agent.AgentOrchestrator",
        orchestrator_mock,
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Do not execute this",
        },
        headers=_auth_headers(user),
    )

    assert response.status_code == 429

    orchestrator_mock.assert_not_called()


def test_allowed_agent_request_reaches_orchestrator(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(
        db_session
    )

    organization = _create_organization(
        db_session
    )

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    check_mock = MagicMock(
        return_value=RateLimitResult(
            allowed=True,
            limit=100,
            remaining=99,
            retry_after_seconds=None,
        )
    )

    monkeypatch.setattr(
        "app.api.v1.agent.rate_limiter.check",
        check_mock,
    )

    result = MagicMock()
    result.success = True
    result.message = "Agent completed"
    result.error = None
    result.data = {
        "test": True,
    }

    handle_mock = MagicMock(
        return_value=result
    )

    orchestrator_instance = MagicMock()
    orchestrator_instance.handle = handle_mock

    orchestrator_class = MagicMock(
        return_value=orchestrator_instance
    )

    monkeypatch.setattr(
        "app.api.v1.agent.AgentOrchestrator",
        orchestrator_class,
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Allowed task",
        },
        headers=_auth_headers(user),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "Agent completed"
    assert body["error"] is None

    check_mock.assert_called_once_with(
        key=(
            f"agent:"
            f"{organization.id}:"
            f"{user.id}"
        )
    )

    orchestrator_class.assert_called_once()

    handle_mock.assert_called_once()

    call_kwargs = (
        handle_mock.call_args.kwargs
    )

    assert (
        call_kwargs["user_input"]
        == "Allowed task"
    )

    context = call_kwargs[
        "context"
    ]

    assert (
        context.organization_id
        == organization.id
    )

    assert context.user_id == user.id
