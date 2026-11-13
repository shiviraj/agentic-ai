from dataclasses import dataclass

from agent.domain.entity.message import Message


@dataclass(frozen=True)
class ConversationAgentInput:
    messages: tuple[Message, ...]
