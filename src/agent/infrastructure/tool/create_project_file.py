from pathlib import Path
from typing import cast

from agent.domain.vo.tool_result import ToolResult
from agent.infrastructure.tool.tool import Tool
from agent.infrastructure.tool.util import MAX_FILE_SIZE_BYTES


class CreateProjectFile(Tool):
    """Read a UTF-8 text file from the project workspace."""
    name: str = "create_project_file"
    description: str = "Create a new UTF-8 text file inside the project workspace. The parent directory must already " \
                       "exist. Never overwrites an existing file. Use only for creating new files."
    parameters_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Workspace-relative path of the new file, such as src/app.ts.",
                "minLength": 1,
            },
            "content": {
                "type": "string",
                "description": "Complete text content for the new file.",
            },
        },
        "required": ["filename", "content"],
        "additionalProperties": False,
    }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        filename: str = cast(str, arguments["filename"])
        content: str = cast(str, arguments["content"])

        if not filename.strip():
            return ToolResult(success=False, error="Filename must not be empty.")

        if not isinstance(content, str):
            return ToolResult(success=False, error="File content must be a string.")

        content_size = len(content.encode("utf-8"))

        if content_size > MAX_FILE_SIZE_BYTES:
            return ToolResult(
                success=False,
                error=f"File content exceeds the {MAX_FILE_SIZE_BYTES}-byte limit."
            )

        requested_path = (self.workspace_root / filename).resolve()

        if not requested_path.is_relative_to(self.workspace_root):
            return ToolResult(success=False, error="File path must stay inside the project.")

        if requested_path == self.workspace_root:
            return ToolResult(success=False, error="Filename must identify a file.")

        as_posix = requested_path.relative_to(self.workspace_root).as_posix()
        if requested_path.exists():
            return ToolResult(success=False, error=f"File already exists: {as_posix}")

        if not requested_path.parent.is_dir():
            requested_path.parent.mkdir(parents=True, exist_ok=True)

        # Exclusive creation prevents accidentally overwriting an existing file.
        with requested_path.open("x", encoding="utf-8", newline="") as file:
            file.write(content)

        return ToolResult(success=True, data={"filename": as_posix, "created": True, "size_bytes": content_size})
