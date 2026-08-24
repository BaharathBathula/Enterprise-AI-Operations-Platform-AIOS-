import uuid

from pydantic import BaseModel, Field


class RAGQuestionRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=4000,
    )

    conversation_id: uuid.UUID | None = None

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class RAGSource(BaseModel):
    document_id: uuid.UUID
    filename: str
    page_number: int
    similarity_score: float


class RAGAnswerResponse(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    sources: list[RAGSource]
