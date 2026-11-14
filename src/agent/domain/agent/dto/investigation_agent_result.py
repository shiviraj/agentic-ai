from dataclasses import dataclass

from agent.domain.tool.tool import ToolCall


@dataclass(frozen=True)
class InvestigationAgentResult:
    content: str
    tools: list[ToolCall]
    finished: bool
