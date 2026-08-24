import uuid
from unittest.mock import MagicMock, patch

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
            "value": "hello"
        },
        context=create_context(),
    )

    assert result.success is True
    assert result.data["value"] == "hello"

    mock_audit.assert_called_once()


@patch(
    "app.tools.executor.log_audit_event"
)
def test_executor_blocks_unapproved_tool(
    mock_audit,
):
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

    mock_audit.assert_not_called()


@patch(
    "app.tools.executor.log_audit_event"
)
def test_executor_runs_approved_tool(
    mock_audit,
):
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
        approved=True,
    )

    assert result.success is True

    mock_audit.assert_called_once()


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


@patch(
    "app.tools.executor.log_audit_event"
)
def test_executor_does_not_audit_raw_arguments(
    mock_audit,
):
    registry = ToolRegistry()
    registry.register(
        SafeTool()
    )

    executor = ToolExecutor(
        registry
    )

    context = create_context()

    executor.execute(
        tool_name="safe_tool",
        arguments={
            "api_key": "secret-value",
            "customer": "private-data",
        },
        context=context,
    )

    audit_call = mock_audit.call_args.kwargs

    details = audit_call[
        "details"
    ]

    assert "api_key" in details[
        "argument_keys"
    ]

    assert "customer" in details[
        "argument_keys"
    ]

    assert "secret-value" not in str(
        details
    )

    assert "private-data" not in str(
        details
    )
