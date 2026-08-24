import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embeddings


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    page_number: int
    content: str
    similarity_score: float


def retrieve_relevant_chunks(
    db: Session,
    *,
    organization_id: uuid.UUID,
    question: str,
    limit: int = 5,
) -> list[RetrievedChunk]:
    embeddings = generate_embeddings([question])

    if not embeddings:
        return []

    query_embedding = embeddings[0]

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    statement = (
        select(
            DocumentChunk.id,
            DocumentChunk.document_id,
            Document.original_filename,
            DocumentChunk.page_number,
            DocumentChunk.content,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(
            DocumentChunk.organization_id == organization_id,
        )
        .order_by(distance)
        .limit(limit)
    )

    rows = db.execute(statement).all()

    results: list[RetrievedChunk] = []

    for row in rows:
        similarity_score = max(
            0.0,
            1.0 - float(row.distance),
        )

        results.append(
            RetrievedChunk(
                chunk_id=row.id,
                document_id=row.document_id,
                filename=row.original_filename,
                page_number=row.page_number,
                content=row.content,
                similarity_score=similarity_score,
            )
        )

    return results
