import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.document import Document, DocumentStatus
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
        full_name="Integration Test User",
        hashed_password="not-used-in-this-test",
        is_active=True,
        is_superuser=False,
    )

    db.add(user)
    db.flush()

    return user


def _create_organization(
    db: Session,
    name: str,
    slug: str,
) -> Organization:
    organization = Organization(
        name=name,
        slug=slug,
    )

    db.add(organization)
    db.flush()

    return organization


def _add_member(
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


def _create_document(
    db: Session,
    organization: Organization,
    user: User,
    filename: str,
) -> Document:
    document = Document(
        organization_id=organization.id,
        uploaded_by_user_id=user.id,
        filename=filename,
        original_filename=filename,
        content_type="application/pdf",
        file_size=1024,
        storage_path=f"/tmp/{filename}",
        status=DocumentStatus.uploaded,
    )

    db.add(document)
    db.flush()

    return document


def _auth_headers(
    user: User,
) -> dict[str, str]:
    token = create_access_token(
        subject=str(user.id),
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_user_can_read_document_from_own_organization(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "user-a-own@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Organization A",
        f"organization-a-{uuid.uuid4()}",
    )

    _add_member(
        db_session,
        organization_a,
        user_a,
        OrganizationRole.member,
    )

    document_a = _create_document(
        db_session,
        organization_a,
        user_a,
        "organization-a-document.pdf",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/documents/"
            f"{document_a.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(document_a.id)

    assert (
        body["organization_id"]
        == str(organization_a.id)
    )


def test_user_cannot_read_document_from_foreign_organization(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "user-a-cross@example.com",
    )

    user_b = _create_user(
        db_session,
        "user-b-cross@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Tenant A",
        f"tenant-a-{uuid.uuid4()}",
    )

    organization_b = _create_organization(
        db_session,
        "Tenant B",
        f"tenant-b-{uuid.uuid4()}",
    )

    _add_member(
        db_session,
        organization_a,
        user_a,
        OrganizationRole.member,
    )

    _add_member(
        db_session,
        organization_b,
        user_b,
        OrganizationRole.member,
    )

    document_b = _create_document(
        db_session,
        organization_b,
        user_b,
        "tenant-b-secret.pdf",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_b.id}/documents/"
            f"{document_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Organization not found",
    }


def test_document_id_cannot_escape_organization_scope(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "user-a-scope@example.com",
    )

    user_b = _create_user(
        db_session,
        "user-b-scope@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Scope Organization A",
        f"scope-a-{uuid.uuid4()}",
    )

    organization_b = _create_organization(
        db_session,
        "Scope Organization B",
        f"scope-b-{uuid.uuid4()}",
    )

    _add_member(
        db_session,
        organization_a,
        user_a,
        OrganizationRole.member,
    )

    _add_member(
        db_session,
        organization_b,
        user_b,
        OrganizationRole.member,
    )

    document_b = _create_document(
        db_session,
        organization_b,
        user_b,
        "foreign-document.pdf",
    )

    db_session.commit()

    # User A is legitimately authorized for Organization A,
    # but deliberately supplies Document B's UUID.
    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/documents/"
            f"{document_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Document not found",
    }


def test_unauthenticated_user_cannot_read_document(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "document-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Protected Organization",
        f"protected-{uuid.uuid4()}",
    )

    _add_member(
        db_session,
        organization,
        user,
        OrganizationRole.member,
    )

    document = _create_document(
        db_session,
        organization,
        user,
        "protected.pdf",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/documents/"
            f"{document.id}"
        )
    )

    assert response.status_code == 401
