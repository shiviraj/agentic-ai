from dataclasses import dataclass

from agent.shared.domain.vo import ValueObject


@dataclass(frozen=True)
class Prompt(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Prompt cannot be empty")
