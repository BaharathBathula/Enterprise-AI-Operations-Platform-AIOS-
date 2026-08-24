import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import (
    Document,
    DocumentStatus,
)


def create_document_record(
    db: Session,
    *,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    original_filename: str,
    stored_filename: str,
    content_type: str,
    file_size: int,
    storage_path: str,
) -> Document:
    document = Document(
        organization_id=organization_id,
        uploaded_by_user_id=user_id,
        filename=stored_filename,
        original_filename=original_filename,
        content_type=content_type,
        file_size=file_size,
        storage_path=storage_path,
        status=DocumentStatus.uploaded,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def list_documents(
    db: Session,
    organization_id: uuid.UUID,
) -> list[Document]:
    statement = (
        select(Document)
        .where(
            Document.organization_id
            == organization_id,
        )
        .order_by(
            Document.created_at.desc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_document(
    db: Session,
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
) -> Document | None:
    statement = select(Document).where(
        Document.id == document_id,
        Document.organization_id
        == organization_id,
    )

    return db.scalar(statement)


def delete_document(
    db: Session,
    document: Document,
) -> None:
    file_path = Path(
        document.storage_path
    )

    if file_path.exists():
        file_path.unlink()

    db.delete(document)
    db.commit()
