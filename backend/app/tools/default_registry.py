from app.tools.knowledge_search import (
    KnowledgeSearchTool,
)
from app.tools.registry import ToolRegistry


def create_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        KnowledgeSearchTool()
    )

    return registry
