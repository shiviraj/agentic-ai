from dataclasses import dataclass

from agent.shared.domain.vo import ValueObject


@dataclass(frozen=True)
class UserRequest(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("User request cannot be empty")
        if len(self.value.strip()) > 3000:
            raise ValueError("User request is too long")
