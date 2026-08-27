import uuid

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.user import User
from app.services.audit_service import (
    list_organization_audit_logs,
    log_audit_event,
)


def _create_user(
    db: Session,
    email: str,
) -> User:
    user = User(
        email=email,
        full_name="Audit Service Test User",
        hashed_password="not-used-in-test",
        is_active=True,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    return user


def _create_organization(
    db: Session,
    name: str,
) -> Organization:
    organization = Organization(
        name=name,
        slug=f"audit-service-{uuid.uuid4()}",
    )

    db.add(organization)
    db.flush()

    return organization


def test_log_audit_event_records_event_type_and_outcome(
    db_session: Session,
):
    user = _create_user(
        db_session,
        "audit-service-event@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Service Event Org",
    )

    audit_log = log_audit_event(
        db_session,
        organization_id=organization.id,
        user_id=user.id,
        event_type="tool_execution",
        action="tool.execute",
        outcome="approved",
        resource_type="tool",
        resource_id="tool-123",
        details={
            "tool_name": "example_tool",
        },
    )

    assert audit_log.organization_id == organization.id
    assert audit_log.user_id == user.id
    assert audit_log.event_type == "tool_execution"
    assert audit_log.action == "tool.execute"
    assert audit_log.outcome == "approved"
    assert audit_log.resource_type == "tool"
    assert audit_log.resource_id == "tool-123"

    assert audit_log.details == {
        "tool_name": "example_tool",
    }

    assert audit_log.created_at is not None


def test_log_audit_event_uses_safe_defaults(
    db_session: Session,
):
    organization = _create_organization(
        db_session,
        "Audit Service Defaults Org",
    )

    audit_log = log_audit_event(
        db_session,
        organization_id=organization.id,
        action="general.test",
        resource_type="test_resource",
    )

    assert audit_log.event_type == "general"
    assert audit_log.outcome == "success"


def test_log_audit_event_can_record_failure(
    db_session: Session,
):
    organization = _create_organization(
        db_session,
        "Audit Failure Org",
    )

    audit_log = log_audit_event(
        db_session,
        organization_id=organization.id,
        event_type="authorization",
        action="tool.execute",
        outcome="denied",
        resource_type="tool",
        resource_id="restricted-tool",
        details={
            "reason": "approval_required",
        },
    )

    assert audit_log.event_type == "authorization"
    assert audit_log.outcome == "denied"

    assert audit_log.details == {
        "reason": "approval_required",
    }


def test_list_organization_audit_logs_is_tenant_scoped(
    db_session: Session,
):
    organization_a = _create_organization(
        db_session,
        "Audit Service Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Audit Service Tenant B",
    )

    audit_a = log_audit_event(
        db_session,
        organization_id=organization_a.id,
        event_type="security",
        action="tenant.a.action",
        resource_type="test_resource",
    )

    audit_b = log_audit_event(
        db_session,
        organization_id=organization_b.id,
        event_type="security",
        action="tenant.b.action",
        resource_type="test_resource",
    )

    results = list_organization_audit_logs(
        db_session,
        organization_id=organization_a.id,
    )

    ids = {
        audit_log.id
        for audit_log in results
    }

    assert audit_a.id in ids
    assert audit_b.id not in ids
