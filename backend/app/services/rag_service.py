from openai import OpenAI

from app.core.config import settings
from app.models.message import Message
from app.services.retrieval_service import RetrievedChunk


class RAGGenerationError(Exception):
    pass


def build_context(
    chunks: list[RetrievedChunk],
) -> str:
    sections: list[str] = []

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):
        sections.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    f"Document: {chunk.filename}",
                    f"Page: {chunk.page_number}",
                    chunk.content,
                ]
            )
        )

    return "\n\n".join(sections)


def build_conversation_history(
    messages: list[Message],
    limit: int = 10,
) -> str:
    recent_messages = messages[-limit:]

    history: list[str] = []

    for message in recent_messages:
        history.append(
            f"{message.role.value.upper()}: "
            f"{message.content}"
        )

    return "\n".join(history)


def generate_grounded_answer(
    *,
    question: str,
    chunks: list[RetrievedChunk],
    messages: list[Message] | None = None,
) -> str:
    if not chunks:
        return (
            "I could not find enough relevant information "
            "in the organization's documents to answer "
            "this question."
        )

    if not settings.OPENAI_API_KEY:
        raise RAGGenerationError(
            "OPENAI_API_KEY is not configured"
        )

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )

    document_context = build_context(chunks)

    conversation_history = build_conversation_history(
        messages or [],
    )

    system_prompt = """
You are an enterprise document assistant.

Answer the user's question using only the supplied document context
as the factual source of truth.

Conversation history may be used only to understand references,
follow-up questions, and conversational intent.

Rules:
1. Do not use outside knowledge.
2. Do not treat previous assistant messages as factual evidence.
3. Use the document context as the factual authority.
4. If the documents do not contain enough information, say so.
5. Do not invent facts.
6. Refer to supporting document sources as [Source 1],
   [Source 2], etc.
7. Keep answers concise and precise.
""".strip()

    user_prompt = f"""
Conversation History:
{conversation_history or "No previous conversation."}

Current Question:
{question}

Document Context:
{document_context}
""".strip()

    try:
        response = client.responses.create(
            model=settings.CHAT_MODEL,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )
    except Exception as exc:
        raise RAGGenerationError(
            "Failed to generate grounded answer"
        ) from exc

    answer = response.output_text.strip()

    if not answer:
        raise RAGGenerationError(
            "AI provider returned an empty answer"
        )

    return answer
