import uuid
from unittest.mock import MagicMock, patch

from app.services.retrieval_service import (
    retrieve_relevant_chunks,
)


@patch(
    "app.services.retrieval_service.generate_embeddings"
)
def test_retrieval_uses_organization_scope(
    mock_generate_embeddings,
):
    mock_generate_embeddings.return_value = [
        [0.1] * 1536
    ]

    db = MagicMock()

    result = MagicMock()
    result.all.return_value = []

    db.execute.return_value = result

    organization_id = uuid.uuid4()

    chunks = retrieve_relevant_chunks(
        db=db,
        organization_id=organization_id,
        question="What is the cancellation period?",
        limit=5,
    )

    assert chunks == []

    db.execute.assert_called_once()

    statement = db.execute.call_args.args[0]

    compiled = str(
        statement.compile(
            compile_kwargs={
                "literal_binds": False,
            }
        )
    )

    assert "organization_id" in compiled
