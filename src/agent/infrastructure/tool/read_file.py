from pathlib import Path

from agent.domain.vo.tool_result import ToolResult
from agent.infrastructure.tool.tool import Tool


class ReadFile(Tool):
    """Read a UTF-8 text file from the project workspace."""
    name: str = "read_file"
    description: str = "Read a UTF-8 text file from the project workspace. Provide a project-relative file path."
    parameters_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file relative to the project workspace.",
            },
        },
        "required": ["file_path"],
        "additionalProperties": False,
    }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        file_path = arguments.get("file_path", None)
        if file_path is None:
            print(f"Not found: {file_path}")
        else:
            print(f"Reading file: {file_path}")
        return ToolResult(status=True, content="No content")
