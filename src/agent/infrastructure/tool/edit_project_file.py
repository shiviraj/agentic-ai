from pathlib import Path
from typing import cast

from agent.domain.vo.tool_result import ToolResult
from agent.infrastructure.tool.tool import Tool
from agent.infrastructure.tool.util import MAX_FILE_SIZE_BYTES


class EditProjectFile(Tool):
    """Read a UTF-8 text file from the project workspace."""
    name: str = "edit_project_file"
    description: str = "Replace exactly one occurrence of a text string in an existing UTF-8 project file. Fails if " \
                       "the text is missing or ambiguous. Does not create files."
    parameters_schema: dict[str, object] = {
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

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        filename: str = cast(str, arguments["filename"])
        new_text: str = cast(str, arguments["new_text"])
        old_text: str = cast(str, arguments["old_text"])

        print("---------------------------------")
        print(filename)
        print("---------------------------------")
        print(old_text)
        print("---------------------------------")
        print(new_text)
        print("---------------------------------")

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
