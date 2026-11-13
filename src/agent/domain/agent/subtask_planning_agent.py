from abc import abstractmethod

from agent.domain.aggregate.conversation import Conversation
from agent.domain.vo.task_analysis import TaskAnalysis


class SubtaskPlanningAgent:
    @abstractmethod
    def run(self, conversation: Conversation) -> TaskAnalysis: ...
