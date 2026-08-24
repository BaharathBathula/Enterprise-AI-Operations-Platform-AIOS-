import pytest
from pydantic import ValidationError

from app.schemas.rag import RAGQuestionRequest


def test_rag_question_request_defaults_top_k():
    request = RAGQuestionRequest(
        question="What does this document say?"
    )

    assert request.top_k == 5


def test_rag_question_rejects_too_short_question():
    with pytest.raises(ValidationError):
        RAGQuestionRequest(
            question="Hi"
        )


def test_rag_question_rejects_top_k_above_limit():
    with pytest.raises(ValidationError):
        RAGQuestionRequest(
            question="What does this document say?",
            top_k=11,
        )


def test_rag_question_rejects_top_k_below_one():
    with pytest.raises(ValidationError):
        RAGQuestionRequest(
            question="What does this document say?",
            top_k=0,
        )
