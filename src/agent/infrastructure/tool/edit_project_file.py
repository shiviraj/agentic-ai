from pathlib import Path
from typing import cast, TypedDict

from agent.domain.vo.tool_result import ToolResult
from agent.application.tool.tool import Tool, ArgsT
from agent.domain.vo.tool_risk import ToolRisk
from agent.infrastructure.tool.util import MAX_FILE_SIZE_BYTES

class EditProjectFileArgs(TypedDict):
    filename: str
    old_text: str
    new_text: str

class EditProjectFile(Tool[EditProjectFileArgs]):
    """Read a UTF-8 text file from the project workspace."""

    @property
    def display_name(self) -> str:
        return "Edit project file"

    @property
    def name(self) -> str:
        return "edit_project_file"

    @property
    def description(self) -> str:
        return "Replace exactly one occurrence of a text string in an existing UTF-8 project file. Fails if " \
               "the text is missing or ambiguous. Does not create files."

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
                "old_text": {
                    "type": "string",
                    "description": "Exact text to find and replace.",
                    "minLength": 1,
                },
                "new_text": {
                    "type": "string",
                    "description": "Replacement text.",
                },
            },
            "required": ["filename", "old_text", "new_text"],
            "additionalProperties": False
        }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def display_arguments(self, arguments: ArgsT) -> str | None:
        return f"Filename: {arguments['filename']}"

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        filename: str = cast(str, arguments["filename"])
        new_text: str = cast(str, arguments["new_text"])
        old_text: str = cast(str, arguments["old_text"])

        if not filename.strip():
            return ToolResult(success=False, error="Filename must not be empty.")

        if not old_text:
            return ToolResult(success=False, error="Search text must not be empty.")

        if not isinstance(new_text, str):
            return ToolResult(success=False, error="Replacement content must be a string.")

        requested_path = (self.workspace_root / filename).resolve()

        if not requested_path.is_relative_to(self.workspace_root):
            return ToolResult(success=False, error="File path must stay inside the project.")

        if requested_path == self.workspace_root or not requested_path.is_file():
            return ToolResult(success=False, error=f"File not found: {filename}")

        size_bytes = requested_path.stat().st_size
        if size_bytes > MAX_FILE_SIZE_BYTES:
            return ToolResult(success=False, error=
            f"File is too large to edit. Maximum size is {MAX_FILE_SIZE_BYTES} bytes.")

        try:
            original_content = requested_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ToolResult(success=False, error="File is not valid UTF-8 text.")

        occurrences = original_content.count(old_text)

        if occurrences == 0:
            return ToolResult(success=False, error="Search text was not found in the file.")

        if occurrences > 1:
            return ToolResult(success=False,
                              error=f"Search text is ambiguous: found {occurrences} occurrences.")

        updated_content = original_content.replace(old_text, new_text, 1)
        updated_size = len(updated_content.encode("utf-8"))

        if updated_size > MAX_FILE_SIZE_BYTES:
            return ToolResult(
                success=False,
                error=f"Updated file exceeds the {MAX_FILE_SIZE_BYTES}-byte limit."
            )

        requested_path.write_text(updated_content, encoding="utf-8")

        return ToolResult(
            success=True,
            data={
                "filename": requested_path.relative_to(self.workspace_root).as_posix(),
                "updated": True,
                "size_bytes_before": size_bytes,
                "size_bytes_after": updated_size,
                "replacements": 1,
            }
        )
