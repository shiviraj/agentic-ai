from pathlib import Path

from agent.infrastructure.tool.read_file import ReadFile
from agent.infrastructure.tool_registry import ToolRegistry


def create_tool_registry(workspace_root: Path) -> ToolRegistry:
    return ToolRegistry(
        tools=[
            ReadFile(workspace_root)
        ]
    )
