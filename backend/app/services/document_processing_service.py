from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.document import (
    Document,
    DocumentStatus,
)
from app.models.document_chunk import DocumentChunk
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import (
    EmbeddingGenerationError,
    generate_embeddings,
)
from app.services.pdf_service import (
    EmptyPDFError,
    PDFExtractionError,
    extract_pdf_pages,
)


class DocumentProcessingError(Exception):
    pass


def process_document(
    db: Session,
    document: Document,
) -> Document:
    document.status = DocumentStatus.processing
    document.processing_error = None

    db.commit()
    db.refresh(document)

    try:
        pages = extract_pdf_pages(
            document.storage_path,
        )

        chunks = chunk_pages(pages)

        if not chunks:
            raise DocumentProcessingError(
                "Document produced no usable text chunks"
            )

        embeddings = generate_embeddings(
            [
                chunk.content
                for chunk in chunks
            ]
        )

        db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id
                == document.id
            )
        )

        for chunk, embedding in zip(
            chunks,
            embeddings,
            strict=True,
        ):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    organization_id=(
                        document.organization_id
                    ),
                    page_number=(
                        chunk.page_number
                    ),
                    chunk_index=(
                        chunk.chunk_index
                    ),
                    content=chunk.content,
                    embedding=embedding,
                )
            )

        document.page_count = max(
            page.page_number
            for page in pages
        )

        document.status = (
            DocumentStatus.ready
        )

        document.processing_error = None

        db.commit()
        db.refresh(document)

        return document

    except (
        PDFExtractionError,
        EmptyPDFError,
        EmbeddingGenerationError,
        DocumentProcessingError,
    ) as exc:
        db.rollback()

        document.status = (
            DocumentStatus.failed
        )

        document.processing_error = str(
            exc
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        raise DocumentProcessingError(
            str(exc)
        ) from exc

    except Exception as exc:
        db.rollback()

        document.status = (
            DocumentStatus.failed
        )

        document.processing_error = (
            "Unexpected document processing failure"
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        raise DocumentProcessingError(
            "Unexpected document processing failure"
        ) from exc
