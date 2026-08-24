from app.tools.base import BaseTool


class ToolNotFoundError(Exception):
    pass


class DuplicateToolError(Exception):
    pass


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:
        if tool.name in self._tools:
            raise DuplicateToolError(
                f"Tool '{tool.name}' is already registered"
            )

        self._tools[tool.name] = tool

    def get(
        self,
        tool_name: str,
    ) -> BaseTool:
        tool = self._tools.get(tool_name)

        if tool is None:
            raise ToolNotFoundError(
                f"Tool '{tool_name}' is not registered"
            )

        return tool

    def list_tools(
        self,
    ) -> list[BaseTool]:
        return list(
            self._tools.values()
        )

    def contains(
        self,
        tool_name: str,
    ) -> bool:
        return tool_name in self._tools
