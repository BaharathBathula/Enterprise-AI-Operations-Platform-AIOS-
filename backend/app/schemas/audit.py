import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None
    user_id: uuid.UUID | None

    event_type: str
    action: str
    outcome: str

    resource_type: str
    resource_id: str | None

    details: dict[str, Any] | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
