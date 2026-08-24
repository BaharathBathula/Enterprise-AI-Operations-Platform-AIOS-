import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tool_approval import (
    ToolApproval,
    ToolApprovalStatus,
)


class ToolApprovalStateError(Exception):
    pass


def create_tool_approval(
    db: Session,
    *,
    organization_id: uuid.UUID,
    requested_by_user_id: uuid.UUID,
    tool_name: str,
    arguments: dict[str, Any],
    conversation_id: uuid.UUID | None = None,
) -> ToolApproval:
    approval = ToolApproval(
        organization_id=organization_id,
        requested_by_user_id=requested_by_user_id,
        conversation_id=conversation_id,
        tool_name=tool_name,
        arguments=arguments,
        status=ToolApprovalStatus.pending,
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


def get_tool_approval(
    db: Session,
    *,
    organization_id: uuid.UUID,
    approval_id: uuid.UUID,
) -> ToolApproval | None:
    statement = select(
        ToolApproval
    ).where(
        ToolApproval.id == approval_id,
        ToolApproval.organization_id == organization_id,
    )

    return db.scalar(statement)


def list_tool_approvals(
    db: Session,
    *,
    organization_id: uuid.UUID,
    status: ToolApprovalStatus | None = None,
    limit: int = 100,
) -> list[ToolApproval]:
    statement = select(
        ToolApproval
    ).where(
        ToolApproval.organization_id == organization_id,
    )

    if status is not None:
        statement = statement.where(
            ToolApproval.status == status,
        )

    statement = (
        statement
        .order_by(
            ToolApproval.created_at.desc(),
        )
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )


def approve_tool_request(
    db: Session,
    *,
    approval: ToolApproval,
    reviewed_by_user_id: uuid.UUID,
    review_note: str | None = None,
) -> ToolApproval:
    if approval.status != ToolApprovalStatus.pending:
        raise ToolApprovalStateError(
            "Only pending tool requests can be approved"
        )

    approval.status = ToolApprovalStatus.approved
    approval.reviewed_by_user_id = reviewed_by_user_id
    approval.review_note = review_note
    approval.reviewed_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(approval)

    return approval


def reject_tool_request(
    db: Session,
    *,
    approval: ToolApproval,
    reviewed_by_user_id: uuid.UUID,
    review_note: str | None = None,
) -> ToolApproval:
    if approval.status != ToolApprovalStatus.pending:
        raise ToolApprovalStateError(
            "Only pending tool requests can be rejected"
        )

    approval.status = ToolApprovalStatus.rejected
    approval.reviewed_by_user_id = reviewed_by_user_id
    approval.review_note = review_note
    approval.reviewed_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(approval)

    return approval


def mark_tool_approval_executed(
    db: Session,
    *,
    approval: ToolApproval,
) -> ToolApproval:
    if approval.status != ToolApprovalStatus.approved:
        raise ToolApprovalStateError(
            "Only approved tool requests can be executed"
        )

    approval.status = ToolApprovalStatus.executed
    approval.executed_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(approval)

    return approval
