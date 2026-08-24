from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=10000,
    )


class AgentResponse(BaseModel):
    success: bool
    message: str | None = None
    error: str | None = None
    data: dict[str, Any]
