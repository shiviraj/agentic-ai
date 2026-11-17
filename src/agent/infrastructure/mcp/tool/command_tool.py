import contextlib
import os
import secrets
import shutil
import signal
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

MAX_OUTPUT_BYTES = 100_000
DEFAULT_TIMEOUT = 60
MAX_TIMEOUT = 300
MAX_BACKGROUND_PROCESSES = 10
MAX_TRACKED_PROCESSES = 50


# Commands are matched by their executable and required prefix.
# Additional arguments are permitted after the approved prefix.
ALLOWED_COMMANDS = (
    ("npm", "test"),
    ("npm", "run", "test"),
    ("npm", "run", "build"),
    ("npm", "run", "lint"),
    ("npm", "run", "typecheck"),
    ("npx", "tsc", "--noEmit"),
    ("uv", "run", "pytest"),
    ("pytest",),
    ("python", "-m", "pytest"),
)


class CommandToolError(Exception):
    """An expected command execution failure."""


@dataclass
class ProcessRecord:
    process: subprocess.Popen
    command: list[str]
    directory: str
    stdout_file: BinaryIO
    stderr_file: BinaryIO


class CommandTools:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._processes: dict[str, ProcessRecord] = {}
        self._lock = threading.RLock()

        if not self._root.is_dir():
            raise CommandToolError(f"Workspace directory does not exist: {self._root}")

    def run_command(
        self,
        arguments: list[str],
        directory: str = ".",
        timeout: int = DEFAULT_TIMEOUT,
        background: bool = False,
    ) -> dict[str, object]:

        self._validate_arguments(arguments)
        self._validate_timeout(timeout)

        working_directory = self._resolve_directory(directory)

        self._validate_command(arguments)

        with self._lock:
            self._validate_process_capacity(background)

            return self._execute(
                arguments=arguments,
                directory=working_directory,
                timeout=timeout,
                background=background,
            )

    def get_command_status(self, process_id: str) -> dict[str, object]:
        with self._lock:
            record = self._get_process(process_id)
            exit_code = record.process.poll()
            return {
                "process_id": process_id,
                "command": record.command,
                "status": "running" if exit_code is None else "completed",
                "exit_code": exit_code,
                "success": None if exit_code is None else exit_code == 0,
            }

    def get_command_output(self, process_id: str) -> dict[str, object]:
        with self._lock:
            record = self._get_process(process_id)
            stdout = self._read_output(record.stdout_file)
            stderr = self._read_output(record.stderr_file)
            exit_code = record.process.poll()
            return {
                "process_id": process_id,
                "stdout": stdout,
                "stderr": stderr,
                "status": "running" if exit_code is None else "completed",
                "exit_code": exit_code,
            }

    def terminate_command(self, process_id: str) -> dict[str, object]:
        with self._lock:
            record = self._get_process(process_id)
            if record.process.poll() is not None:
                return {"process_id": process_id, "status": "already_completed", "exit_code": record.process.returncode}

            try:
                self._terminate_process(record.process)
                return {"process_id": process_id, "status": "terminated", "exit_code": record.process.returncode}
            except OSError as error:
                raise CommandToolError(f"Could not terminate process: {error}") from error

    def cleanup(self) -> None:
        """Terminate active processes and release temporary files."""
        with self._lock:
            for record in self._processes.values():
                if record.process.poll() is None:
                    try:
                        self._terminate_process(record.process)
                    except OSError:
                        pass

                record.stdout_file.close()
                record.stderr_file.close()

            self._processes.clear()

    def _execute(self, arguments: list[str], directory: Path, timeout: int, background: bool) -> dict[str, object]:
        stdout_file = tempfile.TemporaryFile()
        stderr_file = tempfile.TemporaryFile()
        try:
            executable = shutil.which(arguments[0])
            if executable is None:
                raise CommandToolError(f"Command executable not found: {arguments[0]}")
            process = subprocess.Popen(
                [executable, *arguments[1:]],
                cwd=directory,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                shell=False,
                start_new_session=True,
                close_fds=True,
            )

            process_id = secrets.token_urlsafe(16)

            record = ProcessRecord(
                process=process,
                command=arguments.copy(),
                directory=str(directory),
                stdout_file=stdout_file,
                stderr_file=stderr_file,
            )

            self._processes[process_id] = record

            if background:
                return {
                    "process_id": process_id,
                    "command": arguments,
                    "status": "running",
                    "directory": str(directory),
                }

            try:
                exit_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self._terminate_process(process)

                stdout = self._read_output(stdout_file)
                stderr = self._read_output(stderr_file)

                self._release_process(process_id)

                return {
                    "command": arguments,
                    "exit_code": process.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "timed_out": True,
                    "success": False,
                }

            stdout = self._read_output(stdout_file)
            stderr = self._read_output(stderr_file)

            self._release_process(process_id)

            return {
                "command": arguments,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "timed_out": False,
                "success": exit_code == 0,
            }
        except Exception:
            stdout_file.close()
            stderr_file.close()
            raise

    def _validate_arguments(self, arguments: list[str]) -> None:
        if (
            not isinstance(arguments, list)
            or not arguments
            or not all(isinstance(arg, str) and arg and "\x00" not in arg for arg in arguments)
        ):
            raise CommandToolError("Command arguments must be a non-empty list of strings.")

    def _validate_timeout(self, timeout: int) -> None:
        if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= MAX_TIMEOUT:
            raise CommandToolError(f"Timeout must be between 1 and {MAX_TIMEOUT} seconds.")

    def _validate_command(self, arguments: list[str]) -> None:
        if not any(
            len(arguments) >= len(allowed) and tuple(arguments[: len(allowed)]) == allowed
            for allowed in ALLOWED_COMMANDS
        ):
            raise CommandToolError(f"Command is not allowed: {arguments}")

    def _resolve_directory(self, directory: str) -> Path:
        if not isinstance(directory, str) or "\x00" in directory:
            raise CommandToolError("Invalid working directory.")

        path = (self._root / directory).resolve()

        if not path.is_relative_to(self._root):
            raise CommandToolError(f"Working directory is outside workspace: {directory}")

        if not path.is_dir():
            raise CommandToolError(f"Directory does not exist: {directory}")

        return path

    def _validate_process_capacity(self, background: bool) -> None:
        if len(self._processes) >= MAX_TRACKED_PROCESSES:
            raise CommandToolError("Maximum tracked process limit reached.")

        active_count = sum(record.process.poll() is None for record in self._processes.values())

        if background and active_count >= MAX_BACKGROUND_PROCESSES:
            raise CommandToolError("Maximum background process limit reached.")

    def _get_process(self, process_id: str) -> ProcessRecord:
        if not isinstance(process_id, str) or process_id not in self._processes:
            raise CommandToolError(f"Process not found: {process_id}")

        return self._processes[process_id]

    def _release_process(self, process_id: str) -> None:
        record = self._processes.pop(process_id, None)

        if record:
            record.stdout_file.close()
            record.stderr_file.close()

    @staticmethod
    def _read_output(file: BinaryIO) -> str:
        file.flush()
        file.seek(0)

        content = file.read(MAX_OUTPUT_BYTES + 1)
        truncated = len(content) > MAX_OUTPUT_BYTES

        if truncated:
            content = content[:MAX_OUTPUT_BYTES]

        result = content.decode("utf-8", errors="replace")

        if truncated:
            result += "\n[Output truncated]"

        return result

    @staticmethod
    def _terminate_process(process: subprocess.Popen) -> None:
        if process.poll() is not None:
            return
        with contextlib.suppress(ProcessLookupError):
            os.killpg(process.pid, signal.SIGTERM)

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)

            process.wait()
