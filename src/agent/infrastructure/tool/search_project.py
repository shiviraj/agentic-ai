from pathlib import Path
from typing import cast

from agent.domain.vo.tool_result import ToolResult
from agent.infrastructure.tool.tool import Tool
from agent.infrastructure.tool.util import MAX_FILE_SIZE_BYTES, IGNORED_DIRECTORIES


class SearchProject(Tool):
    """Read a UTF-8 text file from the project workspace."""
    name: str = "search_project"
    description: str = "Search project text files for a case-insensitive query. Returns matching file paths, line " \
                       "numbers, and line content. Read-only; does not modify files."
    parameters_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Text to search for.",
                "minLength": 1,
            },
            "file_pattern": {
                "type": "string",
                "description": (
                    "Glob pattern for filenames, such as *.py or *.ts."
                ),
                "default": "*",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of matching lines to return.",
                "minimum": 1,
                "default": 100,
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    }

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def execute(self, arguments: dict[str, object]) -> ToolResult:
        query: str = cast(str, arguments["query"])
        file_pattern: str = cast(str, arguments["file_pattern"]) or "*"
        max_results: int = cast(int, arguments["max_results"]) or 100
        if not query.strip():
            return ToolResult(success=False, error=ValueError("Search query must not be empty."))

        if max_results < 1:
            return ToolResult(success=False, error=ValueError("max_results must be greater than zero."))

        if not self.workspace_root.is_dir():
            return ToolResult(
                success=False,
                error=NotADirectoryError(f"Project workspace is not a directory: {self.workspace_root}")
            )

        matches: list[dict[str, object]] = []
        files_scanned = 0
        truncated = False

        for path in sorted(self.workspace_root.rglob(file_pattern)):
            relative_path = path.relative_to(self.workspace_root)

            if any(
                    part.startswith(".") or part in IGNORED_DIRECTORIES
                    for part in relative_path.parts[:-1]
            ):
                continue

            if not path.is_file():
                continue

            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            files_scanned += 1

            for line_number, line in enumerate(content.splitlines(), start=1):
                if query.casefold() not in line.casefold():
                    continue

                if len(matches) >= max_results:
                    truncated = True
                    break

                matches.append({"filename": relative_path.as_posix(), "line_number": line_number, "line": line.strip()})

            if truncated:
                break

        return ToolResult(
            success=True,
            data={
                "query": query,
                "file_pattern": file_pattern,
                "files_scanned": files_scanned,
                "match_count": len(matches),
                "truncated": truncated,
                "matches": matches,
            }
        )
