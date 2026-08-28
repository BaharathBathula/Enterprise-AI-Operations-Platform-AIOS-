import uuid
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.models.organization import Organization
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User
from app.services.rate_limit_service import (
    RateLimitResult,
)


REQUEST_ID_HEADER = "X-Request-ID"


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
    *,
    request_id: str | None = None,
) -> dict[str, str]:
    from app.core.security import create_access_token

    token = create_access_token(
        subject=str(user.id),
    )

    headers = {
        "Authorization": f"Bearer {token}",
    }

    if request_id is not None:
        headers[REQUEST_ID_HEADER] = request_id

    return headers


def _deny_rate_limit(
    monkeypatch,
    *,
    limit: int = 100,
    remaining: int = 0,
    retry_after_seconds: int | None = 30,
):
    check_mock = MagicMock(
        return_value=RateLimitResult(
            allowed=False,
            limit=limit,
            remaining=remaining,
            retry_after_seconds=retry_after_seconds,
        )
    )

    monkeypatch.setattr(
        "app.api.v1.agent.rate_limiter.check",
        check_mock,
    )

    return check_mock


def _allow_rate_limit(
    monkeypatch,
    *,
    limit: int = 100,
    remaining: int = 99,
):
    check_mock = MagicMock(
        return_value=RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=remaining,
            retry_after_seconds=None,
        )
    )

    monkeypatch.setattr(
        "app.api.v1.agent.rate_limiter.check",
        check_mock,
    )

    return check_mock


