"""add documents

Revision ID: 20260824_0002
Revises: 20260718_0001
Create Date: 2026-08-24
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260824_0002"
down_revision: str | None = "20260718_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


document_status = postgresql.ENUM(
    "uploaded",
    "processing",
    "ready",
    "failed",
    name="document_status",
)


def upgrade() -> None:
    op.create_table(
        "documents",
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
            "uploaded_by_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "filename",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "original_filename",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "file_size",
            sa.BigInteger(),
            nullable=False,
        ),
        sa.Column(
            "storage_path",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "status",
            document_status,
            nullable=False,
        ),
        sa.Column(
            "processing_error",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "page_count",
            sa.Integer(),
            nullable=True,
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
            ["uploaded_by_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_documents_organization_id",
        "documents",
        ["organization_id"],
    )

    op.create_index(
        "ix_documents_uploaded_by_user_id",
        "documents",
        ["uploaded_by_user_id"],
    )

    op.create_index(
        "ix_documents_status",
        "documents",
        ["status"],
    )

    op.create_index(
        "ix_documents_created_at",
        "documents",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_documents_created_at",
        table_name="documents",
    )

    op.drop_index(
        "ix_documents_status",
        table_name="documents",
    )

    op.drop_index(
        "ix_documents_uploaded_by_user_id",
        table_name="documents",
    )

    op.drop_index(
        "ix_documents_organization_id",
        table_name="documents",
    )

    op.drop_table("documents")

    document_status.drop(
        op.get_bind(),
        checkfirst=True,
    )