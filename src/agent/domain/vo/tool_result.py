from dataclasses import dataclass


@dataclass
class ToolResult:
    success: bool
    data: dict[str, object] | None = None
    error: str | None = None
