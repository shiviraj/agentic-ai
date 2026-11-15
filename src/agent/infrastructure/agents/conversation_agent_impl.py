from agent.application.port.llm_client import LLMClient
from agent.domain.agent.conversation_agent import ConversationAgent
from agent.domain.entity.message import Message
from agent.domain.vo.chat_response import ChatResponse
from agent.infrastructure.agents.llm_agent import LLMAgent
from agent.infrastructure.agents.parser.default_parser import DefaultParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class ConversationAgentImpl(LLMAgent, ConversationAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, load_prompt("conversation_agent"))
        self._parser = DefaultParser()

    def execute(self, context: tuple[Message, ...]) -> ChatResponse:
        return self._ask_json(context, self._parser)
