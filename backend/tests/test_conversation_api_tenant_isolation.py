import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.conversation import Conversation
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
        full_name="Conversation Test User",
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
) -> Organization:
    organization = Organization(
        name=name,
        slug=f"{name.lower().replace(' ', '-')}-{uuid.uuid4()}",
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


def _create_conversation(
    db: Session,
    organization: Organization,
    user: User,
    title: str,
) -> Conversation:
    conversation = Conversation(
        organization_id=organization.id,
        user_id=user.id,
        title=title,
    )

    db.add(conversation)
    db.flush()

    return conversation


def _auth_headers(
    user: User,
) -> dict[str, str]:
    token = create_access_token(
        subject=str(user.id),
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def test_user_can_read_own_conversation(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "conversation-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Conversation Org",
    )

    _add_member(
        db_session,
        organization,
        user,
    )

    conversation = _create_conversation(
        db_session,
        organization,
        user,
        "Private AIOS Conversation",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/conversations/"
            f"{conversation.id}"
        ),
        headers=_auth_headers(user),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(conversation.id)

    assert (
        body["organization_id"]
        == str(organization.id)
    )

    assert (
        body["user_id"]
        == str(user.id)
    )


def test_user_cannot_read_conversation_from_foreign_organization(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "conversation-user-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "conversation-user-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Conversation Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Conversation Tenant B",
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

    conversation_b = _create_conversation(
        db_session,
        organization_b,
        user_b,
        "Tenant B Sensitive Thread",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_b.id}/conversations/"
            f"{conversation_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Organization not found",
    }


def test_user_cannot_read_another_users_conversation_in_same_organization(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "same-org-user-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "same-org-user-b@example.com",
    )

    organization = _create_organization(
        db_session,
        "Shared Enterprise Org",
    )

    _add_member(
        db_session,
        organization,
        user_a,
    )

    _add_member(
        db_session,
        organization,
        user_b,
    )

    conversation_b = _create_conversation(
        db_session,
        organization,
        user_b,
        "User B Private Conversation",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/conversations/"
            f"{conversation_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Conversation not found",
    }


def test_conversation_id_cannot_escape_organization_scope(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "conversation-scope-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "conversation-scope-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Conversation Scope A",
    )

    organization_b = _create_organization(
        db_session,
        "Conversation Scope B",
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

    conversation_b = _create_conversation(
        db_session,
        organization_b,
        user_b,
        "Foreign Conversation",
    )

    db_session.commit()

    # User A is authorized for Organization A,
    # but injects a conversation UUID owned by Org B.
    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/conversations/"
            f"{conversation_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Conversation not found",
    }


def test_conversation_list_returns_only_current_users_conversations(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "list-user-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "list-user-b@example.com",
    )

    organization = _create_organization(
        db_session,
        "Conversation List Org",
    )

    _add_member(
        db_session,
        organization,
        user_a,
    )

    _add_member(
        db_session,
        organization,
        user_b,
    )

    conversation_a = _create_conversation(
        db_session,
        organization,
        user_a,
        "User A Conversation",
    )

    conversation_b = _create_conversation(
        db_session,
        organization,
        user_b,
        "User B Conversation",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/conversations"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 200

    body = response.json()

    ids = {
        item["id"]
        for item in body
    }

    assert str(conversation_a.id) in ids

    assert str(conversation_b.id) not in ids


def test_unauthenticated_user_cannot_read_conversation(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "unauthenticated-conversation@example.com",
    )

    organization = _create_organization(
        db_session,
        "Protected Conversation Org",
    )

    _add_member(
        db_session,
        organization,
        user,
    )

    conversation = _create_conversation(
        db_session,
        organization,
        user,
        "Protected Conversation",
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/conversations/"
            f"{conversation.id}"
        )
    )

    assert response.status_code == 401
