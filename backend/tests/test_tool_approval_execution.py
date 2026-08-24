import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.tool_approvals import execute_tool_approval
from app.models.tool_approval import (
    ToolApproval,
    ToolApprovalStatus,
)
from app.models.user import User
from app.tools.base import ToolResult


def create_user() -> User:
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    return user


def create_approval(
    *,
    organization_id: uuid.UUID,
    status: ToolApprovalStatus,
) -> ToolApproval:
    return ToolApproval(
        id=uuid.uuid4(),
        organization_id=organization_id,
        requested_by_user_id=uuid.uuid4(),
        conversation_id=None,
        tool_name="create_incident",
        arguments={
            "title": "Checkout API outage",
            "description": (
                "Checkout API is returning "
                "HTTP 503 responses."
            ),
            "severity": "critical",
        },
        status=status,
    )


@pytest.mark.parametrize(
    "approval_status",
    [
        ToolApprovalStatus.pending,
        ToolApprovalStatus.rejected,
        ToolApprovalStatus.executed,
    ],
)
@patch(
    "app.api.v1.tool_approvals.get_tool_approval"
)
def test_execute_blocks_non_approved_requests(
    mock_get_approval,
    approval_status,
):
    organization_id = uuid.uuid4()

    approval = create_approval(
        organization_id=organization_id,
        status=approval_status,
    )

    mock_get_approval.return_value = approval

    with pytest.raises(HTTPException) as exc_info:
        execute_tool_approval(
            organization_id=organization_id,
            approval_id=approval.id,
            _=MagicMock(),
            current_user=create_user(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == 409

    assert exc_info.value.detail == (
        "Only approved tool requests "
        "can be executed"
    )


@patch(
    "app.api.v1.tool_approvals.get_tool_approval"
)
def test_execute_returns_404_for_unknown_approval(
    mock_get_approval,
):
    mock_get_approval.return_value = None

    organization_id = uuid.uuid4()

    with pytest.raises(HTTPException) as exc_info:
        execute_tool_approval(
            organization_id=organization_id,
            approval_id=uuid.uuid4(),
            _=MagicMock(),
            current_user=create_user(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == 404

    assert exc_info.value.detail == (
        "Tool approval request not found"
    )


@patch(
    "app.api.v1.tool_approvals.log_audit_event"
)
@patch(
    "app.api.v1.tool_approvals.ToolExecutor"
)
@patch(
    "app.api.v1.tool_approvals.create_default_tool_registry"
)
@patch(
    "app.api.v1.tool_approvals.get_tool_approval"
)
def test_execute_runs_approved_request(
    mock_get_approval,
    mock_create_registry,
    mock_executor_class,
    mock_audit,
):
    organization_id = uuid.uuid4()

    approval = create_approval(
        organization_id=organization_id,
        status=ToolApprovalStatus.approved,
    )

    mock_get_approval.return_value = approval

    registry = MagicMock()
    mock_create_registry.return_value = registry

    executor = MagicMock()
    mock_executor_class.return_value = executor

    executor.execute.return_value = ToolResult(
        success=True,
        message="Incident created successfully.",
        data={
            "incident_id": str(
                uuid.uuid4()
            ),
            "status": "open",
        },
    )

    db = MagicMock()
    current_user = create_user()

    response = execute_tool_approval(
        organization_id=organization_id,
        approval_id=approval.id,
        _=MagicMock(),
        current_user=current_user,
        db=db,
    )

    assert response.success is True

    executor.execute.assert_called_once_with(
        tool_name="create_incident",
        arguments=approval.arguments,
        context=executor.execute.call_args.kwargs[
            "context"
        ],
        approval_id=approval.id,
    )

    execution_context = (
        executor.execute.call_args.kwargs[
            "context"
        ]
    )

    assert (
        execution_context.organization_id
        == organization_id
    )

    assert (
        execution_context.user_id
        == approval.requested_by_user_id
    )

    assert execution_context.db is db

    mock_audit.assert_called_once()


@patch(
    "app.api.v1.tool_approvals.log_audit_event"
)
@patch(
    "app.api.v1.tool_approvals.ToolExecutor"
)
@patch(
    "app.api.v1.tool_approvals.create_default_tool_registry"
)
@patch(
    "app.api.v1.tool_approvals.get_tool_approval"
)
def test_execute_propagates_tool_failure(
    mock_get_approval,
    mock_create_registry,
    mock_executor_class,
    mock_audit,
):
    organization_id = uuid.uuid4()

    approval = create_approval(
        organization_id=organization_id,
        status=ToolApprovalStatus.approved,
    )

    mock_get_approval.return_value = approval
    mock_create_registry.return_value = MagicMock()

    executor = MagicMock()
    mock_executor_class.return_value = executor

    executor.execute.return_value = ToolResult(
        success=False,
        error="approval_arguments_mismatch",
    )

    with pytest.raises(HTTPException) as exc_info:
        execute_tool_approval(
            organization_id=organization_id,
            approval_id=approval.id,
            _=MagicMock(),
            current_user=create_user(),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == 409

    assert exc_info.value.detail == (
        "approval_arguments_mismatch"
    )

    mock_audit.assert_not_called()
