from agent.application.tool.tool import Tool


class ToolRegistry:
    def __init__(self, tools: list[Tool], discovery_tools: list[Tool]) -> None:
        self._tools: dict[str, Tool] = {}
        for tool in tools:
            if tool.name in self._tools:
                raise ValueError(f"Duplicate tool name: {tool.name}")
            self._tools[tool.name] = tool
        self._tools_definition: list[dict[str, object]] = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema,
                },
            }
            for tool in self._tools.values()
        ]
        self._discovery_tools_definition: list[dict[str, object]] = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters_schema,
                },
            }
            for tool in discovery_tools
        ]

    @property
    def tools_definition(self) -> list[dict[str, object]]:
        return self._tools_definition

    @property
    def discovery_tools_definition(self) -> list[dict[str, object]]:
        return self._discovery_tools_definition

    def get_tool(self, tool_name: str) -> Tool:
        return self._tools[tool_name]
