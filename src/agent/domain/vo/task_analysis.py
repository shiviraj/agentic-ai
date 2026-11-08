# agent/domain/agent/task_analysis.py
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskAnalysis:
    summary: str
    requirements: list[str]
