import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    uploaded_by_user_id: uuid.UUID | None

    filename: str
    original_filename: str
    content_type: str
    file_size: int

    status: DocumentStatus
    processing_error: str | None
    page_count: int | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
