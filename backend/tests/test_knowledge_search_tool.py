import uuid
from unittest.mock import (
    MagicMock,
    patch,
)

from app.services.retrieval_service import (
    RetrievedChunk,
)
from app.tools.base import ToolExecutionContext
from app.tools.knowledge_search import (
    KnowledgeSearchTool,
)


def create_context():
    return ToolExecutionContext(
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        db=MagicMock(),
    )


def test_knowledge_search_requires_database():
    tool = KnowledgeSearchTool()

    context = ToolExecutionContext(
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
    )

    result = tool.execute(
        context=context,
        arguments={
            "query": "What is the cancellation period?"
        },
    )

    assert result.success is False
    assert result.error == (
        "Database session is required"
    )


def test_knowledge_search_requires_query():
    tool = KnowledgeSearchTool()

    result = tool.execute(
        context=create_context(),
        arguments={},
    )

    assert result.success is False
    assert result.error == (
        "A search query is required"
    )


def test_knowledge_search_validates_limit():
    tool = KnowledgeSearchTool()

    result = tool.execute(
        context=create_context(),
        arguments={
            "query": "insurance policy",
            "limit": 20,
        },
    )

    assert result.success is False
    assert result.error == (
        "Search limit must be between 1 and 10"
    )


@patch(
    "app.tools.knowledge_search.retrieve_relevant_chunks"
)
def test_knowledge_search_returns_results(
    mock_retrieve,
):
    organization_id = uuid.uuid4()

    context = ToolExecutionContext(
        organization_id=organization_id,
        user_id=uuid.uuid4(),
        db=MagicMock(),
    )

    document_id = uuid.uuid4()
    chunk_id = uuid.uuid4()

    mock_retrieve.return_value = [
        RetrievedChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            filename="policy.pdf",
            page_number=7,
            content=(
                "Cancellation requires "
                "thirty days notice."
            ),
            similarity_score=0.92,
        )
    ]

    tool = KnowledgeSearchTool()

    result = tool.execute(
        context=context,
        arguments={
            "query": "What is the cancellation period?",
            "limit": 5,
        },
    )

    assert result.success is True
    assert result.data["result_count"] == 1

    assert (
        result.data["results"][0]["filename"]
        == "policy.pdf"
    )

    mock_retrieve.assert_called_once_with(
        db=context.db,
        organization_id=organization_id,
        question="What is the cancellation period?",
        limit=5,
    )


def test_default_registry_contains_knowledge_search():
    from app.tools.default_registry import (
        create_default_tool_registry,
    )

    registry = create_default_tool_registry()

    assert registry.contains(
        "knowledge_search"
    )
