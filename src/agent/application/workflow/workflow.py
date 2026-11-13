from abc import ABC, abstractmethod

from agent.application.workflow.workflow_input import WorkflowInput
from agent.application.workflow.workflow_result import WorkflowResult


class Workflow(ABC):
    @abstractmethod
    def execute(self, data: WorkflowInput) -> WorkflowResult: ...
