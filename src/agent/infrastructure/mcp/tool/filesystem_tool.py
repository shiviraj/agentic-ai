"""The real work behind the two filesystem tools. No MCP and no JSON in here."""

import os
from pathlib import Path

# Folders that are noise in a TypeScript project and would flood the LLM context.
IGNORED_DIRECTORIES = frozenset({".git", "node_modules", "dist", "build", "coverage", ".next", ".venv", "__pycache__"})
MAX_LISTED_FILES = 1000
MAX_FILE_BYTES = 200_000


class FilesystemToolError(Exception):
    """An expected failure the LLM should be told about (bad path, file too big...)."""


class FilesystemTools:
    """Read-only access to files inside one root folder."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def list_directory(self, relative_path: str = ".") -> str:
        directory = self._resolve(relative_path)
        if not directory.is_dir():
            raise FilesystemToolError(f"Not a directory: {relative_path}")

        files: list[str] = []
        for current, directory_names, file_names in os.walk(directory):
            # Changing this list in place tells os.walk to skip those folders.
            directory_names[:] = [name for name in directory_names if name not in IGNORED_DIRECTORIES]
            for file_name in file_names:
                full_path = Path(current) / file_name
                files.append(full_path.relative_to(self._root).as_posix())

        if not files:
            return "(no files found)"
        files.sort()
        if len(files) > MAX_LISTED_FILES:
            hidden = len(files) - MAX_LISTED_FILES
            files = files[:MAX_LISTED_FILES]
            files.append(f"... {hidden} more files not shown. List a sub-folder to see them.")
        return "\n".join(files)

    def read_file(self, relative_path: str) -> str:
        file_path = self._resolve(relative_path)
        if not file_path.is_file():
            raise FilesystemToolError(f"Not a file: {relative_path}")
        if file_path.stat().st_size > MAX_FILE_BYTES:
            raise FilesystemToolError(f"File is too large (limit {MAX_FILE_BYTES} bytes): {relative_path}")
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise FilesystemToolError(f"Not a UTF-8 text file: {relative_path}") from None
        except OSError as error:
            raise FilesystemToolError(f"Could not read {relative_path}: {error.strerror}") from error

    def _resolve(self, relative_path: str) -> Path:
        candidate = (self._root / relative_path).resolve()
        # Safety: after following ".." and symlinks, the path must still be inside the root.
        if not candidate.is_relative_to(self._root):
            raise FilesystemToolError(f"Path is outside the project root: {relative_path}")
        if not candidate.exists():
            raise FilesystemToolError(f"Path does not exist: {relative_path}")
        return candidate
