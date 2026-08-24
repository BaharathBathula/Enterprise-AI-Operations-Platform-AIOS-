from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class ToolExecutionContext:
    organization_id: uuid.UUID
    user_id: uuid.UUID
    conversation_id: uuid.UUID | None = None


@dataclass
class ToolResult:
    success: bool
    data: dict[str, Any] = field(
        default_factory=dict,
    )
    message: str | None = None
    error: str | None = None


class BaseTool(ABC):
    name: str
    description: str

    requires_approval: bool = False

    @abstractmethod
    def execute(
        self,
        *,
        context: ToolExecutionContext,
        arguments: dict[str, Any],
    ) -> ToolResult:
        raise NotImplementedError
