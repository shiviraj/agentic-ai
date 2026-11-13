from dataclasses import dataclass

from agent.domain.aggregate.execution_plan import ExecutionPlan
from agent.domain.entity.subtask import Subtask


@dataclass(frozen=True)
class TestDesignInput:
    original_request: str
    task_analysis: TaskAnalysisResult
    sub_task: Subtask
    execution_plan: ExecutionPlan
    project_context: ProjectContext
