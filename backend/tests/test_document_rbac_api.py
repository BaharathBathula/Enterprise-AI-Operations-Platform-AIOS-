import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
)
from app.models.document import (
    Document,
    DocumentStatus,
)
from app.models.organization import (
    Organization,
)
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
        full_name="Document RBAC User",
        hashed_password=(
            "not-used-in-test"
        ),
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
        slug=(
            f"document-rbac-"
            f"{uuid.uuid4()}"
        ),
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
        organization_id=(
            organization.id
        ),
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
        organization_id=(
            organization.id
        ),
        uploaded_by_user_id=user.id,
        filename=filename,
        original_filename=filename,
        content_type="application/pdf",
        file_size=1024,
        storage_path=(
            f"/tmp/{filename}"
        ),
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
        "Authorization":
            f"Bearer {token}",
    }


def test_member_can_list_documents(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "document-list-member@example.com",
    )

    organization = _create_organization(
        db_session,
        "Document List Org",
    )

    _add_membership(
        db_session,
        organization,
        member,
        OrganizationRole.member,
    )

    document = _create_document(
        db_session,
        organization,
        member,
        "member-visible.pdf",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/documents"
        ),
        headers=_auth_headers(member),
    )

    assert response.status_code == 200

    ids = {
        item["id"]
        for item
        in response.json()
    }

    assert str(document.id) in ids


def test_member_cannot_delete_document(
    client: TestClient,
    db_session: Session,
):
    member = _create_user(
        db_session,
        "document-delete-member@example.com",
    )

    organization = _create_organization(
        db_session,
        "Document Delete Member Org",
    )

    _add_membership(
        db_session,
        organization,
        member,
        OrganizationRole.member,
    )

    document = _create_document(
        db_session,
        organization,
        member,
        "member-protected.pdf",
    )

    document_id = document.id

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/documents/"
            f"{document_id}"
        ),
        headers=_auth_headers(member),
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Organization administrator "
            "access required",
    }

    db_session.expire_all()

    assert (
        db_session.get(
            Document,
            document_id,
        )
        is not None
    )


def test_admin_can_delete_document(
    client: TestClient,
    db_session: Session,
):
    uploader = _create_user(
        db_session,
        "document-admin-uploader@example.com",
    )

    admin = _create_user(
        db_session,
        "document-delete-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Document Admin Delete Org",
    )

    _add_membership(
        db_session,
        organization,
        uploader,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    document = _create_document(
        db_session,
        organization,
        uploader,
        "admin-delete.pdf",
    )

    document_id = document.id

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/documents/"
            f"{document_id}"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 204

    db_session.expire_all()

    assert (
        db_session.get(
            Document,
            document_id,
        )
        is None
    )


def test_owner_can_delete_document(
    client: TestClient,
    db_session: Session,
):
    uploader = _create_user(
        db_session,
        "document-owner-uploader@example.com",
    )

    owner = _create_user(
        db_session,
        "document-delete-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Document Owner Delete Org",
    )

    _add_membership(
        db_session,
        organization,
        uploader,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    document = _create_document(
        db_session,
        organization,
        uploader,
        "owner-delete.pdf",
    )

    document_id = document.id

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/documents/"
            f"{document_id}"
        ),
        headers=_auth_headers(owner),
    )

    assert response.status_code == 204

    db_session.expire_all()

    assert (
        db_session.get(
            Document,
            document_id,
        )
        is None
    )


def test_admin_cannot_delete_foreign_tenant_document(
    client: TestClient,
    db_session: Session,
):
    admin_a = _create_user(
        db_session,
        "document-foreign-admin-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "document-foreign-user-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Document Foreign A",
    )

    organization_b = _create_organization(
        db_session,
        "Document Foreign B",
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

    document_b = _create_document(
        db_session,
        organization_b,
        user_b,
        "foreign-secret.pdf",
    )

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/documents/"
            f"{document_b.id}"
        ),
        headers=_auth_headers(admin_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail":
            "Document not found",
    }

    db_session.expire_all()

    assert (
        db_session.get(
            Document,
            document_b.id,
        )
        is not None
    )


def test_unauthenticated_user_cannot_delete_document(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "document-unauth-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Document Protected Org",
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    document = _create_document(
        db_session,
        organization,
        owner,
        "protected-document.pdf",
    )

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/documents/"
            f"{document.id}"
        )
    )

    assert response.status_code == 401
