from abc import abstractmethod

from agent.domain.aggregate.conversation import Conversation
from agent.domain.aggregate.task import Task


class TaskDecompositionAgent:
    @abstractmethod
    def run(self, conversation: Conversation) -> Task: ...
