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
        full_name="Incident RBAC User",
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
        slug=f"incident-rbac-{uuid.uuid4()}",
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
        description="Incident RBAC test",
        severity=IncidentSeverity.medium,
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


def test_member_can_create_incident(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "incident-create-member@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Incident Create Org",
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
            f"{organization.id}/incidents"
        ),
        headers=_auth_headers(member),
        json={
            "title": "Member-created incident",
            "description": "Created by normal member",
            "severity": "medium",
            "source": "manual",
        },
    )

    assert response.status_code == 201

    assert (
        response.json()["title"]
        == "Member-created incident"
    )


def test_member_cannot_update_incident(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "incident-update-member@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Update Denied Org",
    )

    _add_membership(
        db_session,
        organization,
        member,
        OrganizationRole.member,
    )

    incident = _create_incident(
        db_session,
        organization,
        member,
        "Original Incident",
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/incidents/"
            f"{incident.id}"
        ),
        headers=_auth_headers(member),
        json={
            "title": "Unauthorized Change",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Organization administrator access required",
    }

    db_session.expire_all()

    refreshed = db_session.get(
        Incident,
        incident.id,
    )

    assert refreshed is not None

    assert (
        refreshed.title
        == "Original Incident"
    )


def test_admin_can_update_incident(
    client: TestClient,
    db_session: Session,
):
    creator = _create_user(
        db_session,
        "incident-update-creator@example.com",
    )

    admin = _create_user(
        db_session,
        "incident-update-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Admin Update Org",
    )

    _add_membership(
        db_session,
        organization,
        creator,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    incident = _create_incident(
        db_session,
        organization,
        creator,
        "Needs Update",
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/incidents/"
            f"{incident.id}"
        ),
        headers=_auth_headers(admin),
        json={
            "title": "Updated By Admin",
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["title"]
        == "Updated By Admin"
    )


def test_owner_can_update_incident(
    client: TestClient,
    db_session: Session,
):
    creator = _create_user(
        db_session,
        "incident-owner-update-creator@example.com",
    )

    owner = _create_user(
        db_session,
        "incident-owner-update@example.com",
    )

    organization = _create_organization(
        db_session,
        "Owner Update Org",
    )

    _add_membership(
        db_session,
        organization,
        creator,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    incident = _create_incident(
        db_session,
        organization,
        creator,
        "Owner Update Target",
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/incidents/"
            f"{incident.id}"
        ),
        headers=_auth_headers(owner),
        json={
            "title": "Updated By Owner",
        },
    )

    assert response.status_code == 200


def test_member_cannot_delete_incident(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "incident-delete-member@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Delete Denied Org",
    )

    _add_membership(
        db_session,
        organization,
        member,
        OrganizationRole.member,
    )

    incident = _create_incident(
        db_session,
        organization,
        member,
        "Protected Incident",
    )

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/incidents/"
            f"{incident.id}"
        ),
        headers=_auth_headers(member),
    )

    assert response.status_code == 403

    db_session.expire_all()

    assert (
        db_session.get(
            Incident,
            incident.id,
        )
        is not None
    )


def test_admin_can_delete_incident(
    client: TestClient,
    db_session: Session,
):
    creator = _create_user(
        db_session,
        "incident-delete-creator@example.com",
    )

    admin = _create_user(
        db_session,
        "incident-delete-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Admin Delete Incident Org",
    )

    _add_membership(
        db_session,
        organization,
        creator,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    incident = _create_incident(
        db_session,
        organization,
        creator,
        "Delete By Admin",
    )

    incident_id = incident.id

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/incidents/"
            f"{incident_id}"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 204

    db_session.expire_all()

    assert (
        db_session.get(
            Incident,
            incident_id,
        )
        is None
    )


def test_owner_can_delete_incident(
    client: TestClient,
    db_session: Session,
):
    creator = _create_user(
        db_session,
        "incident-owner-delete-creator@example.com",
    )

    owner = _create_user(
        db_session,
        "incident-owner-delete@example.com",
    )

    organization = _create_organization(
        db_session,
        "Owner Delete Incident Org",
    )

    _add_membership(
        db_session,
        organization,
        creator,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    incident = _create_incident(
        db_session,
        organization,
        creator,
        "Delete By Owner",
    )

    incident_id = incident.id

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/incidents/"
            f"{incident_id}"
        ),
        headers=_auth_headers(owner),
    )

    assert response.status_code == 204
