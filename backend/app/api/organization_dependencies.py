import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.organization_member import (
    OrganizationMember,
    OrganizationRole,
)
from app.models.user import User
from app.services.organization_service import get_membership


def get_current_membership(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMember:
    membership = get_membership(
        db=db,
        organization_id=organization_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return membership


def require_organization_admin(
    membership: OrganizationMember = Depends(
        get_current_membership,
    ),
) -> OrganizationMember:
    allowed_roles = {
        OrganizationRole.owner,
        OrganizationRole.admin,
    }

    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization administrator access required",
        )

    return membership


def require_organization_owner(
    membership: OrganizationMember = Depends(
        get_current_membership,
    ),
) -> OrganizationMember:
    if membership.role != OrganizationRole.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization owner access required",
        )

    return membership
