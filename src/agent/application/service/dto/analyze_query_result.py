from dataclasses import dataclass

from agent.domain.tool.tool import ToolCall


@dataclass
class AnalyzeQueryResult:
    content: str
    tools: list[ToolCall]
    finished: bool
