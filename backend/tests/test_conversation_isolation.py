import uuid
from unittest.mock import MagicMock

from app.services.conversation_service import (
    get_conversation,
)


def test_conversation_query_is_user_and_organization_scoped():
    db = MagicMock()

    db.scalar.return_value = None

    organization_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    user_id = uuid.uuid4()

    result = get_conversation(
        db=db,
        organization_id=organization_id,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    assert result is None

    db.scalar.assert_called_once()

    statement = db.scalar.call_args.args[0]

    compiled = str(
        statement.compile(
            compile_kwargs={
                "literal_binds": False,
            }
        )
    )

    assert "organization_id" in compiled
    assert "user_id" in compiled
