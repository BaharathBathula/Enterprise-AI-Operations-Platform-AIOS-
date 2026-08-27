from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    outcome: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )

    __table_args__ = (
        Index(
            "ix_audit_events_tenant_created_at",
            "tenant_id",
            "created_at",
        ),
        Index(
            "ix_audit_events_tenant_event_type",
            "tenant_id",
            "event_type",
        ),
    )
