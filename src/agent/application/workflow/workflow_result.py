from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowResult:
    content: str
