from abc import abstractmethod

from agent.domain.aggregate.execution_plan import ExecutionPlan
from agent.domain.entity.message import Message


class SubtaskPlanningAgent:
    @abstractmethod
    def execute(self, context: tuple[Message, ...]) -> ExecutionPlan: ...
