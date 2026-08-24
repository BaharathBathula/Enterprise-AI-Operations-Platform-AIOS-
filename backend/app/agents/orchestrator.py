import re
from dataclasses import dataclass
from typing import Any

from app.services.tool_approval_service import create_tool_approval
from app.tools.base import ToolExecutionContext, ToolResult
from app.tools.executor import ToolExecutor


@dataclass
class AgentDecision:
    action: str
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None


class AgentOrchestrator:
    def __init__(
        self,
        executor: ToolExecutor,
    ) -> None:
        self.executor = executor

    def decide(
        self,
        user_input: str,
    ) -> AgentDecision:
        normalized = user_input.strip().lower()

        if any(
            phrase in normalized
            for phrase in (
                "create incident",
                "open incident",
                "raise incident",
            )
        ):
            severity = self._extract_severity(
                normalized
            )

            return AgentDecision(
                action="tool",
                tool_name="create_incident",
                arguments={
                    "title": user_input.strip()[:255],
                    "description": user_input.strip(),
                    "severity": severity,
                },
            )

        return AgentDecision(
            action="tool",
            tool_name="knowledge_search",
            arguments={
                "query": user_input.strip(),
                "limit": 5,
            },
        )

    def handle(
        self,
        *,
        user_input: str,
        context: ToolExecutionContext,
    ) -> ToolResult:
        decision = self.decide(
            user_input
        )

        if (
            decision.tool_name is None
            or decision.arguments is None
        ):
            return ToolResult(
                success=False,
                error="No executable agent decision",
            )

        tool = self.executor.registry.get(
            decision.tool_name
        )

        if tool.requires_approval:
            if context.db is None:
                return ToolResult(
                    success=False,
                    error="Database session is required",
                )

            approval = create_tool_approval(
                db=context.db,
                organization_id=context.organization_id,
                requested_by_user_id=context.user_id,
                conversation_id=context.conversation_id,
                tool_name=decision.tool_name,
                arguments=decision.arguments,
            )

            return ToolResult(
                success=False,
                error="approval_required",
                message=(
                    f"Tool '{decision.tool_name}' "
                    "requires human approval."
                ),
                data={
                    "approval_id": str(
                        approval.id
                    ),
                    "tool_name": decision.tool_name,
                    "arguments": decision.arguments,
                },
            )

        return self.executor.execute(
            tool_name=decision.tool_name,
            arguments=decision.arguments,
            context=context,
        )

    @staticmethod
    def _extract_severity(
        text: str,
    ) -> str:
        patterns = {
            "critical": r"\bcritical\b|\bp0\b|\bp1\b",
            "high": r"\bhigh\b|\bp2\b",
            "medium": r"\bmedium\b|\bp3\b",
            "low": r"\blow\b|\bp4\b",
        }

        for severity, pattern in patterns.items():
            if re.search(
                pattern,
                text,
            ):
                return severity

        return "medium"
