import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
)
from app.models.audit_log import AuditLog
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
        full_name="Ownership Transfer User",
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
            f"ownership-transfer-"
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


def test_owner_can_transfer_ownership_to_existing_member(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "transfer-owner@example.com",
    )

    target = _create_user(
        db_session,
        "transfer-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Ownership Transfer Org",
    )

    owner_membership = (
        _add_membership(
            db_session,
            organization,
            owner,
            OrganizationRole.owner,
        )
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

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}/"
            "transfer-ownership"
        ),
        headers=_auth_headers(owner),
    )

    assert response.status_code == 200

    assert (
        response.json()["role"]
        == "owner"
    )

    db_session.expire_all()

    refreshed_previous_owner = (
        db_session.get(
            OrganizationMember,
            owner_membership.id,
        )
    )

    refreshed_new_owner = (
        db_session.get(
            OrganizationMember,
            target_membership.id,
        )
    )

    assert (
        refreshed_previous_owner
        is not None
    )

    assert (
        refreshed_new_owner
        is not None
    )

    assert (
        refreshed_previous_owner.role
        == OrganizationRole.admin
    )

    assert (
        refreshed_new_owner.role
        == OrganizationRole.owner
    )


def test_admin_cannot_transfer_ownership(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "transfer-protected-owner@example.com",
    )

    admin = _create_user(
        db_session,
        "transfer-admin@example.com",
    )

    target = _create_user(
        db_session,
        "transfer-admin-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Admin Transfer Denied Org",
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
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

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}/"
            "transfer-ownership"
        ),
        headers=_auth_headers(admin),
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail":
            "Organization owner access required",
    }


def test_member_cannot_transfer_ownership(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "transfer-member-owner@example.com",
    )

    member = _create_user(
        db_session,
        "transfer-member@example.com",
    )

    target = _create_user(
        db_session,
        "transfer-member-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Member Transfer Denied Org",
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    _add_membership(
        db_session,
        organization,
        member,
        OrganizationRole.member,
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

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}/"
            "transfer-ownership"
        ),
        headers=_auth_headers(member),
    )

    assert response.status_code == 403


def test_owner_cannot_transfer_to_foreign_tenant_member(
    client: TestClient,
    db_session: Session,
):
    owner_a = _create_user(
        db_session,
        "transfer-foreign-owner@example.com",
    )

    user_b = _create_user(
        db_session,
        "transfer-foreign-target@example.com",
    )

    organization_a = _create_organization(
        db_session,
        "Transfer Tenant A",
    )

    organization_b = _create_organization(
        db_session,
        "Transfer Tenant B",
    )

    _add_membership(
        db_session,
        organization_a,
        owner_a,
        OrganizationRole.owner,
    )

    foreign_membership = (
        _add_membership(
            db_session,
            organization_b,
            user_b,
            OrganizationRole.member,
        )
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization_a.id}/members/"
            f"{foreign_membership.id}/"
            "transfer-ownership"
        ),
        headers=_auth_headers(owner_a),
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail":
            "Target organization member "
            "not found",
    }

    db_session.expire_all()

    refreshed = db_session.get(
        OrganizationMember,
        foreign_membership.id,
    )

    assert refreshed is not None

    assert (
        refreshed.role
        == OrganizationRole.member
    )


def test_owner_cannot_transfer_ownership_to_self(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "transfer-self@example.com",
    )

    organization = _create_organization(
        db_session,
        "Self Transfer Org",
    )

    owner_membership = (
        _add_membership(
            db_session,
            organization,
            owner,
            OrganizationRole.owner,
        )
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{owner_membership.id}/"
            "transfer-ownership"
        ),
        headers=_auth_headers(owner),
    )

    assert response.status_code == 409

    assert response.json() == {
        "detail":
            "Ownership cannot be transferred "
            "to the current owner",
    }


def test_transfer_creates_audit_log(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "transfer-audit-owner@example.com",
    )

    target = _create_user(
        db_session,
        "transfer-audit-target@example.com",
    )

    organization = _create_organization(
        db_session,
        "Ownership Audit Org",
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    target_membership = (
        _add_membership(
            db_session,
            organization,
            target,
            OrganizationRole.admin,
        )
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}/"
            "transfer-ownership"
        ),
        headers=_auth_headers(owner),
    )

    assert response.status_code == 200

    audit_log = (
        db_session.query(
            AuditLog
        )
        .filter(
            AuditLog.organization_id
            == organization.id,
            AuditLog.action
            == (
                "organization."
                "ownership_transferred"
            ),
        )
        .one_or_none()
    )

    assert audit_log is not None

    assert (
        audit_log.user_id
        == owner.id
    )

    assert (
        audit_log.details[
            "new_owner_user_id"
        ]
        == str(target.id)
    )


def test_transfer_leaves_exactly_one_owner(
    client: TestClient,
    db_session: Session,
):
    owner = _create_user(
        db_session,
        "transfer-single-owner@example.com",
    )

    target = _create_user(
        db_session,
        "transfer-single-target@example.com",
    )

    other_member = _create_user(
        db_session,
        "transfer-single-other@example.com",
    )

    organization = _create_organization(
        db_session,
        "Single Owner Org",
    )

    _add_membership(
        db_session,
        organization,
        owner,
        OrganizationRole.owner,
    )

    target_membership = (
        _add_membership(
            db_session,
            organization,
            target,
            OrganizationRole.admin,
        )
    )

    _add_membership(
        db_session,
        organization,
        other_member,
        OrganizationRole.member,
    )

    db_session.commit()

    response = client.post(
        (
            f"/api/v1/organizations/"
            f"{organization.id}/members/"
            f"{target_membership.id}/"
            "transfer-ownership"
        ),
        headers=_auth_headers(owner),
    )

    assert response.status_code == 200

    owners = (
        db_session.query(
            OrganizationMember
        )
        .filter(
            OrganizationMember.organization_id
            == organization.id,
            OrganizationMember.role
            == OrganizationRole.owner,
        )
        .all()
    )

    assert len(owners) == 1

    assert (
        owners[0].user_id
        == target.id
    )
