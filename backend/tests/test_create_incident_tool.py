import uuid
from unittest.mock import MagicMock

from app.models.incident import (
    IncidentSeverity,
    IncidentStatus,
)
from app.tools.base import ToolExecutionContext
from app.tools.create_incident import (
    CreateIncidentTool,
)
from app.tools.default_registry import (
    create_default_tool_registry,
)


def create_context():
    return ToolExecutionContext(
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        db=MagicMock(),
    )


def test_create_incident_requires_approval():
    tool = CreateIncidentTool()

    assert tool.requires_approval is True


def test_create_incident_requires_database():
    tool = CreateIncidentTool()

    context = ToolExecutionContext(
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
    )

    result = tool.execute(
        context=context,
        arguments={
            "title": "Production outage",
            "description": "API unavailable",
            "severity": "critical",
        },
    )

    assert result.success is False
    assert result.error == (
        "Database session is required"
    )


def test_create_incident_requires_title():
    tool = CreateIncidentTool()

    result = tool.execute(
        context=create_context(),
        arguments={
            "description": "API unavailable",
            "severity": "critical",
        },
    )

    assert result.success is False
    assert result.error == (
        "Incident title is required"
    )


def test_create_incident_requires_description():
    tool = CreateIncidentTool()

    result = tool.execute(
        context=create_context(),
        arguments={
            "title": "Production outage",
            "severity": "critical",
        },
    )

    assert result.success is False
    assert result.error == (
        "Incident description is required"
    )


def test_create_incident_rejects_invalid_severity():
    tool = CreateIncidentTool()

    result = tool.execute(
        context=create_context(),
        arguments={
            "title": "Production outage",
            "description": "API unavailable",
            "severity": "p1",
        },
    )

    assert result.success is False

    assert "Invalid incident severity" in (
        result.error or ""
    )


def test_create_incident_persists_incident():
    tool = CreateIncidentTool()

    context = create_context()

    def assign_incident_id(incident):
        incident.id = uuid.uuid4()

    context.db.refresh.side_effect = (
        assign_incident_id
    )

    result = tool.execute(
        context=context,
        arguments={
            "title": "Production API outage",
            "description": (
                "Checkout API is returning "
                "HTTP 503 responses."
            ),
            "severity": "critical",
        },
    )

    assert result.success is True

    context.db.add.assert_called_once()
    context.db.commit.assert_called_once()
    context.db.refresh.assert_called_once()

    incident = (
        context.db.add.call_args.args[0]
    )

    assert (
        incident.organization_id
        == context.organization_id
    )

    assert (
        incident.created_by_user_id
        == context.user_id
    )

    assert (
        incident.severity
        == IncidentSeverity.critical
    )

    assert (
        incident.status
        == IncidentStatus.open
    )

    assert (
        incident.source
        == "aios-agent"
    )

    assert (
        result.data["severity"]
        == "critical"
    )

    assert (
        result.data["status"]
        == "open"
    )


def test_default_registry_contains_create_incident():
    registry = create_default_tool_registry()

    assert registry.contains(
        "create_incident"
    )

    tool = registry.get(
        "create_incident"
    )

    assert tool.requires_approval is True
