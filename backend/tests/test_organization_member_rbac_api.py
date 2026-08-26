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
        full_name="RBAC Test User",
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
        slug=f"rbac-{uuid.uuid4()}",
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


def test_member_can_list_organization_members(
    client: TestClient,
    db_session: Session,
):
    member_user = _create_user(
        db_session,
        "member-list@example.com",
    )

    other_user = _create_user(
        db_session,
        "other-list@example.com",
    )

    organization = _create_organization(
        db_session,
        "List Members Org",
    )

    _add_membership(
        db_session,
        organization,
        member_user,
        OrganizationRole.member,
    )

    _add_membership(
        db_session,
        organization,
        other_user,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members"
        ),
        headers=_auth_headers(
            member_user,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    emails = {
        item["email"]
        for item in body
    }

    assert (
        "member-list@example.com"
        in emails
    )

    assert (
        "other-list@example.com"
        in emails
    )


def test_member_cannot_add_organization_member(
    client: TestClient,
    db_session: Session,
):
    member_user = _create_user(
        db_session,
        "member-add@example.com",
    )

    target_user = _create_user(
        db_session,
        "target-add@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Cannot Add Org",
    )

    _add_membership(
        db_session,
        organization,
        member_user,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members"
        ),
        headers=_auth_headers(
            member_user,
        ),
        json={
            "email": target_user.email,
            "role": "member",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Organization administrator access required",
    }


def test_admin_can_add_organization_member(
    client: TestClient,
    db_session: Session,
):
    admin_user = _create_user(
        db_session,
        "admin-add@example.com",
    )

    target_user = _create_user(
        db_session,
        "admin-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Admin Add Org",
    )

    _add_membership(
        db_session,
        organization,
        admin_user,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members"
        ),
        headers=_auth_headers(
            admin_user,
        ),
        json={
            "email": target_user.email,
            "role": "member",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert (
        body["email"]
        == target_user.email
    )

    assert body["role"] == "member"


def test_owner_can_add_organization_member(
    client: TestClient,
    db_session: Session,
):
    owner_user = _create_user(
        db_session,
        "owner-add@example.com",
    )

    target_user = _create_user(
        db_session,
        "owner-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Owner Add Org",
    )

    _add_membership(
        db_session,
        organization,
        owner_user,
        OrganizationRole.owner,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members"
        ),
        headers=_auth_headers(
            owner_user,
        ),
        json={
            "email": target_user.email,
            "role": "member",
        },
    )

    assert response.status_code == 201

    assert (
        response.json()["email"]
        == target_user.email
    )


def test_member_cannot_change_member_role(
    client: TestClient,
    db_session: Session,
):
    member_user = _create_user(
        db_session,
        "member-patch@example.com",
    )

    target_user = _create_user(
        db_session,
        "patch-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Patch Org",
    )

    _add_membership(
        db_session,
        organization,
        member_user,
        OrganizationRole.member,
    )

    target_membership = _add_membership(
        db_session,
        organization,
        target_user,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}"
        ),
        headers=_auth_headers(
            member_user,
        ),
        json={
            "role": "admin",
        },
    )

    assert response.status_code == 403


def test_admin_can_promote_member(
    client: TestClient,
    db_session: Session,
):
    admin_user = _create_user(
        db_session,
        "admin-promote@example.com",
    )

    target_user = _create_user(
        db_session,
        "promote-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Admin Promote Org",
    )

    _add_membership(
        db_session,
        organization,
        admin_user,
        OrganizationRole.admin,
    )

    target_membership = _add_membership(
        db_session,
        organization,
        target_user,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}"
        ),
        headers=_auth_headers(
            admin_user,
        ),
        json={
            "role": "admin",
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["role"]
        == "admin"
    )


def test_member_cannot_delete_member(
    client: TestClient,
    db_session: Session,
):
    member_user = _create_user(
        db_session,
        "member-delete@example.com",
    )

    target_user = _create_user(
        db_session,
        "delete-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Delete Org",
    )

    _add_membership(
        db_session,
        organization,
        member_user,
        OrganizationRole.member,
    )

    target_membership = _add_membership(
        db_session,
        organization,
        target_user,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}"
        ),
        headers=_auth_headers(
            member_user,
        ),
    )

    assert response.status_code == 403


def test_admin_can_delete_regular_member(
    client: TestClient,
    db_session: Session,
):
    admin_user = _create_user(
        db_session,
        "admin-delete@example.com",
    )

    target_user = _create_user(
        db_session,
        "admin-delete-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Admin Delete Org",
    )

    _add_membership(
        db_session,
        organization,
        admin_user,
        OrganizationRole.admin,
    )

    target_membership = _add_membership(
        db_session,
        organization,
        target_user,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}"
        ),
        headers=_auth_headers(
            admin_user,
        ),
    )

    assert response.status_code == 204


def test_admin_cannot_modify_owner_role(
    client: TestClient,
    db_session: Session,
):
    owner_user = _create_user(
        db_session,
        "protected-owner@example.com",
    )

    admin_user = _create_user(
        db_session,
        "owner-protection-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Owner Protection Org",
    )

    owner_membership = _add_membership(
        db_session,
        organization,
        owner_user,
        OrganizationRole.owner,
    )

    _add_membership(
        db_session,
        organization,
        admin_user,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{owner_membership.id}"
        ),
        headers=_auth_headers(
            admin_user,
        ),
        json={
            "role": "member",
        },
    )

    assert response.status_code == 403


def test_admin_cannot_delete_owner(
    client: TestClient,
    db_session: Session,
):
    owner_user = _create_user(
        db_session,
        "delete-protected-owner@example.com",
    )

    admin_user = _create_user(
        db_session,
        "delete-owner-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Owner Delete Protection Org",
    )

    owner_membership = _add_membership(
        db_session,
        organization,
        owner_user,
        OrganizationRole.owner,
    )

    _add_membership(
        db_session,
        organization,
        admin_user,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{owner_membership.id}"
        ),
        headers=_auth_headers(
            admin_user,
        ),
    )

    assert response.status_code == 403
