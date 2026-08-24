from types import SimpleNamespace

from app.models.message import MessageRole
from app.services.rag_service import (
    build_conversation_history,
)


def test_build_conversation_history():
    messages = [
        SimpleNamespace(
            role=MessageRole.user,
            content="What is the deductible?",
        ),
        SimpleNamespace(
            role=MessageRole.assistant,
            content="The deductible is $1,000.",
        ),
    ]

    history = build_conversation_history(messages)

    assert "USER: What is the deductible?" in history

    assert (
        "ASSISTANT: The deductible is $1,000."
        in history
    )


def test_conversation_history_respects_limit():
    messages = [
        SimpleNamespace(
            role=MessageRole.user,
            content=f"Question {index}",
        )
        for index in range(20)
    ]

    history = build_conversation_history(
        messages,
        limit=5,
    )

    assert "Question 15" in history
    assert "Question 19" in history
    assert "Question 14" not in history
