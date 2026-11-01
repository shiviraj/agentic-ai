from abc import abstractmethod, ABC
from typing import Generic, TypeVar

from agent.shared.domain.policy.policy_result import PolicyResult

T = TypeVar("T")

class Policy(ABC, Generic[T]):
    @abstractmethod
    def evaluate(self, data: T) -> PolicyResult:
        ...
