import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import (
    IncidentSeverity,
    IncidentStatus,
)


class IncidentCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=255,
    )

    description: str = Field(
        min_length=3,
    )

    severity: IncidentSeverity = (
        IncidentSeverity.medium
    )

    source: str = Field(
        default="aios",
        min_length=1,
        max_length=100,
    )


class IncidentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        min_length=3,
    )

    severity: IncidentSeverity | None = None

    status: IncidentStatus | None = None


class IncidentResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_user_id: uuid.UUID

    title: str
    description: str

    severity: IncidentSeverity
    status: IncidentStatus

    source: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
