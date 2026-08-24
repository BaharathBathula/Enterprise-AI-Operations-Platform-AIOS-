from openai import OpenAI

from app.core.config import settings
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


def generate_grounded_answer(
    *,
    question: str,
    chunks: list[RetrievedChunk],
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

    context = build_context(chunks)

    system_prompt = """
You are an enterprise document assistant.

Answer the user's question using only the supplied context.

Rules:
1. Do not use outside knowledge.
2. If the context does not contain enough information, say so.
3. Do not invent facts.
4. Keep the answer concise and precise.
5. Refer to supporting sources as [Source 1], [Source 2], etc.
""".strip()

    user_prompt = f"""
Question:
{question}

Context:
{context}
""".strip()

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
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
