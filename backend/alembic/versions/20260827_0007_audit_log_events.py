"""strengthen audit logs with event type and outcome

Revision ID: 20260827_0007
Revises: 20260824_0006
Create Date: 2026-08-27
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260827_0007"
down_revision: str | None = "20260824_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column(
            "event_type",
            sa.String(length=120),
            nullable=False,
            server_default="general",
        ),
    )

    op.add_column(
        "audit_logs",
        sa.Column(
            "outcome",
            sa.String(length=32),
            nullable=False,
            server_default="success",
        ),
    )

    op.create_index(
        "ix_audit_logs_event_type",
        "audit_logs",
        ["event_type"],
    )

    op.create_index(
        "ix_audit_logs_outcome",
        "audit_logs",
        ["outcome"],
    )

    op.create_index(
        "ix_audit_logs_org_created_at",
        "audit_logs",
        ["organization_id", "created_at"],
    )

    op.create_index(
        "ix_audit_logs_org_event_type",
        "audit_logs",
        ["organization_id", "event_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_audit_logs_org_event_type",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_org_created_at",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_outcome",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_event_type",
        table_name="audit_logs",
    )

    op.drop_column(
        "audit_logs",
        "outcome",
    )

    op.drop_column(
        "audit_logs",
        "event_type",
    )
