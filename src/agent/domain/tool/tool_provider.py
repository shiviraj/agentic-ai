from typing import Protocol

from agent.domain.tool.tool import ToolCall, ToolDefinition, ToolResult


class ToolProvider(Protocol):
    """Port: anything that can list its tools and run them.

    The domain only knows this shape. An MCP client is one implementation;
    a plain in-memory class (handy for a quick fake) is another.
    """

    async def list_tools(self) -> list[ToolDefinition]: ...

    async def call_tool(self, call: ToolCall) -> ToolResult: ...
