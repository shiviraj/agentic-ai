import fnmatch
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
PROTECTED_DIRECTORIES = IGNORED_DIRECTORIES

MAX_LISTED_FILES = 1000
MAX_FILE_BYTES = 200_000


class FilesystemToolError(Exception):
    """An expected filesystem inspection failure."""


class FilesystemTools:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def inspect_project(self, directory: str = ".", max_results: int = MAX_LISTED_FILES) -> dict[str, object]:
        path = self._resolve(directory)
        if not path.is_dir():
            raise FilesystemToolError(f"Not a directory: {directory}")
        if not 1 <= max_results <= MAX_LISTED_FILES:
            raise FilesystemToolError(f"max_results must be between 1 and {MAX_LISTED_FILES}")
        files: list[str] = []
        total_files = 0
        truncated = False
        for current, directory_names, file_names in os.walk(path):
            directory_names[:] = sorted(name for name in directory_names if name not in IGNORED_DIRECTORIES)
            for file_name in sorted(file_names):
                full_path = Path(current) / file_name
                relative_path = full_path.relative_to(self._root).as_posix()
                total_files += 1
                if len(files) < max_results:
                    files.append(relative_path)
                else:
                    truncated = True
                    break
            if truncated:
                break
        files.sort()
        return {"directory": directory, "files": files, "total_files": total_files, "truncated": truncated}

    def read_file(self, relative_path: str) -> dict[str, object]:
        file_path = self._resolve(relative_path)

        if not file_path.is_file():
            raise FilesystemToolError(f"Not a file: {relative_path}")

        if file_path.stat().st_size > MAX_FILE_BYTES:
            raise FilesystemToolError(f"File is too large (limit {MAX_FILE_BYTES} bytes): {relative_path}")

        try:
            return {"path": relative_path, "content": file_path.read_text(encoding="utf-8")}
        except UnicodeDecodeError:
            raise FilesystemToolError(f"Not a UTF-8 text file: {relative_path}") from None

        except OSError as error:
            raise FilesystemToolError(f"Could not read {relative_path}: {error.strerror}") from error

    def write_file(self, relative_path: str, content: str, overwrite: bool = False) -> dict[str, object]:
        file_path = self._resolve(relative_path, must_exist=False)
        if file_path.exists():
            if not file_path.is_file():
                raise FilesystemToolError(f"Not a file: {relative_path}")
            if not overwrite:
                raise FilesystemToolError(f"File already exists: {relative_path}. Set overwrite=True to replace it.")

        if len(content.encode("utf-8")) > MAX_FILE_BYTES:
            raise FilesystemToolError(f"Content exceeds maximum file size of {MAX_FILE_BYTES} bytes.")

        if not file_path.parent.is_dir():
            raise FilesystemToolError(f"Parent directory does not exist: {file_path.parent}")

        try:
            file_path.write_text(content, encoding="utf-8")
            return {
                "path": relative_path,
                "status": "created" if not overwrite or not file_path.exists() else "written",
            }
        except OSError as error:
            raise FilesystemToolError(f"Could not write {relative_path}: {error}") from error

    def edit_file(self, relative_path: str, old_text: str, new_text: str) -> dict[str, object]:
        file_path = self._resolve(relative_path)
        if not file_path.is_file():
            raise FilesystemToolError(f"Not a file: {relative_path}")
        try:
            content = file_path.read_text(encoding="utf-8")
            if old_text not in content:
                raise FilesystemToolError(f"Target text not found in {relative_path}")
            if content.count(old_text) != 1:
                raise FilesystemToolError(f"Target text must occur exactly once in {relative_path}")
            updated_content = content.replace(old_text, new_text, 1)
            if len(updated_content.encode("utf-8")) > MAX_FILE_BYTES:
                raise FilesystemToolError("Updated content exceeds maximum file size.")
            file_path.write_text(updated_content, encoding="utf-8")
            return {"path": relative_path, "status": "updated"}
        except UnicodeDecodeError:
            raise FilesystemToolError(f"Not a UTF-8 text file: {relative_path}") from None
        except OSError as error:
            raise FilesystemToolError(f"Could not edit {relative_path}: {error}") from error

    def create_directory(self, relative_path: str) -> dict[str, object]:
        directory_path = self._resolve(relative_path, must_exist=False)
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
            return {"path": relative_path, "status": "created"}
        except OSError as error:
            raise FilesystemToolError(f"Could not create directory: {error}") from error

    def delete_file(self, relative_path: str) -> dict[str, object]:
        file_path = self._resolve(relative_path)
        if not file_path.is_file():
            raise FilesystemToolError(f"Not a file: {relative_path}")
        self._validate_mutation_path(file_path, relative_path)
        try:
            file_path.unlink()
            return {"path": relative_path, "status": "deleted"}
        except OSError as error:
            raise FilesystemToolError(f"Could not delete {relative_path}: {error.strerror}") from error

    def move_file(self, source: str, destination: str, overwrite: bool = False) -> dict[str, object]:
        source_path = self._resolve(source)
        destination_path = self._resolve(destination, must_exist=False)
        if not source_path.is_file():
            raise FilesystemToolError(f"Source is not a file: {source}")
        self._validate_mutation_path(source_path, source)
        self._validate_mutation_path(destination_path, destination)
        if source_path == destination_path:
            raise FilesystemToolError("Source and destination cannot be the same.")
        if not destination_path.parent.is_dir():
            raise FilesystemToolError(f"Destination directory does not exist: {destination_path.parent}")
        if destination_path.is_dir():
            raise FilesystemToolError(f"Destination is a directory: {destination}")
        destination_exists = destination_path.exists()
        if destination_exists and not overwrite:
            raise FilesystemToolError(f"Destination already exists: {destination}")
        try:
            if overwrite:
                destination_path.parent.mkdir(parents=False, exist_ok=True)
                source_path.replace(destination_path)
            else:
                source_path.rename(destination_path)
            return {"source": source, "destination": destination, "status": "moved", "overwritten": destination_exists}
        except OSError as error:
            raise FilesystemToolError(f"Could not move {source} to {destination}: {error.strerror}") from error

    def get_file_info(self, relative_path: str) -> dict[str, object]:
        file_path = self._resolve(relative_path)
        try:
            stat = file_path.stat()
            return {
                "path": relative_path,
                "name": file_path.name,
                "extension": file_path.suffix,
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "size_bytes": stat.st_size,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime,
                "accessed_at": stat.st_atime,
            }
        except OSError as error:
            raise FilesystemToolError(
                f"Could not retrieve file information for {relative_path}: {error.strerror}"
            ) from error

    def search_files(
        self,
        query: str,
        directory: str = ".",
        file_pattern: str = "*",
        search_content: bool = True,
        max_results: int = 100,
    ) -> dict[str, object]:
        if not query.strip():
            raise FilesystemToolError("Search query cannot be empty.")
        if not 1 <= max_results <= MAX_LISTED_FILES:
            raise FilesystemToolError(f"max_results must be between 1 and {MAX_LISTED_FILES}")
        root_path = self._resolve(directory)
        if not root_path.is_dir():
            raise FilesystemToolError(f"Not a directory: {directory}")
        matches: list[dict[str, object]] = []
        scanned_files = 0
        skipped_files = 0
        truncated = False
        search_query = query.casefold()

        def add_match(
            relative_path: str, match_type: str, line_number: int | None = None, snippet: str | None = None
        ) -> bool:
            nonlocal truncated
            if len(matches) >= max_results:
                truncated = True
                return False
            match: dict[str, object] = {"path": relative_path, "match_type": match_type}
            if line_number is not None:
                match["line_number"] = line_number
            if snippet is not None:
                match["snippet"] = snippet
            matches.append(match)
            return True

        for current, directory_names, file_names in os.walk(root_path):
            directory_names[:] = sorted(name for name in directory_names if name not in IGNORED_DIRECTORIES)
            for file_name in sorted(file_names):
                if not fnmatch.fnmatch(file_name, file_pattern):
                    continue

                full_path = Path(current) / file_name
                relative_path = full_path.relative_to(self._root).as_posix()

                scanned_files += 1

                # Search filename.
                if search_query in file_name.casefold() and not add_match(relative_path, "filename"):
                    break

                # Search file contents.
                if not search_content:
                    continue

                try:
                    if full_path.stat().st_size > MAX_FILE_BYTES:
                        skipped_files += 1
                        continue

                    content = full_path.read_text(encoding="utf-8")

                except UnicodeDecodeError:
                    skipped_files += 1
                    continue

                except OSError:
                    skipped_files += 1
                    continue

                for line_number, line in enumerate(content.splitlines(), start=1):
                    if search_query not in line.casefold():
                        continue

                    if not add_match(
                        relative_path=relative_path,
                        match_type="content",
                        line_number=line_number,
                        snippet=line.strip()[:300],
                    ):
                        break

                if truncated:
                    break

            if truncated:
                break

        return {
            "query": query,
            "directory": directory,
            "file_pattern": file_pattern,
            "matches": matches,
            "total_matches": len(matches),
            "scanned_files": scanned_files,
            "skipped_files": skipped_files,
            "truncated": truncated,
        }

    def _resolve(self, relative_path: str, *, must_exist: bool = False) -> Path:
        candidate = (self._root / relative_path).resolve()

        if not candidate.is_relative_to(self._root):
            raise FilesystemToolError(f"Path is outside the project root: {relative_path}")

        if must_exist and not candidate.exists():
            raise FilesystemToolError(f"Path does not exist: {relative_path}")

        return candidate

    def _validate_mutation_path(self, path: Path, relative_path: str) -> None:
        try:
            relative = path.relative_to(self._root)
        except ValueError:
            raise FilesystemToolError(f"Path is outside the project root: {relative_path}") from None
        protected = PROTECTED_DIRECTORIES.intersection(relative.parts)
        if protected:
            directory = next(iter(protected))
            raise FilesystemToolError(f"Modification inside protected directory is not allowed: {directory}")
