from dataclasses import dataclass
from enum import Enum

from agent.domain.tool.tool import ToolCall


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class Message:
    role: Role
    content: str
    tool_name: str | None = None
    tool_calls: list[ToolCall] | None = None
