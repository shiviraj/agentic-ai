from abc import ABC, abstractmethod


class ConversationAgent(ABC):
    @abstractmethod
    def execute(self, user_request: str) -> str:
        pass
