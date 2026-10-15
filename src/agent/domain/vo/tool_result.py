from dataclasses import dataclass


@dataclass
class ToolResult:
    status: bool
    content: str
