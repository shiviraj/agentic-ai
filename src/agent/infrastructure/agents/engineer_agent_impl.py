from agent.application.port.llm_client import LLMClient
from agent.domain.agent.dto.engineer_agent_result import EngineerAgentResult
from agent.domain.agent.engineer_agent import EngineerAgent
from agent.domain.entity.message import Message
from agent.domain.errors import InvalidAgentResponseError
from agent.domain.vo.role import Role
from agent.domain.vo.user_request import UserRequest
from agent.infrastructure.agents.parser.engineer_agent_result_parser import EngineerAgentResultParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class EngineerAgentImpl(EngineerAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._parser = EngineerAgentResultParser()
        self._system_prompt = load_prompt("engineer_agent")

    def execute(self, context: list[Message], user_request: UserRequest) -> EngineerAgentResult:
        messages = [
            Message.create_text(role=Role.SYSTEM, content=self._system_prompt),
            *context,
            Message.create_text(role=Role.USER, content=self._build_prompt(user_request)),
        ]
        for _ in range(3):
            try:
                response = self._llm_client.chat(messages=messages, schema=self._parser.schema)
                return self._parser.parse(response.content)
            except InvalidAgentResponseError as e:
                messages.append(
                    Message.create_text(role=Role.USER, content=f"Your previous response was invalid: {e}"),
                )

    def _build_prompt(self, user_request: UserRequest) -> str:
        return f"""
        You are the Engineer Agent, the primary request classification agent
        for an AI-powered Senior Backend Engineer system.

        Your responsibility is to understand the user's latest request,
        consider the relevant conversation history, and classify the request

        User request:
        {user_request.value}
        """
