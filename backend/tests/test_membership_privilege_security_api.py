import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
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
        full_name="Membership Security User",
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
        slug=(
            f"membership-security-"
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


def test_admin_cannot_add_new_owner(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "membership-admin-owner@example.com",
    )

    target = _create_user(
        db_session,
        "membership-target-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Owner Escalation Org",
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
            f"{organization.id}/members"
        ),
        headers=_auth_headers(admin),
        json={
            "email": target.email,
            "role": "owner",
        },
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Ownership transfer requires "
            "a dedicated workflow",
    }

    membership = (
        db_session.query(
            OrganizationMember
        )
        .filter(
            OrganizationMember.organization_id
            == organization.id,
            OrganizationMember.user_id
            == target.id,
        )
        .one_or_none()
    )

    assert membership is None


def test_owner_cannot_add_second_owner_directly(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "membership-owner@example.com",
    )

    target = _create_user(
        db_session,
        "membership-second-owner@example.com",
    )

    organization = _create_organization(
        db_session,
        "Second Owner Protection Org",
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
            f"{organization.id}/members"
        ),
        headers=_auth_headers(owner),
        json={
            "email": target.email,
            "role": "owner",
        },
    )

    assert response.status_code == 403


def test_admin_can_add_regular_admin(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "membership-existing-admin@example.com",
    )

    target = _create_user(
        db_session,
        "membership-new-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Admin Addition Org",
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
            f"{organization.id}/members"
        ),
        headers=_auth_headers(admin),
        json={
            "email": target.email,
            "role": "admin",
        },
    )

    assert response.status_code == 201

    assert (
        response.json()["role"]
        == "admin"
    )


def test_admin_cannot_promote_member_to_owner(
    client: TestClient,
    db_session: Session,
):
    admin = _create_user(
        db_session,
        "membership-promote-admin@example.com",
    )

    target = _create_user(
        db_session,
        "membership-promote-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Promotion Protection Org",
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    target_membership = (
        _add_membership(
            db_session,
            organization,
            target,
            OrganizationRole.member,
        )
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}"
        ),
        headers=_auth_headers(admin),
        json={
            "role": "owner",
        },
    )

    assert response.status_code == 403

    db_session.expire_all()

    refreshed = db_session.get(
        OrganizationMember,
        target_membership.id,
    )

    assert refreshed is not None

    assert (
        refreshed.role
        == OrganizationRole.member
    )


def test_admin_cannot_modify_existing_owner(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "membership-protected-owner@example.com",
    )

    admin = _create_user(
        db_session,
        "membership-owner-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Owner Modification Protection Org",
    )

    owner_membership = (
        _add_membership(
            db_session,
            organization,
            owner,
            OrganizationRole.owner,
        )
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{owner_membership.id}"
        ),
        headers=_auth_headers(admin),
        json={
            "role": "member",
        },
    )

    assert response.status_code == 403


def test_admin_cannot_remove_existing_owner(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "membership-delete-owner@example.com",
    )

    admin = _create_user(
        db_session,
        "membership-delete-admin@example.com",
    )

    organization = _create_organization(
        db_session,
        "Owner Delete Protection Org",
    )

    owner_membership = (
        _add_membership(
            db_session,
            organization,
            owner,
            OrganizationRole.owner,
        )
    )

    _add_membership(
        db_session,
        organization,
        admin,
        OrganizationRole.admin,
    )

    db_session.commit()

    response = client.delete(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{owner_membership.id}"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 403

    db_session.expire_all()

    assert (
        db_session.get(
            OrganizationMember,
            owner_membership.id,
        )
        is not None
    )


def test_admin_cannot_modify_foreign_tenant_membership(
    client: TestClient,
    db_session: Session,
):
    admin_a = _create_user(
        db_session,
        "membership-foreign-admin@example.com",
    )

    user_b = _create_user(
        db_session,
        "membership-foreign-user@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Membership Foreign A",
    )

    organization_b = _create_organization(
        db_session,
        "Membership Foreign B",
    )

    _add_membership(
        db_session,
        organization_a,
        admin_a,
        OrganizationRole.admin,
    )

    membership_b = (
        _add_membership(
            db_session,
            organization_b,
            user_b,
            OrganizationRole.member,
        )
    )

    db_session.commit()

    response = client.patch(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/members/"
            f"{membership_b.id}"
        ),
        headers=_auth_headers(admin_a),
        json={
            "role": "admin",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail":
            "Organization member not found",
    }

    db_session.expire_all()

    refreshed = db_session.get(
        OrganizationMember,
        membership_b.id,
    )

    assert refreshed is not None

    assert (
        refreshed.role
        == OrganizationRole.member
    )
