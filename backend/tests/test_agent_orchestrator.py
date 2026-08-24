import uuid
from unittest.mock import MagicMock

from app.agents.orchestrator import (
    AgentOrchestrator,
)
from app.models.tool_approval import ToolApproval
from app.tools.base import (
    BaseTool,
    ToolExecutionContext,
    ToolResult,
)
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class KnowledgeTool(BaseTool):
    name = "knowledge_search"
    description = "Search knowledge"
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
                "query": arguments["query"],
            },
        )


class IncidentTool(BaseTool):
    name = "create_incident"
    description = "Create incident"
    requires_approval = True

    def execute(
        self,
        *,
        context: ToolExecutionContext,
        arguments: dict,
    ) -> ToolResult:
        return ToolResult(
            success=True,
        )


def create_orchestrator():
    registry = ToolRegistry()

    registry.register(
        KnowledgeTool()
    )

    registry.register(
        IncidentTool()
    )

    executor = ToolExecutor(
        registry
    )

    return AgentOrchestrator(
        executor
    )


def create_context():
    return ToolExecutionContext(
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
        db=MagicMock(),
    )


def test_agent_routes_question_to_knowledge_search():
    orchestrator = create_orchestrator()

    decision = orchestrator.decide(
        "What is the cancellation period?"
    )

    assert decision.tool_name == (
        "knowledge_search"
    )

    assert decision.arguments == {
        "query": "What is the cancellation period?",
        "limit": 5,
    }


def test_agent_routes_incident_request_to_incident_tool():
    orchestrator = create_orchestrator()

    decision = orchestrator.decide(
        "Create incident for critical API outage"
    )

    assert decision.tool_name == (
        "create_incident"
    )

    assert (
        decision.arguments["severity"]
        == "critical"
    )


def test_agent_maps_p1_to_critical():
    orchestrator = create_orchestrator()

    decision = orchestrator.decide(
        "Raise a P1 incident for checkout outage"
    )

    assert (
        decision.arguments["severity"]
        == "critical"
    )


def test_agent_executes_safe_tool():
    orchestrator = create_orchestrator()

    result = orchestrator.handle(
        user_input="What is the deductible?",
        context=create_context(),
    )

    assert result.success is True

    assert result.data["query"] == (
        "What is the deductible?"
    )

def test_agent_creates_approval_for_write_tool(
    monkeypatch,
):
    orchestrator = create_orchestrator()

    context = create_context()

    approval_id = uuid.uuid4()

    approval = ToolApproval(
        id=approval_id,
        organization_id=context.organization_id,
        requested_by_user_id=context.user_id,
        tool_name="create_incident",
        arguments={},
    )

    def fake_create_tool_approval(**kwargs):
        return approval

    monkeypatch.setattr(
        "app.agents.orchestrator.create_tool_approval",
        fake_create_tool_approval,
    )

    result = orchestrator.handle(
        user_input=(
            "Create incident for critical "
            "production outage"
        ),
        context=context,
    )

    assert result.success is False
    assert result.error == "approval_required"

    assert result.data["approval_id"] == (
        str(approval_id)
    )

    assert result.data["tool_name"] == (
        "create_incident"
    )
