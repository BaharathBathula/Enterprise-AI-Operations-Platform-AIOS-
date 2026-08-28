import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.audit_log import AuditLog
from app.models.organization import Organization
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User


def _create_user(
    db: Session,
    email: str,
) -> User:
    user = User(
        email=email,
        full_name="Audit Security Test User",
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
        slug=f"audit-{uuid.uuid4()}",
    )

    db.add(organization)
    db.flush()

    return organization


def _add_membership(
    db: Session,
    organization: Organization,
    user: User,
    role: OrganizationRole,
) -> OrganizationMember:
    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role=role,
    )

    db.add(membership)
    db.flush()

    return membership


def _create_audit_log(
    db: Session,
    organization: Organization,
    user: User,
    action: str,
    resource_id: str,
    *,
    event_type: str = "security",
    outcome: str = "success",
) -> AuditLog:
    audit_log = AuditLog(
        organization_id=organization.id,
        user_id=user.id,
        event_type=event_type,
        action=action,
        outcome=outcome,
        resource_type="security_test",
        resource_id=resource_id,
        details={
            "source": "integration-test",
        },
    )

    db.add(audit_log)
    db.flush()

    return audit_log


def _auth_headers(
    user: User,
) -> dict[str, str]:
    token = create_access_token(
        subject=str(user.id),
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_member_cannot_read_audit_logs(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "audit-member@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Member Org",
    )

    _add_membership(
        db_session,
        organization,
        member,
        OrganizationRole.member,
    )

    _create_audit_log(
        db_session,
        organization,
        member,
        "security.member.test",
        "member-resource",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
        ),
        headers=_auth_headers(member),
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Organization administrator access required",
    }


def test_admin_can_read_organization_audit_logs(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "audit-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Admin Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    audit_log = _create_audit_log(
        db_session,
        organization,
        admin,
        "security.admin.test",
        "admin-resource",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 200

    body = response.json()

    audit_item = next(
        item
        for item in body
        if item["id"] == str(audit_log.id)
    )

    assert audit_item["event_type"] == "security"
    assert audit_item["outcome"] == "success"
    assert audit_item["action"] == "security.admin.test"
    assert audit_item["resource_type"] == "security_test"
    assert audit_item["resource_id"] == "admin-resource"

    ids = {
        item["id"]
        for item in body
    }

    assert str(audit_log.id) in ids


def test_owner_can_read_organization_audit_logs(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "audit-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Owner Org",
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    audit_log = _create_audit_log(
        db_session,
        organization,
        owner,
        "security.owner.test",
        "owner-resource",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
        ),
        headers=_auth_headers(owner),
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()
    }

    assert str(audit_log.id) in ids


def test_admin_cannot_access_foreign_organization_audit_endpoint(
    client: TestClient,
    db_session: Session,
):
    admin_a = _create_user(
        db_session,
        "audit-admin-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "audit-user-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Audit Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Audit Tenant B",
    )

    _add_membership(
        db_session,
        organization_a,
        admin_a,
        OrganizationRole.admin,
    )

    _add_membership(
        db_session,
        organization_b,
        user_b,
        OrganizationRole.member,
    )

    _create_audit_log(
        db_session,
        organization_b,
        user_b,
        "tenant-b.secret.action",
        "tenant-b-secret",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_b.id}/audit"
        ),
        headers=_auth_headers(admin_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Organization not found",
    }


def test_audit_list_does_not_leak_foreign_tenant_logs(
    client: TestClient,
    db_session: Session,
):
    admin_a = _create_user(
        db_session,
        "audit-scope-admin-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "audit-scope-user-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Audit Scope A",
    )

    organization_b = _create_organization(
        db_session,
        "Audit Scope B",
    )

    _add_membership(
        db_session,
        organization_a,
        admin_a,
        OrganizationRole.admin,
    )

    _add_membership(
        db_session,
        organization_b,
        user_b,
        OrganizationRole.member,
    )

    audit_a = _create_audit_log(
        db_session,
        organization_a,
        admin_a,
        "tenant-a.visible.action",
        "visible-resource",
    )

    audit_b = _create_audit_log(
        db_session,
        organization_b,
        user_b,
        "tenant-b.hidden.action",
        "hidden-resource",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/audit"
        ),
        headers=_auth_headers(admin_a),
    )

    assert response.status_code == 200

    body = response.json()

    ids = {
        item["id"]
        for item in body
    }

    actions = {
        item["action"]
        for item in body
    }

    assert str(audit_a.id) in ids
    assert str(audit_b.id) not in ids

    assert (
        "tenant-a.visible.action"
        in actions
    )

    assert (
        "tenant-b.hidden.action"
        not in actions
    )


