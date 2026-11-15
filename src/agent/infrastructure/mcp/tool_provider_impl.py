from fastmcp import Client

from agent.domain.tool.errors import ToolProviderError
from agent.domain.tool.tool import ToolCall, ToolDefinition, ToolResult
from agent.domain.tool.tool_provider import ToolProvider


class ToolProviderImpl(ToolProvider):
    def __init__(self, client: Client, server_name: str) -> None:
        self._client = client
        self._server_name = server_name

    @property
    def server_name(self) -> str:
        return self._server_name

    async def list_tools(self) -> list[ToolDefinition]:
        try:
            tools = await self._client.list_tools()
        except Exception as error:
            raise ToolProviderError(f"Could not list tools: {error}") from error
        return [
            ToolDefinition(
                provider=self._server_name,
                name=tool.name,
                description=tool.description or "",
                input_schema=tool.input_schema,
            )
            for tool in tools
        ]

    async def call_tool(self, call: ToolCall) -> ToolResult:
        try:
            result = await self._client.call_tool(call.name, dict(call.arguments), raise_on_error=False)
        except Exception as error:  # connection lost, server crashed, ...
            raise ToolProviderError(f"Call to '{call.name}' failed: {error}") from error

        texts = [text for block in result.content if (text := getattr(block, "text", None))]
        return ToolResult(content="\n".join(texts), is_error=result.is_error)
