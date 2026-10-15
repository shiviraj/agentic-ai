from agent.domain.vo.tool_result import ToolResult


class Tool:
    name: str
    description: str
    parameters_schema: dict[str, object]
    def execute(self, arguments: dict[str, object]) -> ToolResult:
        ...
