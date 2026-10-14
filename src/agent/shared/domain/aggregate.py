from abc import ABC
from typing import TypeVar

from agent.shared.domain.entity import Entity

IdT = TypeVar("IdT")


class Aggregate(Entity[IdT], ABC):
    """Entity that owns an aggregate's consistency boundary."""
