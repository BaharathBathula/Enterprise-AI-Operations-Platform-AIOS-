import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
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
        full_name="Agent RBAC User",
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
        slug=f"agent-rbac-{uuid.uuid4()}",
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


def _auth_headers(
    user: User,
) -> dict[str, str]:
    token = create_access_token(
        subject=str(user.id),
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_viewer_cannot_run_agent(
    client: TestClient,
    db_session: Session,
):
    viewer = _create_user(
        db_session,
        "agent-viewer@example.com",
    )

    organization = _create_organization(
        db_session,
        "Agent Viewer Org",
    )

    _add_membership(
        db_session,
        organization,
        viewer,
        OrganizationRole.viewer,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        headers=_auth_headers(viewer),
        json={
            "message": "Create a critical incident",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Organization write access required",
    }


def test_member_can_run_agent(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "agent-member@example.com",
    )

    organization = _create_organization(
        db_session,
        "Agent Member Org",
    )

    _add_membership(
        db_session,
        organization,
        member,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        headers=_auth_headers(member),
        json={
            "message": "What tools are available?",
        },
    )

    assert response.status_code == 200


def test_admin_can_run_agent(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "agent-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Agent Admin Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        headers=_auth_headers(admin),
        json={
            "message": "What tools are available?",
        },
    )

    assert response.status_code == 200


def test_owner_can_run_agent(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "agent-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Agent Owner Org",
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        headers=_auth_headers(owner),
        json={
            "message": "What tools are available?",
        },
    )

    assert response.status_code == 200


def test_foreign_tenant_user_cannot_run_agent(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "agent-foreign-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "agent-foreign-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Agent Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Agent Tenant B",
    )

    _add_membership(
        db_session,
        organization_a,
        user_a,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization_b,
        user_b,
        OrganizationRole.owner,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_b.id}/agent"
        ),
        headers=_auth_headers(user_a),
        json={
            "message": "Run an action",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Organization not found",
    }


def test_unauthenticated_user_cannot_run_agent(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "agent-unauth-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Agent Protected Org",
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/agent"
        ),
        json={
            "message": "Run an action",
        },
    )

    assert response.status_code == 401
