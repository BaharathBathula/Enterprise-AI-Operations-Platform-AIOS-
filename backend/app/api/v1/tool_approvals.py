import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.organization_dependencies import (
    require_organization_admin,
)
from app.db.database import get_db
from app.models.organization_member import OrganizationMember
from app.models.tool_approval import ToolApprovalStatus
from app.models.user import User
from app.schemas.tool_approval import (
    ToolApprovalExecutionResponse,
    ToolApprovalResponse,
    ToolApprovalReviewRequest,
)
from app.services.audit_service import log_audit_event
from app.services.tool_approval_service import (
    ToolApprovalStateError,
    approve_tool_request,
    get_tool_approval,
    list_tool_approvals,
    reject_tool_request,
)
from app.tools.base import ToolExecutionContext
from app.tools.default_registry import (
    create_default_tool_registry,
)
from app.tools.executor import ToolExecutor


router = APIRouter(
    prefix="/organizations/{organization_id}/tool-approvals",
    tags=["Tool Approvals"],
)


@router.get(
    "",
    response_model=list[ToolApprovalResponse],
)
def get_tool_approvals(
    organization_id: uuid.UUID,
    approval_status: ToolApprovalStatus | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    db: Session = Depends(get_db),
) -> list[ToolApprovalResponse]:
    return list_tool_approvals(
        db=db,
        organization_id=organization_id,
        status=approval_status,
        limit=limit,
    )


@router.get(
    "/{approval_id}",
    response_model=ToolApprovalResponse,
)
def get_tool_approval_by_id(
    organization_id: uuid.UUID,
    approval_id: uuid.UUID,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    db: Session = Depends(get_db),
) -> ToolApprovalResponse:
    approval = get_tool_approval(
        db=db,
        organization_id=organization_id,
        approval_id=approval_id,
    )

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool approval request not found",
        )

    return approval


@router.post(
    "/{approval_id}/approve",
    response_model=ToolApprovalResponse,
)
def approve_tool_approval(
    organization_id: uuid.UUID,
    approval_id: uuid.UUID,
    request: ToolApprovalReviewRequest,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> ToolApprovalResponse:
    approval = get_tool_approval(
        db=db,
        organization_id=organization_id,
        approval_id=approval_id,
    )

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool approval request not found",
        )

    if approval.requested_by_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Users cannot approve their own "
                "tool requests"
            ),
        )

    try:
        approval = approve_tool_request(
            db=db,
            approval=approval,
            reviewed_by_user_id=current_user.id,
            review_note=request.review_note,
        )

    except ToolApprovalStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    log_audit_event(
        db=db,
        action="tool.approved",
        resource_type="tool_approval",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=str(approval.id),
        details={
            "tool_name": approval.tool_name,
            "requested_by_user_id": str(
                approval.requested_by_user_id
            ),
        },
    )

    return approval


@router.post(
    "/{approval_id}/reject",
    response_model=ToolApprovalResponse,
)
def reject_tool_approval(
    organization_id: uuid.UUID,
    approval_id: uuid.UUID,
    request: ToolApprovalReviewRequest,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> ToolApprovalResponse:
    approval = get_tool_approval(
        db=db,
        organization_id=organization_id,
        approval_id=approval_id,
    )

        if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool approval request not found",
        )

    if approval.requested_by_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Users cannot reject their own "
                "tool requests"
            ),
        )

    try:
        approval = reject_tool_request(

    except ToolApprovalStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    log_audit_event(
        db=db,
        action="tool.rejected",
        resource_type="tool_approval",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=str(approval.id),
        details={
            "tool_name": approval.tool_name,
            "requested_by_user_id": str(
                approval.requested_by_user_id
            ),
        },
    )

    return approval


@router.post(
    "/{approval_id}/execute",
    response_model=ToolApprovalExecutionResponse,
)
def execute_tool_approval(
    organization_id: uuid.UUID,
    approval_id: uuid.UUID,
    _: OrganizationMember = Depends(
        require_organization_admin,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
) -> ToolApprovalExecutionResponse:
    approval = get_tool_approval(
        db=db,
        organization_id=organization_id,
        approval_id=approval_id,
    )

    if approval is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool approval request not found",
        )

    if approval.status != ToolApprovalStatus.approved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Only approved tool requests "
                "can be executed"
            ),
        )

    registry = create_default_tool_registry()

    executor = ToolExecutor(
        registry
    )

    context = ToolExecutionContext(
        organization_id=organization_id,
        user_id=approval.requested_by_user_id,
        conversation_id=approval.conversation_id,
        db=db,
    )

    result = executor.execute(
        tool_name=approval.tool_name,
        arguments=approval.arguments,
        context=context,
        approval_id=approval.id,
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                result.error
                or "Tool execution failed"
            ),
        )

    log_audit_event(
        db=db,
        action="tool.approval_executed",
        resource_type="tool_approval",
        organization_id=organization_id,
        user_id=current_user.id,
        resource_id=str(approval.id),
        details={
            "tool_name": approval.tool_name,
            "requested_by_user_id": str(
                approval.requested_by_user_id
            ),
        },
    )

    return ToolApprovalExecutionResponse(
        success=result.success,
        message=result.message,
        error=result.error,
        data=result.data,
    )
