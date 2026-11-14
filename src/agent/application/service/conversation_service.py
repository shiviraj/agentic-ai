from agent.domain.aggregate.conversation import Conversation
from agent.domain.entity.message import Message
from agent.domain.errors import DataNotFoundError
from agent.domain.repository.conversation_repository import ConversationRepository
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.message_type import MessageType
from agent.domain.vo.role import Role


class ConversationService:
    def __init__(self, repository: ConversationRepository):
        self._repository = repository

    def create(self) -> Conversation:
        conversation = Conversation.create()
        self._repository.save(conversation)
        return conversation

    def get_conversation(self, conversation_id: ConversationId) -> Conversation:
        conversation = self._repository.find_by_id(conversation_id)
        if conversation is None:
            raise DataNotFoundError(f"Conversation not found for {conversation_id}")
        return conversation

    def add_user_message(self, conversation_id: ConversationId, content: str) -> Message:
        message = Message.create_text(role=Role.USER, content=content)
        return self._add_message(conversation_id, message)

    def add_agent_response(self, conversation_id: ConversationId, agent_name: str, response: object) -> Message:
        message = Message.create(
            role=Role.ASSISTANT,
            message_type=MessageType.AGENT_RESPONSE,
            content=str(response),
            agent_name=agent_name,
        )
        return self._add_message(conversation_id, message)

    def add_assistant_message(self, conversation_id: ConversationId, content: str) -> Message:
        message = Message.create(role=Role.ASSISTANT, message_type=MessageType.TEXT, content=content)
        return self._add_message(conversation_id, message)

    def _add_message(self, conversation_id: ConversationId, message: Message) -> Message:
        conversation = self._repository.find_by_id(conversation_id)
        if conversation is None:
            raise DataNotFoundError(conversation_id)
        self._repository.save(conversation.add_message(message))
        return message
