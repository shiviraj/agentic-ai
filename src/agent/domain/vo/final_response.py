from dataclasses import dataclass

from agent.shared.domain.vo import ValueObject


@dataclass(frozen=True)
class FinalResponse(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("Agent response cannot be empty")
        if len(self.value.strip()) > 5000:
            raise ValueError("Agent response is too long")
