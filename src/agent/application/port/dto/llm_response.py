from dataclasses import dataclass

from agent.domain.tool.tool import ToolCall


@dataclass
class ChatResponse:
    content: str


@dataclass
class ToolResponse:
    content: str
    tools: list[ToolCall]
