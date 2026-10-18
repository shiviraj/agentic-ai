from pathlib import Path
from typing import TypedDict

from agent.application.tool.tool import Tool, ArgsT
from agent.domain.vo.tool_result import ToolResult
from agent.domain.vo.tool_risk import ToolRisk
from agent.infrastructure.tool.util import MAX_FILE_SIZE_BYTES


class CreateProjectFileArgs(TypedDict):
    filename: str
    content: str


class CreateProjectFile(Tool[CreateProjectFileArgs]):

    @property
    def name(self) -> str:
        return "create_project"

    @property
    def display_name(self) -> str:
        return "Create a new project file"

    @property
    def description(self) -> str:
        return "Create a new UTF-8 text file inside the project workspace. The parent directory must already " \
               "exist. Never overwrites an existing file. Use only for creating new files."

    @property
    def tool_risk(self) -> ToolRisk:
        return ToolRisk.MUTATING

    @property
    def parameters_schema(self) -> dict[str, object]:
        return {
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

    def display_arguments(self, arguments: ArgsT) -> str | None:
        return f"Filename: {arguments['filename']}"

    def execute(self, arguments: CreateProjectFileArgs) -> ToolResult:
        filename = arguments["filename"]
        content = arguments["content"]
        content_size = len(content.encode("utf-8"))

        if content_size > MAX_FILE_SIZE_BYTES:
            return ToolResult(success=False, error=f"File content exceeds the {MAX_FILE_SIZE_BYTES}-byte limit.")

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
