from enum import Enum

from rich.console import Console
from rich.status import Status


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


DEBUG_ENABLED = True


class Logger:
    def __init__(self, name: str) -> None:
        self._name = name
        self._console = Console()

    def debug(self, message: str, tag: str = "dim") -> None:
        if DEBUG_ENABLED:
            self._console.print(self._get_message(message, tag, LogLevel.DEBUG))

    def error(self, message: str, tag: str = "red") -> None:
        self._console.print(self._get_message(message, tag, LogLevel.ERROR))

    def info(self, message: str, tag: str = "green") -> None:
        self._console.print(self._get_message(message, tag, LogLevel.INFO))

    def status(
        self,
        message: str,
        spinner: str,
        tag: str = "cyan",
        level: LogLevel = LogLevel.INFO,
    ) -> Status:
        return self._console.status(
            self._get_message(message, tag, level), spinner=spinner
        )

    def _get_message(
        self, message: str, tag: str = "", level: LogLevel = LogLevel.INFO
    ) -> str:
        opening_tag = f"[{tag}]" if tag != "" else ""
        closing_tag = f"[/{tag}]" if tag != "" else ""
        return f"{opening_tag}[{self._name}] [{level.title()}] {message}{closing_tag}"
