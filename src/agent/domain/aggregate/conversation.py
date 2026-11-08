from dataclasses import dataclass

from agent.domain.llm.message import Message
from agent.domain.vo.conversation_id import ConversationId
from agent.shared.domain.aggregate import Aggregate


@dataclass(eq=False)
class Conversation(Aggregate[ConversationId]):
    chats: list[Message]

    def add(self, message: Message) -> "Conversation":
        self.chats.append(message)
        return self

    def get_messages(self) -> list[Message]:
        return self.chats

    @classmethod
    def create(cls) -> "Conversation":
        return cls(id=ConversationId.generate(), chats=[])
