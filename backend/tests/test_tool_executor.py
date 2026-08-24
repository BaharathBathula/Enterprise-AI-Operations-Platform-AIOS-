import uuid
from unittest.mock import (
    MagicMock,
    patch,
)

from app.models.tool_approval import (
    ToolApproval,
    ToolApprovalStatus,
)
from app.tools.base import (
    BaseTool,
    ToolExecutionContext,
    ToolResult,
)
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class SafeTool(BaseTool):
    name = "safe_tool"
    description = "A safe test tool"
    requires_approval = False

    def execute(
        self,
        *,
        context: ToolExecutionContext,
        arguments: dict,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "value": arguments.get(
                    "value"
                )
            },
        )


class DangerousTool(BaseTool):
    name = "dangerous_tool"
    description = "A tool requiring approval"
    requires_approval = True

    def execute(
        self,
        *,
        context: ToolExecutionContext,
        arguments: dict,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            message="Dangerous action executed",
        )


class BrokenTool(BaseTool):
    name = "broken_tool"
    description = "Tool that raises an exception"

    def execute(
        self,
        *,
        context: ToolExecutionContext,
        arguments: dict,
    ) -> ToolResult:
        raise RuntimeError(
            "Something broke"
        )


def create_context():
    return ToolExecutionContext(
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        db=MagicMock(),
    )


@patch(
    "app.tools.executor.log_audit_event"
)
def test_executor_runs_safe_tool(
    mock_audit,
):
    registry = ToolRegistry()
    registry.register(
        SafeTool()
    )

    executor = ToolExecutor(
        registry
    )

    result = executor.execute(
        tool_name="safe_tool",
        arguments={
            "value": "hello",
        },
        context=create_context(),
    )

    assert result.success is True
    assert result.data["value"] == "hello"

    mock_audit.assert_called_once()


def test_executor_blocks_tool_without_approval():
    registry = ToolRegistry()
    registry.register(
        DangerousTool()
    )

    executor = ToolExecutor(
        registry
    )

    result = executor.execute(
        tool_name="dangerous_tool",
        arguments={},
        context=create_context(),
    )

    assert result.success is False
    assert result.error == "approval_required"


@patch(
    "app.tools.executor.get_tool_approval"
)
@patch(
    "app.tools.executor.mark_tool_approval_executed"
)
@patch(
    "app.tools.executor.log_audit_event"
)
def test_executor_runs_with_persisted_approval(
    mock_audit,
    mock_mark_executed,
    mock_get_approval,
):
    registry = ToolRegistry()
    registry.register(
        DangerousTool()
    )

    executor = ToolExecutor(
        registry
    )

    context = create_context()

    approval_id = uuid.uuid4()

    approval = ToolApproval(
        id=approval_id,
        organization_id=context.organization_id,
        requested_by_user_id=uuid.uuid4(),
        tool_name="dangerous_tool",
        arguments={
            "value": "approved",
        },
        status=ToolApprovalStatus.approved,
    )

    mock_get_approval.return_value = approval

    result = executor.execute(
        tool_name="dangerous_tool",
        arguments={
            "value": "approved",
        },
        context=context,
        approval_id=approval_id,
    )

    assert result.success is True

    mock_get_approval.assert_called_once_with(
        db=context.db,
        organization_id=context.organization_id,
        approval_id=approval_id,
    )

    mock_mark_executed.assert_called_once_with(
        db=context.db,
        approval=approval,
    )

    mock_audit.assert_called_once()


@patch(
    "app.tools.executor.get_tool_approval"
)
def test_executor_rejects_unapproved_record(
    mock_get_approval,
):
    registry = ToolRegistry()
    registry.register(
        DangerousTool()
    )

    executor = ToolExecutor(
        registry
    )

    context = create_context()

    approval = ToolApproval(
        id=uuid.uuid4(),
        organization_id=context.organization_id,
        requested_by_user_id=uuid.uuid4(),
        tool_name="dangerous_tool",
        arguments={},
        status=ToolApprovalStatus.pending,
    )

    mock_get_approval.return_value = approval

    result = executor.execute(
        tool_name="dangerous_tool",
        arguments={},
        context=context,
        approval_id=approval.id,
    )

    assert result.success is False

    assert (
        result.error
        == "approval_not_approved"
    )


@patch(
    "app.tools.executor.get_tool_approval"
)
def test_executor_rejects_tool_mismatch(
    mock_get_approval,
):
    registry = ToolRegistry()
    registry.register(
        DangerousTool()
    )

    executor = ToolExecutor(
        registry
    )

    context = create_context()

    approval = ToolApproval(
        id=uuid.uuid4(),
        organization_id=context.organization_id,
        requested_by_user_id=uuid.uuid4(),
        tool_name="another_tool",
        arguments={},
        status=ToolApprovalStatus.approved,
    )

    mock_get_approval.return_value = approval

    result = executor.execute(
        tool_name="dangerous_tool",
        arguments={},
        context=context,
        approval_id=approval.id,
    )

    assert result.success is False

    assert (
        result.error
        == "approval_tool_mismatch"
    )


@patch(
    "app.tools.executor.get_tool_approval"
)
def test_executor_rejects_argument_mismatch(
    mock_get_approval,
):
    registry = ToolRegistry()
    registry.register(
        DangerousTool()
    )

    executor = ToolExecutor(
        registry
    )

    context = create_context()

    approval = ToolApproval(
        id=uuid.uuid4(),
        organization_id=context.organization_id,
        requested_by_user_id=uuid.uuid4(),
        tool_name="dangerous_tool",
        arguments={
            "severity": "low",
        },
        status=ToolApprovalStatus.approved,
    )

    mock_get_approval.return_value = approval

    result = executor.execute(
        tool_name="dangerous_tool",
        arguments={
            "severity": "critical",
        },
        context=context,
        approval_id=approval.id,
    )

    assert result.success is False

    assert (
        result.error
        == "approval_arguments_mismatch"
    )


def test_executor_handles_unknown_tool():
    registry = ToolRegistry()

    executor = ToolExecutor(
        registry
    )

    result = executor.execute(
        tool_name="missing",
        arguments={},
        context=create_context(),
    )

    assert result.success is False

    assert "not registered" in (
        result.error or ""
    )


@patch(
    "app.tools.executor.log_audit_event"
)
def test_executor_contains_tool_exception(
    mock_audit,
):
    registry = ToolRegistry()
    registry.register(
        BrokenTool()
    )

    executor = ToolExecutor(
        registry
    )

    result = executor.execute(
        tool_name="broken_tool",
        arguments={},
        context=create_context(),
    )

    assert result.success is False

    assert result.error == (
        "Tool execution failed: RuntimeError"
    )

    mock_audit.assert_called_once()
