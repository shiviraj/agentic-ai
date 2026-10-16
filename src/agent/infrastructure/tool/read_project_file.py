from pathlib import Path
from typing import cast

from agent.domain.vo.tool_result import ToolResult
from agent.infrastructure.tool.tool import Tool
from agent.infrastructure.tool.util import MAX_FILE_SIZE_BYTES


class ReadProjectFile(Tool):
    """Read a UTF-8 text file from the project workspace."""
    name: str = "read_file"
    description: str = "Read a UTF-8 text file from the project workspace. Provide a project-relative file path."
    parameters_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "filename": {
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
        filename: str = cast(str, arguments["filename"])
        project_root = self.workspace_root.resolve()
        requested_path = project_root / filename

        # Prevent reading files outside the project workspace.
        if not requested_path.is_relative_to(project_root):
            return ToolResult(success=False, error="File path must stay inside the project.")

        if not requested_path.is_file():
            return ToolResult(success=False, error=f"File not found: {filename}")

        size_bytes = requested_path.stat().st_size

        if size_bytes > MAX_FILE_SIZE_BYTES:
            return ToolResult(
                success=False,
                error=f"File is too large to read. Maximum size is {MAX_FILE_SIZE_BYTES} bytes."
            )

        try:
            content = requested_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ToolResult(success=False, error="File is not valid UTF-8 text.")

        return ToolResult(
            success=True,
            data={
                "filename": requested_path.relative_to(project_root).as_posix(),
                "size_bytes": size_bytes,
                "content": content,
            }
        )
