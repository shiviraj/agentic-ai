from dataclasses import dataclass

from agent.shared.domain.identifier import Identifier


@dataclass(frozen=True)
class MessageId(Identifier):
    pass
