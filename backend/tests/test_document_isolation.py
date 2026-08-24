import uuid
from unittest.mock import MagicMock

from app.services.document_service import (
    get_document,
)


def test_document_query_is_organization_scoped():
    db = MagicMock()

    db.scalar.return_value = None

    organization_id = uuid.uuid4()
    document_id = uuid.uuid4()

    result = get_document(
        db=db,
        organization_id=organization_id,
        document_id=document_id,
    )

    assert result is None

    statement = db.scalar.call_args.args[0]

    compiled = str(
        statement.compile(
            compile_kwargs={
                "literal_binds": False,
            }
        )
    )

    assert "organization_id" in compiled
