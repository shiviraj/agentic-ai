from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionResult:
    content: str
