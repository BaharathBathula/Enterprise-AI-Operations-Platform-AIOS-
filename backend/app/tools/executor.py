import time
import uuid
from typing import Any

from app.models.tool_approval import ToolApprovalStatus
from app.services.audit_service import log_audit_event
from app.services.tool_approval_service import (
    get_tool_approval,
    mark_tool_approval_executed,
)
from app.tools.base import (
    ToolExecutionContext,
    ToolResult,
)
from app.tools.registry import (
    ToolNotFoundError,
    ToolRegistry,
)


class ToolExecutor:
    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self.registry = registry

    def execute(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        context: ToolExecutionContext,
        approval_id: uuid.UUID | None = None,
    ) -> ToolResult:
        try:
            tool = self.registry.get(
                tool_name
            )

        except ToolNotFoundError as exc:
            return ToolResult(
                success=False,
                error=str(exc),
            )

        approval = None

        if tool.requires_approval:
            approval_result = self._validate_approval(
                tool_name=tool.name,
                arguments=arguments,
                context=context,
                approval_id=approval_id,
            )

            if isinstance(
                approval_result,
                ToolResult,
            ):
                return approval_result

            approval = approval_result

        started_at = time.perf_counter()

        try:
            result = tool.execute(
                context=context,
                arguments=arguments,
            )

        except Exception as exc:
            result = ToolResult(
                success=False,
                error=(
                    "Tool execution failed: "
                    f"{type(exc).__name__}"
                ),
            )

        duration_ms = round(
            (
                time.perf_counter()
                - started_at
            )
            * 1000,
            2,
        )

        if (
            result.success
            and approval is not None
            and context.db is not None
        ):
            mark_tool_approval_executed(
                db=context.db,
                approval=approval,
            )

        self._audit_execution(
            tool_name=tool.name,
            arguments=arguments,
            result=result,
            context=context,
            duration_ms=duration_ms,
            approval_id=(
                approval.id
                if approval is not None
                else None
            ),
        )

        return result

    @staticmethod
    def _validate_approval(
        *,
        tool_name: str,
        arguments: dict[str, Any],
        context: ToolExecutionContext,
        approval_id: uuid.UUID | None,
    ) -> Any:
        if context.db is None:
            return ToolResult(
                success=False,
                error="Database session is required",
            )

        if approval_id is None:
            return ToolResult(
                success=False,
                message=(
                    f"Tool '{tool_name}' "
                    "requires human approval."
                ),
                error="approval_required",
                data={
                    "tool_name": tool_name,
                    "requires_approval": True,
                },
            )

        approval = get_tool_approval(
            db=context.db,
            organization_id=context.organization_id,
            approval_id=approval_id,
        )

        if approval is None:
            return ToolResult(
                success=False,
                error="approval_not_found",
            )

        if (
            approval.status
            != ToolApprovalStatus.approved
        ):
            return ToolResult(
                success=False,
                error="approval_not_approved",
            )

        if approval.tool_name != tool_name:
            return ToolResult(
                success=False,
                error="approval_tool_mismatch",
            )

        if approval.arguments != arguments:
            return ToolResult(
                success=False,
                error="approval_arguments_mismatch",
            )

        return approval

    @staticmethod
    def _audit_execution(
        *,
        tool_name: str,
        arguments: dict[str, Any],
        result: ToolResult,
        context: ToolExecutionContext,
        duration_ms: float,
        approval_id: uuid.UUID | None,
    ) -> None:
        if context.db is None:
            return

        log_audit_event(
            db=context.db,
            action="tool.executed",
            resource_type="tool",
            organization_id=context.organization_id,
            user_id=context.user_id,
            resource_id=tool_name,
            details={
                "tool_name": tool_name,
                "success": result.success,
                "duration_ms": duration_ms,
                "argument_keys": sorted(
                    arguments.keys()
                ),
                "approval_id": (
                    str(approval_id)
                    if approval_id
                    else None
                ),
                "error": result.error,
            },
        )
