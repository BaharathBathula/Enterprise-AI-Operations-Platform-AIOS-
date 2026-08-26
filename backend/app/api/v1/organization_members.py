import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.organization_dependencies import (
    get_current_membership,
    require_organization_admin,
)
from app.db.database import get_db
from app.models.organization_member import (
    OrganizationMember,
)
from app.schemas.organization import (
    OrganizationMemberAdd,
    OrganizationMemberResponse,
    OrganizationMemberRoleUpdate,
)
from app.services.membership_service import (
    MemberAlreadyExistsError,
    OwnerModificationError,
    UserNotFoundError,
    add_organization_member,
    get_organization_member,
    list_organization_members,
    remove_organization_member,
    update_member_role,
)


router = APIRouter(
    prefix=(
        "/organizations/"
        "{organization_id}/members"
    ),
    tags=["Organization Members"],
)


def serialize_membership(
    membership: OrganizationMember,
) -> OrganizationMemberResponse:
    return OrganizationMemberResponse(
        id=membership.id,
        user_id=membership.user_id,
        email=membership.user.email,
        full_name=membership.user.full_name,
        role=membership.role,
        created_at=membership.created_at,
    )


@router.get(
    "",
    response_model=list[
        OrganizationMemberResponse
    ],
)
def list_members(
    organization_id: uuid.UUID,
    _: OrganizationMember = Depends(
        get_current_membership,
    ),
    db: Session = Depends(get_db),
) -> list[OrganizationMemberResponse]:
    memberships = (
        list_organization_members(
            db,
            organization_id,
        )
    )

    return [
        serialize_membership(
            membership
        )
        for membership
        in memberships
    ]


@router.post(
    "",
    response_model=(
        OrganizationMemberResponse
    ),
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def add_member(
    organization_id: uuid.UUID,
    member_data: OrganizationMemberAdd,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    db: Session = Depends(get_db),
) -> OrganizationMemberResponse:
    try:
        membership = (
            add_organization_member(
                db=db,
                organization_id=(
                    organization_id
                ),
                email=str(
                    member_data.email
                ),
                role=member_data.role,
            )
        )

    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc

    except MemberAlreadyExistsError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(exc),
        ) from exc

    except OwnerModificationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(exc),
        ) from exc

    membership = (
        get_organization_member(
            db,
            organization_id,
            membership.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Failed to retrieve "
                "created membership"
            ),
        )

    return serialize_membership(
        membership
    )


@router.patch(
    "/{member_id}",
    response_model=(
        OrganizationMemberResponse
    ),
)
def change_member_role(
    organization_id: uuid.UUID,
    member_id: uuid.UUID,
    role_data: OrganizationMemberRoleUpdate,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    db: Session = Depends(get_db),
) -> OrganizationMemberResponse:
    membership = (
        get_organization_member(
            db,
            organization_id,
            member_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Organization member "
                "not found"
            ),
        )

    try:
        membership = (
            update_member_role(
                db,
                membership,
                role_data.role,
            )
        )

    except OwnerModificationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(exc),
        ) from exc

    return serialize_membership(
        membership
    )


@router.delete(
    "/{member_id}",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def delete_member(
    organization_id: uuid.UUID,
    member_id: uuid.UUID,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    db: Session = Depends(get_db),
) -> Response:
    membership = (
        get_organization_member(
            db,
            organization_id,
            member_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Organization member "
                "not found"
            ),
        )

    try:
        remove_organization_member(
            db,
            membership,
        )

    except OwnerModificationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(exc),
        ) from exc

    return Response(
        status_code=(
            status.HTTP_204_NO_CONTENT
        )
    )
