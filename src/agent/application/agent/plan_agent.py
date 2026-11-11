from abc import abstractmethod

from agent.domain.aggregate.conversation import Conversation
from agent.domain.aggregate.implementation_plan import ImplementationPlan


class PlanAgent:
    @abstractmethod
    def run(self, conversation: Conversation) -> ImplementationPlan: ...
