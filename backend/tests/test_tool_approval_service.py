import uuid
from unittest.mock import MagicMock

import pytest

from app.models.tool_approval import (
    ToolApproval,
    ToolApprovalStatus,
)
from app.services.tool_approval_service import (
    ToolApprovalStateError,
    approve_tool_request,
    mark_tool_approval_executed,
    reject_tool_request,
)


def create_approval(
    status: ToolApprovalStatus,
) -> ToolApproval:
    return ToolApproval(
        id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        requested_by_user_id=uuid.uuid4(),
        tool_name="create_incident",
        arguments={
            "title": "Production outage",
        },
        status=status,
    )


def test_pending_request_can_be_approved():
    db = MagicMock()

    approval = create_approval(
        ToolApprovalStatus.pending
    )

    reviewer_id = uuid.uuid4()

    result = approve_tool_request(
        db=db,
        approval=approval,
        reviewed_by_user_id=reviewer_id,
        review_note="Approved for execution",
    )

    assert result.status == ToolApprovalStatus.approved
    assert result.reviewed_by_user_id == reviewer_id
    assert result.reviewed_at is not None

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(
        approval
    )


def test_pending_request_can_be_rejected():
    db = MagicMock()

    approval = create_approval(
        ToolApprovalStatus.pending
    )

    result = reject_tool_request(
        db=db,
        approval=approval,
        reviewed_by_user_id=uuid.uuid4(),
        review_note="Action is too risky",
    )

    assert result.status == ToolApprovalStatus.rejected
    assert result.reviewed_at is not None

    db.commit.assert_called_once()


def test_approved_request_cannot_be_approved_again():
    db = MagicMock()

    approval = create_approval(
        ToolApprovalStatus.approved
    )

    with pytest.raises(
        ToolApprovalStateError
    ):
        approve_tool_request(
            db=db,
            approval=approval,
            reviewed_by_user_id=uuid.uuid4(),
        )

    db.commit.assert_not_called()


def test_rejected_request_cannot_be_approved():
    db = MagicMock()

    approval = create_approval(
        ToolApprovalStatus.rejected
    )

    with pytest.raises(
        ToolApprovalStateError
    ):
        approve_tool_request(
            db=db,
            approval=approval,
            reviewed_by_user_id=uuid.uuid4(),
        )

    db.commit.assert_not_called()


def test_approved_request_can_be_marked_executed():
    db = MagicMock()

    approval = create_approval(
        ToolApprovalStatus.approved
    )

    result = mark_tool_approval_executed(
        db=db,
        approval=approval,
    )

    assert result.status == ToolApprovalStatus.executed
    assert result.executed_at is not None

    db.commit.assert_called_once()


def test_pending_request_cannot_be_marked_executed():
    db = MagicMock()

    approval = create_approval(
        ToolApprovalStatus.pending
    )

    with pytest.raises(
        ToolApprovalStateError
    ):
        mark_tool_approval_executed(
            db=db,
            approval=approval,
        )

    db.commit.assert_not_called()
