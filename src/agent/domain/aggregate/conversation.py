from dataclasses import dataclass

from agent.application.port.dto.llm_response import ChatResponse
from agent.domain.entity.interaction import Interaction
from agent.domain.llm.message import Message
from agent.domain.vo.agent_response import AgentResponse
from agent.domain.vo.conversation_id import ConversationId
from agent.domain.vo.user_request import UserRequest
from agent.shared.domain.aggregate import Aggregate


@dataclass(eq=False)
class Conversation(Aggregate[ConversationId]):
    messages: list[Message]
    history: list[Interaction]
    current: Interaction | None

    def add(self, message: Message) -> "Conversation":
        self.messages.append(message)
        return self

    def get_messages(self) -> list[Message]:
        return self.messages

    def start_interaction(self, request: UserRequest) -> "Conversation":
        self.current = Interaction.create(request)
        return self

    def stop_interaction(self, response: ChatResponse) -> "Conversation":
        self.current.response = response
        self.history.append(self.current)
        self.current = None
        return self

    def get_request(self) -> UserRequest:
        return self.current.request

    def add_response(self, response: AgentResponse) -> "Conversation":
        self.current.agent_responses.append(response)
        return self

    def build_agent_response(self) -> str:
        responses = [f"Response: {response}" for response in self.current.agent_responses]
        return "\n--------------\n".join(responses)

    @classmethod
    def create(cls) -> "Conversation":
        return cls(id=ConversationId.generate(), messages=[], history=[], current=None)
