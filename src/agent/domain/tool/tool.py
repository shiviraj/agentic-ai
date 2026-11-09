from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    """What a tool is: its name, what it does, and what input it accepts."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    """A request to run one tool with some arguments."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    """What came back from a tool. Errors are normal results, not exceptions."""

    content: str
    is_error: bool = False

    @classmethod
    def success(cls, content: str) -> "ToolResult":
        return cls(content=content)

    @classmethod
    def failure(cls, message: str) -> "ToolResult":
        return cls(content=message, is_error=True)
