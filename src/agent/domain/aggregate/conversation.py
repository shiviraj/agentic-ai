from dataclasses import dataclass, field
from datetime import datetime, timezone

from agent.domain.entity.message import Message
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.domain.aggregate import Aggregate


@dataclass(eq=False)
class Conversation(Aggregate[ConversationId]):
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, message: Message) -> "Conversation":
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)
        return self

    @classmethod
    def create(cls) -> "Conversation":
        return cls(id=ConversationId.generate())
