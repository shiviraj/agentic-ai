from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    """What a tool is: its name, what it does, and what input it accepts."""

    provider: str
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    """A request to run one tool with some arguments."""

    provider: str
    name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    content: dict[str, object]
    error: Exception | None = None
    is_error: bool = False

    @classmethod
    def success(cls, content: dict[str, object]) -> "ToolResult":
        return cls(content=content)

    @classmethod
    def failure(cls, error: Exception) -> "ToolResult":
        return cls(content={"message": "There is an error in tool result"}, is_error=True, error=error)
