import os
from pathlib import Path

IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        "node_modules",
        "dist",
        "build",
        "coverage",
        ".next",
        ".venv",
        "__pycache__",
    }
)

MAX_LISTED_FILES = 1000
MAX_FILE_BYTES = 200_000


class FilesystemToolError(Exception):
    """An expected filesystem inspection failure."""


class FilesystemTools:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def inspect_project(self, directory: str = ".") -> str:
        path = (self._root / directory).resolve()
        if not path.is_relative_to(self._root):
            raise FilesystemToolError(f"Path is outside the project root: {directory}")

        if not path.exists():
            raise FilesystemToolError(f"Path does not exist: {directory}")

        if not path.is_dir():
            raise FilesystemToolError(f"Not a directory: {directory}")

        files: list[str] = []
        for current, directory_names, file_names in os.walk(path):
            directory_names[:] = sorted(name for name in directory_names if name not in IGNORED_DIRECTORIES)

            for file_name in file_names:
                full_path = Path(current) / file_name
                relative_path = full_path.relative_to(self._root).as_posix()

                files.append(relative_path)

                if len(files) >= MAX_LISTED_FILES:
                    files.sort()
                    return "\n".join(files) + f"\n... truncated at {MAX_LISTED_FILES} files"

        files.sort()
        return "\n".join(files) if files else "No files found."

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

        # Prevent access outside the project root, including symlinks.
        if not candidate.is_relative_to(self._root):
            raise FilesystemToolError(f"Path is outside the project root: {relative_path}")

        if not candidate.exists():
            raise FilesystemToolError(f"Path does not exist: {relative_path}")

        return candidate
