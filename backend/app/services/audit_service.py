import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_audit_event(
    db: Session,
    *,
    action: str,
    resource_type: str,
    organization_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    event_type: str = "general",
    outcome: str = "success",
) -> AuditLog:
    audit_log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        event_type=event_type,
        action=action,
        outcome=outcome,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def list_organization_audit_logs(
    db: Session,
    *,
    organization_id: uuid.UUID,
    event_type: str | None = None,
    outcome: str | None = None,
    limit: int = 100,
) -> list[AuditLog]:
    statement = select(AuditLog).where(
        AuditLog.organization_id == organization_id,
    )

    if event_type is not None:
        statement = statement.where(
            AuditLog.event_type == event_type,
        )

    if outcome is not None:
        statement = statement.where(
            AuditLog.outcome == outcome,
        )

    statement = (
        statement
        .order_by(
            AuditLog.created_at.desc(),
        )
        .limit(limit)
    )

    return list(
        db.scalars(statement).all()
    )
