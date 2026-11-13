from agent.application.agent.summary_agent import SummaryAgent
from agent.application.port.dto.llm_response import ChatResponse
from agent.application.port.llm_client import LLMClient
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.infrastructure.prompts.prompt_loader import load_prompt


class SummaryAgentImpl(SummaryAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._system_prompt = load_prompt("summarize_response")

    def run(self, conversation: Conversation) -> ChatResponse:
        messages = [Message(Role.SYSTEM, self._system_prompt), *conversation.get_messages()]
        return self._llm_client.chat(messages=messages)
