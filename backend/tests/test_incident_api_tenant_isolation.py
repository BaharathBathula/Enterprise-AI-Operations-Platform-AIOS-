import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
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
        full_name="Incident Test User",
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
        slug=f"incident-{uuid.uuid4()}",
    )

    db.add(organization)
    db.flush()

    return organization


def _add_member(
    db: Session,
    organization: Organization,
    user: User,
    role: OrganizationRole = OrganizationRole.member,
) -> OrganizationMember:
    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role=role,
    )

    db.add(membership)
    db.flush()

    return membership


def _create_incident(
    db: Session,
    organization: Organization,
    user: User,
    title: str,
) -> Incident:
    incident = Incident(
        organization_id=organization.id,
        created_by_user_id=user.id,
        title=title,
        description="Integration test incident",
        severity=IncidentSeverity.high,
        status=IncidentStatus.open,
        source="integration-test",
    )

    db.add(incident)
    db.flush()

    return incident


def _auth_headers(
    user: User,
) -> dict[str, str]:
    token = create_access_token(
        subject=str(user.id),
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_member_can_read_incident_from_own_organization(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "incident-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Incident Owner Org",
    )

    _add_member(
        db_session,
        organization,
        user,
    )

    incident = _create_incident(
        db_session,
        organization,
        user,
        "Own Organization Incident",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/incidents/"
            f"{incident.id}"
        ),
        headers=_auth_headers(user),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(incident.id)

    assert (
        body["organization_id"]
        == str(organization.id)
    )


def test_user_cannot_read_incident_from_foreign_organization(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "incident-user-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "incident-user-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Incident Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Incident Tenant B",
    )

    _add_member(
        db_session,
        organization_a,
        user_a,
    )

    _add_member(
        db_session,
        organization_b,
        user_b,
    )

    incident_b = _create_incident(
        db_session,
        organization_b,
        user_b,
        "Tenant B Sensitive Incident",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_b.id}/incidents/"
            f"{incident_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Organization not found",
    }


def test_foreign_incident_id_cannot_escape_organization_scope(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "incident-scope-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "incident-scope-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Incident Scope A",
    )

    organization_b = _create_organization(
        db_session,
        "Incident Scope B",
    )

    _add_member(
        db_session,
        organization_a,
        user_a,
    )

    _add_member(
        db_session,
        organization_b,
        user_b,
    )

    incident_b = _create_incident(
        db_session,
        organization_b,
        user_b,
        "Foreign Incident",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/incidents/"
            f"{incident_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Incident not found",
    }


def test_incident_list_does_not_leak_foreign_tenant_incidents(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "incident-list-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "incident-list-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Incident List A",
    )

    organization_b = _create_organization(
        db_session,
        "Incident List B",
    )

    _add_member(
        db_session,
        organization_a,
        user_a,
    )

    _add_member(
        db_session,
        organization_b,
        user_b,
    )

    incident_a = _create_incident(
        db_session,
        organization_a,
        user_a,
        "Visible Incident A",
    )

    incident_b = _create_incident(
        db_session,
        organization_b,
        user_b,
        "Hidden Incident B",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/incidents"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item in response.json()
    }

    assert str(incident_a.id) in ids

    assert str(incident_b.id) not in ids


def test_foreign_incident_cannot_be_updated_through_own_organization(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "incident-update-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "incident-update-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Incident Update A",
    )

    organization_b = _create_organization(
        db_session,
        "Incident Update B",
    )

    _add_member(
        db_session,
        organization_a,
        user_a,
        OrganizationRole.admin,
    )

    _add_member(
        db_session,
        organization_b,
        user_b,
    )

    incident_b = _create_incident(
        db_session,
        organization_b,
        user_b,
        "Do Not Modify",
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/incidents/"
            f"{incident_b.id}"
        ),
        headers=_auth_headers(user_a),
        json={
            "title": "Compromised Title",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Incident not found",
    }

    db_session.expire_all()

    refreshed = db_session.get(
        Incident,
        incident_b.id,
    )

    assert refreshed is not None

    assert (
        refreshed.title
        == "Do Not Modify"
    )


def test_foreign_incident_cannot_be_deleted_through_own_organization(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "incident-delete-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "incident-delete-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Incident Delete A",
    )

    organization_b = _create_organization(
        db_session,
        "Incident Delete B",
    )

    _add_member(
        db_session,
        organization_a,
        user_a,
        OrganizationRole.admin,
    )

    _add_member(
        db_session,
        organization_b,
        user_b,
    )

    incident_b = _create_incident(
        db_session,
        organization_b,
        user_b,
        "Protected From Delete",
    )

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/incidents/"
            f"{incident_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Incident not found",
    }

    db_session.expire_all()

    refreshed = db_session.get(
        Incident,
        incident_b.id,
    )

    assert refreshed is not None


def test_unauthenticated_user_cannot_list_incidents(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "incident-protected@example.com",
    )

    organization = _create_organization(
        db_session,
        "Incident Protected Org",
    )

    _add_member(
        db_session,
        organization,
        user,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/incidents"
        )
    )

    assert response.status_code == 401
