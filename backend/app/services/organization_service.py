import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.organization import Organization
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User
from app.schemas.organization import OrganizationCreate


class OrganizationAlreadyExistsError(Exception):
    pass


def get_organization_by_slug(
    db: Session,
    slug: str,
) -> Organization | None:
    statement = select(Organization).where(
        Organization.slug == slug.strip().lower(),
    )

    return db.scalar(statement)


def create_organization(
    db: Session,
    organization_data: OrganizationCreate,
    current_user: User,
) -> Organization:
    organization = Organization(
        name=organization_data.name.strip(),
        slug=organization_data.slug.strip().lower(),
    )

    membership = OrganizationMember(
        organization=organization,
        user=current_user,
        role=OrganizationRole.owner,
    )

    db.add(organization)
    db.add(membership)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise OrganizationAlreadyExistsError(
            "An organization with this slug already exists"
        ) from exc

    db.refresh(organization)

    return organization


def get_user_memberships(
    db: Session,
    user_id: uuid.UUID,
) -> list[OrganizationMember]:
    statement = (
        select(OrganizationMember)
        .options(
            joinedload(OrganizationMember.organization),
        )
        .where(
            OrganizationMember.user_id == user_id,
        )
        .order_by(
            OrganizationMember.created_at.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_membership(
    db: Session,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
) -> OrganizationMember | None:
    statement = select(OrganizationMember).where(
        OrganizationMember.organization_id == organization_id,
        OrganizationMember.user_id == user_id,
    )

    return db.scalar(statement)