def test_audit_event_type_filter(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "audit-event-filter@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Event Filter Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    authorization_log = _create_audit_log(
        db_session,
        organization,
        admin,
        "authorization.denied.test",
        "authorization-resource",
        event_type="authorization",
        outcome="denied",
    )

    security_log = _create_audit_log(
        db_session,
        organization,
        admin,
        "security.success.test",
        "security-resource",
        event_type="security",
        outcome="success",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
            "?event_type=authorization"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()
    }

    assert str(authorization_log.id) in ids
    assert str(security_log.id) not in ids

    assert all(
        item["event_type"] == "authorization"
        for item in response.json()
    )


def test_audit_outcome_filter(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "audit-outcome-filter@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Outcome Filter Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    denied_log = _create_audit_log(
        db_session,
        organization,
        admin,
        "authorization.denied.test",
        "denied-resource",
        event_type="authorization",
        outcome="denied",
    )

    success_log = _create_audit_log(
        db_session,
        organization,
        admin,
        "tool.success.test",
        "success-resource",
        event_type="tool_execution",
        outcome="success",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
            "?outcome=denied"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()
    }

    assert str(denied_log.id) in ids
    assert str(success_log.id) not in ids

    assert all(
        item["outcome"] == "denied"
        for item in response.json()
    )


def test_audit_combined_event_type_and_outcome_filter(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "audit-combined-filter@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Combined Filter Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    matching_log = _create_audit_log(
        db_session,
        organization,
        admin,
        "tool.execution.failed",
        "matching-resource",
        event_type="tool_execution",
        outcome="failed",
    )

    wrong_outcome_log = _create_audit_log(
        db_session,
        organization,
        admin,
        "tool.execution.success",
        "wrong-outcome-resource",
        event_type="tool_execution",
        outcome="success",
    )

    wrong_type_log = _create_audit_log(
        db_session,
        organization,
        admin,
        "authorization.failed",
        "wrong-type-resource",
        event_type="authorization",
        outcome="failed",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
            "?event_type=tool_execution"
            "&outcome=failed"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()
    }

    assert str(matching_log.id) in ids
    assert str(wrong_outcome_log.id) not in ids
    assert str(wrong_type_log.id) not in ids

    for item in response.json():
        assert item["event_type"] == "tool_execution"
        assert item["outcome"] == "failed"


def test_audit_filters_do_not_leak_foreign_tenant_logs(
    client: TestClient,
    db_session: Session,
):
    admin_a = _create_user(
        db_session,
        "audit-filter-admin-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "audit-filter-user-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Audit Filter Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Audit Filter Tenant B",
    )

    _add_membership(
        db_session,
        organization_a,
        admin_a,
        OrganizationRole.admin,
    )

    _add_membership(
        db_session,
        organization_b,
        user_b,
        OrganizationRole.member,
    )

    audit_a = _create_audit_log(
        db_session,
        organization_a,
        admin_a,
        "tenant-a.denied",
        "tenant-a-denied",
        event_type="authorization",
        outcome="denied",
    )

    audit_b = _create_audit_log(
        db_session,
        organization_b,
        user_b,
        "tenant-b.denied",
        "tenant-b-denied",
        event_type="authorization",
        outcome="denied",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/audit"
            "?event_type=authorization"
            "&outcome=denied"
        ),
        headers=_auth_headers(admin_a),
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()
    }

    assert str(audit_a.id) in ids
    assert str(audit_b.id) not in ids


def test_audit_limit_is_enforced(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "audit-limit-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Limit Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    for index in range(5):
        _create_audit_log(
            db_session,
            organization,
            admin,
            f"limit.test.{index}",
            f"limit-resource-{index}",
        )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
            "?limit=2"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_invalid_audit_limit_is_rejected(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "audit-invalid-limit@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Invalid Limit Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
            "?limit=501"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 422


def test_empty_audit_event_type_filter_is_rejected(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "audit-empty-event-type@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Empty Event Type Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
            "?event_type="
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 422


def test_empty_audit_outcome_filter_is_rejected(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "audit-empty-outcome@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Empty Outcome Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
            "?outcome="
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 422


def test_unauthenticated_user_cannot_read_audit_logs(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "audit-unauthenticated@example.com",
    )

    organization = _create_organization(
        db_session,
        "Audit Protected Org",
    )

    _add_membership(
        db_session,
        organization,
        user,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/audit"
        )
    )

    assert response.status_code == 401
