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
        full_name="Organization Security User",
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
        slug=f"organization-security-{uuid.uuid4()}",
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


def test_user_can_read_own_organization(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "organization-own@example.com",
    )

    organization = _create_organization(
        db_session,
        "Own Organization",
    )

    _add_membership(
        db_session,
        organization,
        user,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}"
        ),
        headers=_auth_headers(user),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == str(
        organization.id
    )

    assert body["name"] == (
        "Own Organization"
    )


def test_user_cannot_read_foreign_organization(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "organization-user-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "organization-user-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Organization A",
    )

    organization_b = _create_organization(
        db_session,
        "Organization B",
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

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization_b.id}"
        ),
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Organization not found",
    }


def test_organization_list_contains_only_users_memberships(
    client: TestClient,
    db_session: Session,
):
    user_a = _create_user(
        db_session,
        "organization-list-a@example.com",
    )

    user_b = _create_user(
        db_session,
        "organization-list-b@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Visible Organization",
    )

    organization_b = _create_organization(
        db_session,
        "Hidden Organization",
    )

    _add_membership(
        db_session,
        organization_a,
        user_a,
        OrganizationRole.admin,
    )

    _add_membership(
        db_session,
        organization_b,
        user_b,
        OrganizationRole.owner,
    )

    db_session.commit()

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(user_a),
    )

    assert response.status_code == 200

    body = response.json()

    organization_ids = {
        item["organization"]["id"]
        for item in body
    }

    assert str(
        organization_a.id
    ) in organization_ids

    assert str(
        organization_b.id
    ) not in organization_ids


def test_organization_list_returns_membership_role(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "organization-role@example.com",
    )

    organization = _create_organization(
        db_session,
        "Role Organization",
    )

    _add_membership(
        db_session,
        organization,
        user,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(user),
    )

    assert response.status_code == 200

    matching = [
        item
        for item in response.json()
        if (
            item["organization"]["id"]
            == str(organization.id)
        )
    ]

    assert len(matching) == 1

    assert (
        matching[0]["role"]
        == "admin"
    )


def test_user_can_belong_to_multiple_organizations(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "organization-multi@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Multi Organization A",
    )

    organization_b = _create_organization(
        db_session,
        "Multi Organization B",
    )

    _add_membership(
        db_session,
        organization_a,
        user,
        OrganizationRole.owner,
    )

    _add_membership(
        db_session,
        organization_b,
        user,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.get(
        "/api/v1/organizations",
        headers=_auth_headers(user),
    )

    assert response.status_code == 200

    organization_ids = {
        item["organization"]["id"]
        for item in response.json()
    }

    assert str(
        organization_a.id
    ) in organization_ids

    assert str(
        organization_b.id
    ) in organization_ids


def test_unauthenticated_user_cannot_list_organizations(
    client: TestClient,
):
    response = client.get(
        "/api/v1/organizations"
    )

    assert response.status_code == 401


def test_unauthenticated_user_cannot_read_organization(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "organization-unauth@example.com",
    )

    organization = _create_organization(
        db_session,
        "Protected Organization",
    )

    _add_membership(
        db_session,
        organization,
        user,
        OrganizationRole.owner,
    )

    db_session.commit()

    response = client.get(
        (
            f"/api/v1/organizations/"
            f"{organization.id}"
        )
    )

    assert response.status_code == 401


def test_authenticated_user_can_create_organization(
    client: TestClient,
    db_session: Session,
):
    user = _create_user(
        db_session,
        "organization-create@example.com",
    )

    db_session.commit()

    unique_suffix = uuid.uuid4().hex

    response = client.post(
        "/api/v1/organizations",
        headers=_auth_headers(user),
        json={
            "name": (
                "Created Security Organization"
            ),
            "slug": (
                f"created-security-"
                f"{unique_suffix}"
            ),
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == (
        "Created Security Organization"
    )

    organization_id = uuid.UUID(
        body["id"]
    )

    membership = (
        db_session.query(
            OrganizationMember
        )
        .filter(
            OrganizationMember.organization_id
            == organization_id,
            OrganizationMember.user_id
            == user.id,
        )
        .one_or_none()
    )

    assert membership is not None

    assert (
        membership.role
        == OrganizationRole.owner
    )


def test_unauthenticated_user_cannot_create_organization(
    client: TestClient,
):
    response = client.post(
        "/api/v1/organizations",
        json={
            "name":
                "Unauthorized Organization",
            "slug":
                f"unauthorized-{uuid.uuid4()}",
        },
    )

    assert response.status_code == 401
