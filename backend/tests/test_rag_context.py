import uuid

from app.services.rag_service import build_context
from app.services.retrieval_service import RetrievedChunk


def test_build_context_contains_document_and_page_metadata():
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            filename="policy.pdf",
            page_number=7,
            content="Cancellation requires thirty days notice.",
            similarity_score=0.91,
        )
    ]

    context = build_context(chunks)

    assert "[Source 1]" in context
    assert "Document: policy.pdf" in context
    assert "Page: 7" in context
    assert "Cancellation requires thirty days notice." in context


def test_build_context_handles_multiple_sources():
    chunks = [
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            filename="policy.pdf",
            page_number=2,
            content="Coverage begins on January 1.",
            similarity_score=0.95,
        ),
        RetrievedChunk(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            filename="endorsement.pdf",
            page_number=4,
            content="The endorsement modifies the deductible.",
            similarity_score=0.89,
        ),
    ]

    context = build_context(chunks)

    assert "[Source 1]" in context
    assert "[Source 2]" in context
    assert "policy.pdf" in context
    assert "endorsement.pdf" in context
