import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User


class MemberAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class MemberNotFoundError(Exception):
    pass


class OwnerModificationError(Exception):
    pass


def list_organization_members(
    db: Session,
    organization_id: uuid.UUID,
) -> list[OrganizationMember]:
    statement = (
        select(OrganizationMember)
        .options(
            joinedload(OrganizationMember.user),
        )
        .where(
            OrganizationMember.organization_id
            == organization_id,
        )
        .order_by(
            OrganizationMember.created_at.asc(),
        )
    )

    return list(db.scalars(statement).all())


def add_organization_member(
    db: Session,
    organization_id: uuid.UUID,
    email: str,
    role: OrganizationRole,
) -> OrganizationMember:
    normalized_email = email.strip().lower()

    user_statement = select(User).where(
        User.email == normalized_email,
    )

    user = db.scalar(user_statement)

    if user is None:
        raise UserNotFoundError(
            "No registered user exists with this email"
        )

    membership_statement = select(
        OrganizationMember
    ).where(
        OrganizationMember.organization_id
        == organization_id,
        OrganizationMember.user_id == user.id,
    )

    existing_membership = db.scalar(
        membership_statement
    )

    if existing_membership is not None:
        raise MemberAlreadyExistsError(
            "User is already a member of this organization"
        )

    membership = OrganizationMember(
        organization_id=organization_id,
        user_id=user.id,
        role=role,
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return membership


def get_organization_member(
    db: Session,
    organization_id: uuid.UUID,
    member_id: uuid.UUID,
) -> OrganizationMember | None:
    statement = (
        select(OrganizationMember)
        .options(
            joinedload(OrganizationMember.user),
        )
        .where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id
            == organization_id,
        )
    )

    return db.scalar(statement)


def update_member_role(
    db: Session,
    membership: OrganizationMember,
    new_role: OrganizationRole,
) -> OrganizationMember:
    if membership.role == OrganizationRole.owner:
        raise OwnerModificationError(
            "Organization owner role cannot be modified"
        )

    if new_role == OrganizationRole.owner:
        raise OwnerModificationError(
            "Ownership transfer requires a dedicated workflow"
        )

    membership.role = new_role

    db.commit()
    db.refresh(membership)

    return membership


def remove_organization_member(
    db: Session,
    membership: OrganizationMember,
) -> None:
    if membership.role == OrganizationRole.owner:
        raise OwnerModificationError(
            "Organization owner cannot be removed"
        )

    db.delete(membership)
    db.commit()
