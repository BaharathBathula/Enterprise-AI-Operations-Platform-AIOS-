"""add tool approvals

Revision ID: 20260824_0005
Revises: 20260824_0004
Create Date: 2026-08-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260824_0005"
down_revision: str | None = "20260824_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


tool_approval_status = postgresql.ENUM(
    "pending",
    "approved",
    "rejected",
    "executed",
    name="tool_approval_status",
)


def upgrade() -> None:
    tool_approval_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "tool_approvals",
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
            "requested_by_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "tool_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "arguments",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "status",
            tool_approval_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "reviewed_by_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "review_note",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_tool_approvals_organization_id",
        "tool_approvals",
        ["organization_id"],
    )

    op.create_index(
        "ix_tool_approvals_requested_by_user_id",
        "tool_approvals",
        ["requested_by_user_id"],
    )

    op.create_index(
        "ix_tool_approvals_conversation_id",
        "tool_approvals",
        ["conversation_id"],
    )

    op.create_index(
        "ix_tool_approvals_tool_name",
        "tool_approvals",
        ["tool_name"],
    )

    op.create_index(
        "ix_tool_approvals_status",
        "tool_approvals",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tool_approvals_status",
        table_name="tool_approvals",
    )

    op.drop_index(
        "ix_tool_approvals_tool_name",
        table_name="tool_approvals",
    )

    op.drop_index(
        "ix_tool_approvals_conversation_id",
        table_name="tool_approvals",
    )

    op.drop_index(
        "ix_tool_approvals_requested_by_user_id",
        table_name="tool_approvals",
    )

    op.drop_index(
        "ix_tool_approvals_organization_id",
        table_name="tool_approvals",
    )

    op.drop_table(
        "tool_approvals"
    )

    tool_approval_status.drop(
        op.get_bind(),
        checkfirst=True,
    )
