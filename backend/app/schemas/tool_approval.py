import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.tool_approval import ToolApprovalStatus


class ToolApprovalResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    requested_by_user_id: uuid.UUID
    conversation_id: uuid.UUID | None

    tool_name: str
    arguments: dict[str, Any]
    status: ToolApprovalStatus

    reviewed_by_user_id: uuid.UUID | None
    review_note: str | None

    created_at: datetime
    reviewed_at: datetime | None
    executed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ToolApprovalReviewRequest(BaseModel):
    review_note: str | None = Field(
        default=None,
        max_length=1000,
    )