def test_agent_rate_limit_denied_returns_429(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(db_session)
    organization = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    check_mock = _deny_rate_limit(
        monkeypatch,
        limit=100,
        retry_after_seconds=37,
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

    assert response.headers["Retry-After"] == "37"
    assert response.headers["X-RateLimit-Limit"] == "100"
    assert response.headers["X-RateLimit-Remaining"] == "0"

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
    user = _create_user(db_session)
    organization = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    _deny_rate_limit(
        monkeypatch,
        limit=50,
        retry_after_seconds=None,
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

    assert "Retry-After" not in response.headers
    assert response.headers["X-RateLimit-Limit"] == "50"
    assert response.headers["X-RateLimit-Remaining"] == "0"


def test_denied_agent_request_does_not_create_orchestrator(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(db_session)
    organization = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    _deny_rate_limit(
        monkeypatch,
        retry_after_seconds=60,
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


def test_rate_limit_denial_creates_audit_log(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(db_session)
    organization = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    _deny_rate_limit(
        monkeypatch,
        retry_after_seconds=42,
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Trigger rate limit audit",
        },
        headers=_auth_headers(user),
    )

    assert response.status_code == 429

    db_session.expire_all()

    statement = select(AuditLog).where(
        AuditLog.organization_id == organization.id,
        AuditLog.user_id == user.id,
        AuditLog.action == "agent.rate_limit_denied",
    )

    audit_log = db_session.scalar(statement)

    assert audit_log is not None
    assert audit_log.event_type == "authorization"
    assert audit_log.outcome == "denied"
    assert audit_log.resource_type == "agent_execution"
    assert audit_log.organization_id == organization.id
    assert audit_log.user_id == user.id

    assert audit_log.details is not None
    assert audit_log.details["limit"] == 100
    assert audit_log.details["remaining"] == 0
    assert audit_log.details["retry_after_seconds"] == 42


def test_rate_limit_audit_is_tenant_scoped(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user_a = _create_user(db_session)
    user_b = _create_user(db_session)

    organization_a = _create_organization(db_session)
    organization_b = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user_a,
        organization=organization_a,
    )

    _create_membership(
        db_session,
        user=user_b,
        organization=organization_b,
    )

    db_session.commit()

    _deny_rate_limit(
        monkeypatch,
        retry_after_seconds=30,
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/agent"
        ),
        json={
            "message": "Tenant scoped rate limit",
        },
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 429

    db_session.expire_all()

    tenant_a_statement = select(AuditLog).where(
        AuditLog.organization_id == organization_a.id,
        AuditLog.action == "agent.rate_limit_denied",
    )

    tenant_b_statement = select(AuditLog).where(
        AuditLog.organization_id == organization_b.id,
        AuditLog.action == "agent.rate_limit_denied",
    )

    tenant_a_log = db_session.scalar(
        tenant_a_statement
    )

    tenant_b_log = db_session.scalar(
        tenant_b_statement
    )

    assert tenant_a_log is not None
    assert tenant_a_log.user_id == user_a.id
    assert tenant_b_log is None


def test_allowed_agent_request_reaches_orchestrator(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(db_session)
    organization = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    check_mock = _allow_rate_limit(
        monkeypatch,
        limit=100,
        remaining=99,
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

    assert response.headers["X-RateLimit-Limit"] == "100"
    assert response.headers["X-RateLimit-Remaining"] == "99"
    assert "Retry-After" not in response.headers

    check_mock.assert_called_once_with(
        key=(
            f"agent:"
            f"{organization.id}:"
            f"{user.id}"
        )
    )

    orchestrator_class.assert_called_once()
    handle_mock.assert_called_once()

    call_kwargs = handle_mock.call_args.kwargs

    assert (
        call_kwargs["user_input"]
        == "Allowed task"
    )

    context = call_kwargs["context"]

    assert context.organization_id == organization.id
    assert context.user_id == user.id


def test_allowed_agent_request_does_not_create_rate_limit_denial_audit(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(db_session)
    organization = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    _allow_rate_limit(
        monkeypatch
    )

    result = MagicMock()
result.success = True
result.message = "Allowed"
result.error = None
result.data = {}

    orchestrator_instance = MagicMock()
    orchestrator_instance.handle.return_value = result

    monkeypatch.setattr(
        "app.api.v1.agent.AgentOrchestrator",
        MagicMock(
            return_value=orchestrator_instance
        ),
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Allowed request",
        },
        headers=_auth_headers(user),
    )

    assert response.status_code == 200

    db_session.expire_all()

    statement = select(AuditLog).where(
        AuditLog.organization_id == organization.id,
        AuditLog.user_id == user.id,
        AuditLog.action == "agent.rate_limit_denied",
    )

    audit_log = db_session.scalar(statement)

    assert audit_log is None


def test_rate_limit_audit_request_id_matches_response_header(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(db_session)
    organization = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    _deny_rate_limit(
        monkeypatch,
        retry_after_seconds=25,
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Correlate request ID",
        },
        headers=_auth_headers(user),
    )

    assert response.status_code == 429

    response_request_id = response.headers[
        REQUEST_ID_HEADER
    ]

    db_session.expire_all()

    statement = select(AuditLog).where(
        AuditLog.organization_id == organization.id,
        AuditLog.user_id == user.id,
        AuditLog.action == "agent.rate_limit_denied",
    )

    audit_log = db_session.scalar(statement)

    assert audit_log is not None
    assert audit_log.details is not None

    assert (
        audit_log.details["request_id"]
        == response_request_id
    )


def test_rate_limit_audit_preserves_incoming_request_id(
    client: TestClient,
    db_session,
    monkeypatch,
):
    user = _create_user(db_session)
    organization = _create_organization(db_session)

    _create_membership(
        db_session,
        user=user,
        organization=organization,
    )

    db_session.commit()

    _deny_rate_limit(
        monkeypatch,
        retry_after_seconds=20,
    )

    request_id = str(
        uuid.uuid4()
    )

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Preserve request ID",
        },
        headers=_auth_headers(
            user,
            request_id=request_id,
        ),
    )

    assert response.status_code == 429

    assert (
        response.headers[
            REQUEST_ID_HEADER
        ]
        == request_id
    )

    db_session.expire_all()

    statement = select(AuditLog).where(
        AuditLog.organization_id == organization.id,
        AuditLog.user_id == user.id,
        AuditLog.action == "agent.rate_limit_denied",
    )

    audit_log = db_session.scalar(statement)

    assert audit_log is not None
    assert audit_log.details is not None

    assert (
        audit_log.details["request_id"]
        == request_id
    )
