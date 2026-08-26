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
from app.services.conversation_service import (
    create_conversation,
)


def _create_user(
    db: Session,
    email: str,
) -> User:
    user = User(
        email=email,
        full_name="Chat Security User",
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
        slug=f"chat-security-{uuid.uuid4()}",
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


def test_viewer_cannot_use_chat(
    client: TestClient,
    db_session: Session,
):
    viewer = _create_user(
        db_session,
        "chat-viewer@example.com",
    )

    organization = _create_organization(
        db_session,
        "Chat Viewer Org",
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
            f"{organization.id}/chat"
        ),
        headers=_auth_headers(viewer),
        json={
            "question": "Summarize the documents",
            "top_k": 5,
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Organization write access required",
    }


def test_foreign_tenant_user_cannot_use_chat(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "chat-tenant-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "chat-tenant-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Chat Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Chat Tenant B",
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
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_b.id}/chat"
        ),
        headers=_auth_headers(user_a),
        json={
            "question": "Read tenant B documents",
            "top_k": 5,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Organization not found",
    }


def test_user_cannot_write_to_another_users_conversation(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "chat-owner-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "chat-owner-b@example.com",
    )

    organization = _create_organization(
        db_session,
        "Chat Ownership Org",
    )

    _add_membership(
        db_session,
        organization,
        user_a,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        user_b,
        OrganizationRole.member,
    )

    conversation = create_conversation(
        db=db_session,
        organization_id=organization.id,
        current_user=user_a,
        title="Private Conversation",
    )

    conversation_id = conversation.id

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/chat"
        ),
        headers=_auth_headers(user_b),
        json={
            "question":
                "Write into another user's conversation",
            "conversation_id":
                str(conversation_id),
            "top_k": 5,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Conversation not found",
    }


def test_cross_tenant_conversation_id_is_hidden(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "chat-cross-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "chat-cross-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Chat Cross Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Chat Cross Tenant B",
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
        OrganizationRole.member,
    )

    conversation_b = create_conversation(
        db=db_session,
        organization_id=organization_b.id,
        current_user=user_b,
        title="Tenant B Conversation",
    )

    conversation_id = conversation_b.id

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/chat"
        ),
        headers=_auth_headers(user_a),
        json={
            "question":
                "Attempt cross-tenant conversation access",
            "conversation_id":
                str(conversation_id),
            "top_k": 5,
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Conversation not found",
    }


def test_unauthenticated_user_cannot_use_chat(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "chat-unauth-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Chat Protected Org",
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
            f"{organization.id}/chat"
        ),
        json={
            "question": "Unauthorized request",
            "top_k": 5,
        },
    )

    assert response.status_code == 401
