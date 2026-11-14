from agent.application.port.llm_client import LLMClient
from agent.domain.agent.conversation_agent import ConversationAgent
from agent.domain.entity.message import Message
from agent.domain.vo.chat_response import ChatResponse
from agent.domain.vo.role import Role
from agent.infrastructure.prompts.prompt_loader import load_prompt


class ConversationAgentImpl(ConversationAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._system_prompt = load_prompt("conversation_agent")

    def execute(self, context: list[Message]) -> ChatResponse:
        messages = [Message.create_text(role=Role.SYSTEM, content=self._system_prompt), *context]
        return self._llm_client.chat(messages=messages)
