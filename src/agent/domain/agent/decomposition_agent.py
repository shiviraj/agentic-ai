from abc import abstractmethod

from agent.domain.aggregate.task import Task
from agent.domain.entity.message import Message


class DecompositionAgent:
    @abstractmethod
    def execute(self, context: tuple[Message, ...]) -> Task: ...
