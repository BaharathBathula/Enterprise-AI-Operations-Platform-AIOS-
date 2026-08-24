import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationMembershipResponse,
    OrganizationResponse,
)
from app.services.organization_service import (
    OrganizationAlreadyExistsError,
    create_organization,
    get_membership,
    get_user_memberships,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_organization(
    organization_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    try:
        return create_organization(
            db=db,
            organization_data=organization_data,
            current_user=current_user,
        )
    except OrganizationAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[OrganizationMembershipResponse],
)
def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrganizationMembershipResponse]:
    memberships = get_user_memberships(
        db=db,
        user_id=current_user.id,
    )

    return [
        OrganizationMembershipResponse(
            organization=membership.organization,
            role=membership.role,
        )
        for membership in memberships
    ]


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    membership: OrganizationMember | None = get_membership(
        db=db,
        organization_id=organization_id,
        user_id=current_user.id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return membership.organization
