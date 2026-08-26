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
        full_name="Viewer Security User",
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
        slug=f"viewer-security-{uuid.uuid4()}",
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


def test_viewer_can_read_organization(
    client: TestClient,
    db_session: Session,
):
    viewer = _create_user(
        db_session,
        "viewer-read@example.com",
    )

    organization = _create_organization(
        db_session,
        "Viewer Read Org",
    )

    _add_membership(
        db_session,
        organization,
        viewer,
        OrganizationRole.viewer,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}"
        ),
        headers=_auth_headers(viewer),
    )

    assert response.status_code == 200

    assert (
        response.json()["id"]
        == str(organization.id)
    )


def test_viewer_can_list_documents(
    client: TestClient,
    db_session: Session,
):
    viewer = _create_user(
        db_session,
        "viewer-documents@example.com",
    )

    organization = _create_organization(
        db_session,
        "Viewer Documents Org",
    )

    _add_membership(
        db_session,
        organization,
        viewer,
        OrganizationRole.viewer,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/documents"
        ),
        headers=_auth_headers(viewer),
    )

    assert response.status_code == 200


def test_viewer_cannot_upload_document(
    client: TestClient,
    db_session: Session,
):
    viewer = _create_user(
        db_session,
        "viewer-upload@example.com",
    )

    organization = _create_organization(
        db_session,
        "Viewer Upload Org",
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
            f"{organization.id}/documents"
        ),
        headers=_auth_headers(viewer),
        files={
            "file": (
                "viewer.pdf",
                b"%PDF-1.4 viewer test",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 403


def test_viewer_cannot_create_incident(
    client: TestClient,
    db_session: Session,
):
    viewer = _create_user(
        db_session,
        "viewer-incident@example.com",
    )

    organization = _create_organization(
        db_session,
        "Viewer Incident Org",
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
            f"{organization.id}/incidents"
        ),
        headers=_auth_headers(viewer),
        json={
            "title": "Viewer Incident",
            "description": (
                "Viewer must not create this"
            ),
            "severity": "medium",
            "source": "manual",
        },
    )

    assert response.status_code == 403


def test_viewer_cannot_create_conversation(
    client: TestClient,
    db_session: Session,
):
    viewer = _create_user(
        db_session,
        "viewer-conversation@example.com",
    )

    organization = _create_organization(
        db_session,
        "Viewer Conversation Org",
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
            f"{organization.id}/conversations"
        ),
        headers=_auth_headers(viewer),
        json={
            "title": "Viewer Conversation",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Organization write access required",
    }


def test_member_can_create_conversation(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "member-conversation@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Conversation Org",
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
            f"{organization.id}/conversations"
        ),
        headers=_auth_headers(member),
        json={
            "title": "Allowed Conversation",
        },
    )

    assert response.status_code == 201


def test_viewer_cannot_manage_members(
    client: TestClient,
    db_session: Session,
):
    viewer = _create_user(
        db_session,
        "viewer-members@example.com",
    )

    target = _create_user(
        db_session,
        "viewer-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Viewer Members Org",
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
            f"{organization.id}/members"
        ),
        headers=_auth_headers(viewer),
        json={
            "email": target.email,
            "role": "member",
        },
    )

    assert response.status_code == 403
