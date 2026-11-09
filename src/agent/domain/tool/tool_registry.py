from agent.domain.tool.errors import DuplicateToolError, ToolNotFoundError
from agent.domain.tool.tool import ToolDefinition
from agent.domain.tool.tool_provider import ToolProvider


class ToolRegistry:
    """The catalog of tools the agent can use, and which provider runs each one."""

    def __init__(self) -> None:
        self._definitions: dict[str, ToolDefinition] = {}
        self._providers: dict[str, ToolProvider] = {}

    async def register_provider(self, provider: ToolProvider) -> None:
        definitions = await provider.list_tools()
        self._ensure_names_are_free(definitions)
        for definition in definitions:
            self._definitions[definition.name] = definition
            self._providers[definition.name] = provider

    def definitions(self) -> list[ToolDefinition]:
        return list(self._definitions.values())

    def provider_for(self, tool_name: str) -> ToolProvider:
        provider = self._providers.get(tool_name)
        if provider is None:
            raise ToolNotFoundError(f"Unknown tool: {tool_name}")
        return provider

    def _ensure_names_are_free(self, definitions: list[ToolDefinition]) -> None:
        # Check everything first, so a clash leaves the registry unchanged.
        seen: set[str] = set()
        for definition in definitions:
            if definition.name in self._definitions or definition.name in seen:
                raise DuplicateToolError(f"Tool name already registered: {definition.name}")
            seen.add(definition.name)
