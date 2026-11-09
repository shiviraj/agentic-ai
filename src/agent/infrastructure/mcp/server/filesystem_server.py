import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from agent.infrastructure.mcp.tool.filesystem_tool import FilesystemToolError, FilesystemTools


def create_server(root: Path) -> FastMCP:
    files = FilesystemTools(root)
    server = FastMCP("filesystem")

    # FastMCP builds each tool's name, description and input schema from the
    # function name, the docstring and the type hints. The LLM reads them.

    @server.tool
    def list_directory(path: str = ".") -> str:
        """List every file under a folder, including sub-folders, one path per line.

        Paths are relative to the project root. Skips node_modules, .git, dist
        and similar folders. Use this first to see how the project is laid out.
        'path' is the folder to list; it defaults to the project root.
        """
        try:
            return files.list_directory(path)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    @server.tool
    def read_file(path: str) -> str:
        """Read the full text of one file.

        'path' is relative to the project root, for example 'src/index.ts'.
        Binary files and files larger than 200 KB are refused.
        """
        try:
            return files.read_file(path)
        except FilesystemToolError as error:
            raise ToolError(str(error)) from error

    return server


def main() -> None:
    cwd = Path.cwd().resolve()
    load_dotenv()
    relative_path = os.getenv("WORKSPACE")
    root = (cwd / relative_path).resolve()

    create_server(root).run()  # stdio is the default transport


if __name__ == "__main__":
    main()
