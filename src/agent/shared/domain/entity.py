from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

IdT = TypeVar("IdT")


@dataclass(eq=False)
class Entity(ABC, Generic[IdT]):
    id: IdT