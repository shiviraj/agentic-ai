from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject(ABC):  # noqa: B024
    """Immutable domain value without independent identity."""
