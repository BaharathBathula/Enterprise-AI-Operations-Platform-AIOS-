"""add conversations and messages

Revision ID: 20260824_0004
Revises: 20260824_0003
Create Date: 2026-08-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260824_0004"
down_revision: str | None = "20260824_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


message_role = postgresql.ENUM(
    "user",
    "assistant",
    name="message_role",
)


def upgrade() -> None:
    message_role.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "conversations",
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
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
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
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_conversations_organization_id",
        "conversations",
        ["organization_id"],
    )

    op.create_index(
        "ix_conversations_user_id",
        "conversations",
        ["user_id"],
    )

    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "role",
            message_role,
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_messages_conversation_id",
        "messages",
        ["conversation_id"],
    )

    op.create_index(
        "ix_messages_organization_id",
        "messages",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_messages_organization_id",
        table_name="messages",
    )

    op.drop_index(
        "ix_messages_conversation_id",
        table_name="messages",
    )

    op.drop_table("messages")

    op.drop_index(
        "ix_conversations_user_id",
        table_name="conversations",
    )

    op.drop_index(
        "ix_conversations_organization_id",
        table_name="conversations",
    )

    op.drop_table("conversations")

    message_role.drop(
        op.get_bind(),
        checkfirst=True,
    )
