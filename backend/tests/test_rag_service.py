from app.services.rag_service import (
    generate_grounded_answer,
)


def test_rag_returns_safe_answer_when_no_chunks_exist():
    answer = generate_grounded_answer(
        question="What is the deductible?",
        chunks=[],
    )

    assert (
        "could not find enough relevant information"
        in answer.lower()
    )
