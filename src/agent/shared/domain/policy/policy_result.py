from dataclasses import dataclass

from agent.shared.domain.exception.policy_violation_exception import PolicyViolationException


@dataclass
class PolicyResult:
    is_valid: bool
    errors: list[str]

    def __init__(self, is_valid: bool, errors: list[str]):
        self.is_valid = is_valid
        self.errors = errors

    @staticmethod
    def create(errors: list[str]) -> PolicyResult:
        if len(errors) == 0:
            return PolicyResult(True, [])
        return PolicyResult(False, errors)

    def enforce(self, message: str):
        if not self.is_valid:
            print("=================================")
            print(self.errors)
            print("=================================")
            raise PolicyViolationException(message, errors=self.errors)
