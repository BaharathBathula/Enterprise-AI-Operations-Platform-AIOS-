import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.conversation_service import (
    get_conversation,
)
from app.services.document_service import (
    get_document,
)


def _compiled_sql(statement) -> str:
    return str(
        statement.compile(
            compile_kwargs={
                "literal_binds": False,
            }
        )
    ).lower()


def test_document_lookup_scopes_by_document_and_organization():
    db = MagicMock()
    db.scalar.return_value = None

    organization_a = uuid.uuid4()
    document_from_org_b = uuid.uuid4()

    result = get_document(
        db=db,
        organization_id=organization_a,
        document_id=document_from_org_b,
    )

    assert result is None
    db.scalar.assert_called_once()

    statement = db.scalar.call_args.args[0]
    compiled = _compiled_sql(statement)

    assert "documents.id" in compiled
    assert "organization_id" in compiled


def test_conversation_lookup_scopes_by_conversation_user_and_organization():
    db = MagicMock()
    db.scalar.return_value = None

    organization_a = uuid.uuid4()
    user_a = uuid.uuid4()
    conversation_from_org_b = uuid.uuid4()

    result = get_conversation(
        db=db,
        organization_id=organization_a,
        conversation_id=conversation_from_org_b,
        user_id=user_a,
    )

    assert result is None
    db.scalar.assert_called_once()

    statement = db.scalar.call_args.args[0]
    compiled = _compiled_sql(statement)

    assert "conversations.id" in compiled
    assert "organization_id" in compiled
    assert "user_id" in compiled


def test_document_service_does_not_return_cross_tenant_document():
    db = MagicMock()

    organization_a = uuid.uuid4()
    organization_b = uuid.uuid4()
    document_id = uuid.uuid4()

    document_b = SimpleNamespace(
        id=document_id,
        organization_id=organization_b,
    )

    # Simulate the database respecting the organization-scoped query:
    # Org A must not receive Org B's row.
    db.scalar.return_value = None

    result = get_document(
        db=db,
        organization_id=organization_a,
        document_id=document_b.id,
    )

    assert result is None


def test_conversation_service_does_not_return_another_users_conversation():
    db = MagicMock()

    organization_id = uuid.uuid4()
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    conversation_id = uuid.uuid4()

    conversation_b = SimpleNamespace(
        id=conversation_id,
        organization_id=organization_id,
        user_id=user_b,
    )

    # The scoped lookup for user A must not expose user B's thread.
    db.scalar.return_value = None

    result = get_conversation(
        db=db,
        organization_id=organization_id,
        conversation_id=conversation_b.id,
        user_id=user_a,
    )

    assert result is None
