import subprocess
from pathlib import Path
from typing import TypedDict

from agent.application.tool.tool import Tool, ArgsT
from agent.domain.vo.tool_result import ToolResult
from agent.domain.vo.tool_risk import ToolRisk


class RunProjectCommandArgs(TypedDict):
    command: list[str]
    timeout_seconds: int


class RunProjectCommand(Tool[RunProjectCommandArgs]):
    DEFAULT_TIMEOUT_SECONDS = 60
    MAX_TIMEOUT_SECONDS = 300
    MAX_OUTPUT_LENGTH = 10_000

    def __init__(self, workspace_root: Path) -> None:
        self._workspace_root = workspace_root.resolve()

    @property
    def display_name(self) -> str:
        return "Run Project Command"

    @property
    def name(self) -> str:
        return "run_project_command"

    @property
    def description(self) -> str:
        return "Run an approved project validation command, such as tests, linting, type checking, or building, " \
               "inside the workspace."

    @property
    def tool_risk(self) -> ToolRisk:
        return ToolRisk.DESTRUCTIVE

    @property
    def parameters_schema(self) -> dict[str, object]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Command and arguments, e.g. "
                        '["npm", "test"] or ["npm", "run", "build"].'
                    ),
                    "minItems": 2,
                },
                "timeout_seconds": {
                    "type": "integer",
                    "description": "Command timeout, between 1 and 300 seconds.",
                    "minimum": 1,
                    "maximum": 300,
                },
            },
            "required": ["command"],
            "additionalProperties": False,
        }

    def display_arguments(self, arguments: RunProjectCommandArgs) -> str | None:
        command = arguments.get("command")
        return " ".join(str(part) for part in command)

    def execute(self, arguments: RunProjectCommandArgs) -> ToolResult:
        command = arguments.get("command")
        timeout = arguments.get("timeout_seconds", self.DEFAULT_TIMEOUT_SECONDS)

        argv = tuple(command)

        try:
            completed = subprocess.run(
                list(argv),
                cwd=self._workspace_root,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )

            stdout = completed.stdout or ""
            stderr = completed.stderr or ""
            if completed.returncode == 0:
                print(f"Output: ${stdout}")
            else:
                print(f"Error: ${stderr}")
            completed.check_returncode()

            return ToolResult(
                success=completed.returncode == 0,
                data={
                    "command": list(argv),
                    "working_directory": str(self._workspace_root),
                    "exit_code": completed.returncode,
                    "stdout": stdout[:self.MAX_OUTPUT_LENGTH],
                    "stderr": stderr[:self.MAX_OUTPUT_LENGTH],
                    "output_truncated": (
                            len(stdout) > self.MAX_OUTPUT_LENGTH
                            or len(stderr) > self.MAX_OUTPUT_LENGTH
                    ),
                },
                error=(
                    None
                    if completed.returncode == 0
                    else f"Command failed with exit code {completed.returncode}."
                ),
            )

        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error=f"Command timed out after {timeout} seconds.")

        except OSError as exc:
            return ToolResult(success=False, error=f"Could not execute command: {exc}")
