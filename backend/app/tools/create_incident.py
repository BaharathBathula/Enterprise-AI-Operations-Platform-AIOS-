from typing import Any

from app.models.incident import (
    Incident,
    IncidentSeverity,
    IncidentStatus,
)
from app.tools.base import (
    BaseTool,
    ToolExecutionContext,
    ToolResult,
)


class CreateIncidentTool(BaseTool):
    name = "create_incident"

    description = (
        "Create an enterprise operational incident. "
        "This is a write action and requires human approval."
    )

    requires_approval = True

    def execute(
        self,
        *,
        context: ToolExecutionContext,
        arguments: dict[str, Any],
    ) -> ToolResult:
        if context.db is None:
            return ToolResult(
                success=False,
                error="Database session is required",
            )

        title = str(
            arguments.get(
                "title",
                "",
            )
        ).strip()

        description = str(
            arguments.get(
                "description",
                "",
            )
        ).strip()

        severity_value = str(
            arguments.get(
                "severity",
                "",
            )
        ).strip().lower()

        if not title:
            return ToolResult(
                success=False,
                error="Incident title is required",
            )

        if len(title) > 255:
            return ToolResult(
                success=False,
                error=(
                    "Incident title must be "
                    "255 characters or fewer"
                ),
            )

        if not description:
            return ToolResult(
                success=False,
                error="Incident description is required",
            )

        try:
            severity = IncidentSeverity(
                severity_value
            )

        except ValueError:
            allowed = ", ".join(
                item.value
                for item in IncidentSeverity
            )

            return ToolResult(
                success=False,
                error=(
                    "Invalid incident severity. "
                    f"Allowed values: {allowed}"
                ),
            )

        incident = Incident(
            organization_id=context.organization_id,
            created_by_user_id=context.user_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.open,
            source="aios-agent",
        )

        context.db.add(incident)
        context.db.commit()
        context.db.refresh(incident)

        return ToolResult(
            success=True,
            data={
                "incident_id": str(
                    incident.id
                ),
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "source": incident.source,
            },
            message=(
                f"Incident '{incident.title}' "
                "was created successfully."
            ),
        )
