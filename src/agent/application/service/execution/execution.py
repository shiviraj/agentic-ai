from abc import ABC, abstractmethod

from agent.application.service.execution.execution_result import ExecutionResult
from agent.application.workflow.workflow_input import WorkflowInput
from agent.domain.aggregate.execution_plan import ExecutionStep


class Execution(ABC):
    @abstractmethod
    async def execute(self, data: WorkflowInput, step: ExecutionStep) -> ExecutionResult: ...
