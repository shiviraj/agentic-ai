from abc import ABC, abstractmethod


class UserInteraction(ABC):
    @abstractmethod
    def ask(self, question: str) -> str:
        """Show the question to the user and return their answer."""
