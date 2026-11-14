from agent.domain.tool.errors import ToolNotFoundError
from agent.domain.tool.tool import ToolDefinition
from agent.domain.tool.tool_provider import ToolProvider


class ToolRegistry:
    """The catalog of tools the agent can use, and which provider runs each one."""

    def __init__(self) -> None:
        self._definitions: dict[str, ToolDefinition] = {}
        self._providers: dict[str, ToolProvider] = {}

    async def register_provider(self, provider: ToolProvider) -> None:
        definitions = await provider.list_tools()
        self._providers[provider.server_name] = provider
        for definition in definitions:
            self._definitions[definition.name] = definition

    def definitions(self) -> list[ToolDefinition]:
        return list(self._definitions.values())

    def provider_for(self, provider: str) -> ToolProvider:
        provider = self._providers.get(provider)
        if provider is None:
            raise ToolNotFoundError(f"Unknown tool: {provider}")
        return provider
