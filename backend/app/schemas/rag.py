import uuid

from pydantic import BaseModel, Field


class RAGQuestionRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=4000,
    )

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
    answer: str
    sources: list[RAGSource]
