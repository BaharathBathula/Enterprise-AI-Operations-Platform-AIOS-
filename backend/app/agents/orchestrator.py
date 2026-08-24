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
        cleaned_input = user_input.strip()
        normalized = cleaned_input.lower()

        if self._is_incident_request(normalized):
            severity = self._extract_severity(
                normalized
            )

            return AgentDecision(
                action="tool",
                tool_name="create_incident",
                arguments={
                    "title": cleaned_input[:255],
                    "description": cleaned_input,
                    "severity": severity,
                },
            )

        return AgentDecision(
            action="tool",
            tool_name="knowledge_search",
            arguments={
                "query": cleaned_input,
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
    def _is_incident_request(
        text: str,
    ) -> bool:
        incident_pattern = (
            r"\b(create|open|raise)\b"
            r".{0,40}"
            r"\bincident\b"
        )

        return (
            re.search(
                incident_pattern,
                text,
            )
            is not None
        )

    @staticmethod
    def _extract_severity(
        text: str,
    ) -> str:
        patterns = {
            "critical": (
                r"\bcritical\b"
                r"|\bp0\b"
                r"|\bp1\b"
            ),
            "high": (
                r"\bhigh\b"
                r"|\bp2\b"
            ),
            "medium": (
                r"\bmedium\b"
                r"|\bp3\b"
            ),
            "low": (
                r"\blow\b"
                r"|\bp4\b"
            ),
        }

        for severity, pattern in patterns.items():
            if re.search(
                pattern,
                text,
            ):
                return severity

        return "medium"
