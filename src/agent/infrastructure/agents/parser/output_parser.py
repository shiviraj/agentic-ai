import json
from typing import Any, Protocol, TypeVar

T_co = TypeVar("T_co", covariant=True)


class OutputParser(Protocol[T_co]):
    """Knows the shape the LLM must answer in, and how to check the answer."""

    @property
    def schema(self) -> dict[str, Any]: ...

    def parse(self, raw: str) -> T_co:
        """Return the result, or raise InvalidAgentOutputError."""
        ...

    def validate(self, data: T_co) -> T_co: ...


def parse_json_object(raw: str) -> dict[str, Any] | list:
    return json.loads(raw)
