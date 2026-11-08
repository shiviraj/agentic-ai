from agent.application.agent.dto.analyze_result import AnalyzeUserRequestResult
from agent.application.port.engineer_agent import EngineerAgent
from agent.application.port.llm_client import LLMClient
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.infrastructure.agents.parser.analyze_user_request_parser import AnalyzeUserRequestParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class EngineerAgentImpl(EngineerAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._parser = AnalyzeUserRequestParser()
        self._system_prompt = load_prompt("analyze_user_request")

    def analyze(self, conversation: Conversation) -> AnalyzeUserRequestResult:
        messages = [Message(Role.SYSTEM, self._system_prompt), *conversation.get_messages()]
        response = self._llm_client.chat(messages=messages, schema=self._parser.schema)
        return self._parser.parse(response)
