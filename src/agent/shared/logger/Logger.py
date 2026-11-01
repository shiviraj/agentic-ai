from rich.console import Console
from rich.status import Status


class Logger:
    def __init__(self, name: str) -> None:
        self._name = name
        self._console = Console()

    def log(self, message: str, tag: str = "") -> None:
        opening_tag = f"[{tag}]" if tag != "" else ""
        closing_tag = f"[/{tag}]" if tag != "" else ""
        self._console.print(f"{opening_tag}[{self._name}] {message}{closing_tag}")

    def status(self, message: str, spinner: str, tag: str = "") -> Status:
        opening_tag = f"[{tag}]" if tag != "" else ""
        closing_tag = f"[/{tag}]" if tag != "" else ""
        return self._console.status(f"{opening_tag}[{self._name}] {message}{closing_tag}", spinner=spinner)
