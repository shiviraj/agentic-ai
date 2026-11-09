from agent.domain.tool.errors import ToolNotFoundError, ToolProviderError
from agent.domain.tool.tool import ToolCall, ToolResult
from agent.domain.tool.tool_registry import ToolRegistry


class ToolExecutor:
    """Use case: run one tool call and always hand back a ToolResult.

    Failures become error results instead of exceptions. The LLM can read
    "Unknown tool: x" and fix its next call; a crash would stop the agent.
    """

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def execute(self, call: ToolCall) -> ToolResult:
        try:
            provider = self._registry.provider_for(call.name)
            return await provider.call_tool(call)
        except ToolNotFoundError as error:
            return ToolResult.failure(str(error))
        except ToolProviderError as error:
            return ToolResult.failure(f"Tool '{call.name}' failed: {error}")
