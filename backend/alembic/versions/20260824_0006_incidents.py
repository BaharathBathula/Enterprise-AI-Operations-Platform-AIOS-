"""add incidents

Revision ID: 20260824_0006
Revises: 20260824_0005
Create Date: 2026-08-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260824_0006"
down_revision: str | None = "20260824_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


incident_severity = postgresql.ENUM(
    "low",
    "medium",
    "high",
    "critical",
    name="incident_severity",
)

incident_status = postgresql.ENUM(
    "open",
    "investigating",
    "resolved",
    name="incident_status",
)


def upgrade() -> None:
    incident_severity.create(
        op.get_bind(),
        checkfirst=True,
    )

    incident_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "incidents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "severity",
            incident_severity,
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "status",
            incident_status,
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "source",
            sa.String(length=100),
            nullable=False,
            server_default="aios",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_incidents_organization_id",
        "incidents",
        ["organization_id"],
    )

    op.create_index(
        "ix_incidents_created_by_user_id",
        "incidents",
        ["created_by_user_id"],
    )

    op.create_index(
        "ix_incidents_severity",
        "incidents",
        ["severity"],
    )

    op.create_index(
        "ix_incidents_status",
        "incidents",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_incidents_status",
        table_name="incidents",
    )

    op.drop_index(
        "ix_incidents_severity",
        table_name="incidents",
    )

    op.drop_index(
        "ix_incidents_created_by_user_id",
        table_name="incidents",
    )

    op.drop_index(
        "ix_incidents_organization_id",
        table_name="incidents",
    )

    op.drop_table("incidents")

    incident_status.drop(
        op.get_bind(),
        checkfirst=True,
    )

    incident_severity.drop(
        op.get_bind(),
        checkfirst=True,
    )
