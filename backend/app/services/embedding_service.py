from openai import OpenAI

from app.core.config import settings


class EmbeddingGenerationError(Exception):
    pass


def get_openai_client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise EmbeddingGenerationError(
            "OPENAI_API_KEY is not configured"
        )

    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )


def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    if not texts:
        return []

    client = get_openai_client()

    try:
        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )
    except Exception as exc:
        raise EmbeddingGenerationError(
            "Failed to generate document embeddings"
        ) from exc

    embeddings = [
        item.embedding
        for item in response.data
    ]

    if len(embeddings) != len(texts):
        raise EmbeddingGenerationError(
            "Embedding response count mismatch"
        )

    return embeddings
