from dataclasses import dataclass

from app.core.config import settings
from app.services.pdf_service import ExtractedPage


@dataclass
class TextChunk:
    page_number: int
    chunk_index: int
    content: str


def split_text(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    cleaned_text = " ".join(
        text.split()
    )

    if not cleaned_text:
        return []

    chunks: list[str] = []

    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = min(
            start + chunk_size,
            text_length,
        )

        chunk = cleaned_text[
            start:end
        ].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def chunk_pages(
    pages: list[ExtractedPage],
) -> list[TextChunk]:
    chunks: list[TextChunk] = []

    global_chunk_index = 0

    for page in pages:
        page_chunks = split_text(
            text=page.text,
            chunk_size=settings.DOCUMENT_CHUNK_SIZE,
            overlap=settings.DOCUMENT_CHUNK_OVERLAP,
        )

        for content in page_chunks:
            chunks.append(
                TextChunk(
                    page_number=page.page_number,
                    chunk_index=global_chunk_index,
                    content=content,
                )
            )

            global_chunk_index += 1

    return chunks
