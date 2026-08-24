import time
from typing import Any

from app.services.audit_service import log_audit_event
from app.tools.base import (
    ToolExecutionContext,
    ToolResult,
)
from app.tools.registry import (
    ToolNotFoundError,
    ToolRegistry,
)


class ToolApprovalRequiredError(Exception):
    pass


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
        approved: bool = False,
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

        if (
            tool.requires_approval
            and not approved
        ):
            return ToolResult(
                success=False,
                message=(
                    f"Tool '{tool.name}' requires approval."
                ),
                error="approval_required",
                data={
                    "tool_name": tool.name,
                    "requires_approval": True,
                },
            )

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
                    f"Tool execution failed: "
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

        self._audit_execution(
            tool_name=tool.name,
            arguments=arguments,
            result=result,
            context=context,
            duration_ms=duration_ms,
        )

        return result

    @staticmethod
    def _audit_execution(
        *,
        tool_name: str,
        arguments: dict[str, Any],
        result: ToolResult,
        context: ToolExecutionContext,
        duration_ms: float,
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
                "error": result.error,
            },
        )
