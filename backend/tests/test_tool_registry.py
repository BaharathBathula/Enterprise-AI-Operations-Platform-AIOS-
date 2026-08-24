import uuid

import pytest

from app.tools.base import (
    BaseTool,
    ToolExecutionContext,
    ToolResult,
)
from app.tools.registry import (
    DuplicateToolError,
    ToolNotFoundError,
    ToolRegistry,
)


class ExampleTool(BaseTool):
    name = "example"
    description = "Example tool for tests"

    def execute(
        self,
        *,
        context: ToolExecutionContext,
        arguments: dict,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "organization_id": str(
                    context.organization_id
                ),
                "arguments": arguments,
            },
        )


def test_register_and_get_tool():
    registry = ToolRegistry()

    tool = ExampleTool()

    registry.register(tool)

    assert registry.get("example") is tool


def test_duplicate_tool_registration_fails():
    registry = ToolRegistry()

    registry.register(
        ExampleTool()
    )

    with pytest.raises(
        DuplicateToolError,
    ):
        registry.register(
            ExampleTool()
        )


def test_unknown_tool_fails():
    registry = ToolRegistry()

    with pytest.raises(
        ToolNotFoundError,
    ):
        registry.get(
            "missing-tool"
        )


def test_registered_tool_executes():
    registry = ToolRegistry()

    registry.register(
        ExampleTool()
    )

    tool = registry.get(
        "example"
    )

    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()

    context = ToolExecutionContext(
        organization_id=organization_id,
        user_id=user_id,
    )

    result = tool.execute(
        context=context,
        arguments={
            "query": "hello",
        },
    )

    assert result.success is True

    assert (
        result.data["organization_id"]
        == str(organization_id)
    )

    assert result.data["arguments"] == {
        "query": "hello",
    }


def test_registry_lists_tools():
    registry = ToolRegistry()

    registry.register(
        ExampleTool()
    )

    tools = registry.list_tools()

    assert len(tools) == 1
    assert tools[0].name == "example"
