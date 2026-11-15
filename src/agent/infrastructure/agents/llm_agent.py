from typing import TypeVar

from agent.application.port.llm_client import LLMClient
from agent.domain.entity.message import Message
from agent.domain.errors import InvalidAgentResponseError
from agent.domain.tool.finish_tool_definition import FINISH_TOOL_DEFINITION
from agent.domain.tool.tool import ToolDefinition
from agent.domain.vo.role import Role
from agent.domain.vo.tool_response import ToolResponse
from agent.infrastructure.agents.parser.output_parser import OutputParser

T = TypeVar("T")


class LLMAgent:
    def __init__(self, llm: LLMClient, system_prompt: str, max_attempts: int = 5) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self._llm = llm
        self._system_prompt = system_prompt
        self._max_attempts = max_attempts

    def _ask_json(self, context: tuple[Message, ...], parser: OutputParser[T]) -> T:
        messages = [Message.create_text(role=Role.SYSTEM, content=self._system_prompt), *context]
        last_error: Exception | None = None

        for _ in range(self._max_attempts):
            reply = self._llm.chat(messages, parser.schema)
            try:
                return parser.parse(reply)
            except InvalidAgentResponseError as e:
                last_error = e
                messages.append(Message.create_text(Role.ASSISTANT, reply))
                messages.append(
                    Message.create_text(
                        Role.USER,
                        f"Your last answer was not valid: {e}. Reply again with ONLY the corrected JSON object.",
                    )
                )

        raise InvalidAgentResponseError(f"no valid answer after {self._max_attempts} attempts: {last_error}")

    def _tools(self, context: tuple[Message, ...], tools: tuple[ToolDefinition, ...]) -> ToolResponse:
        messages = [Message.create_text(role=Role.SYSTEM, content=self._system_prompt), *context]
        last_error: InvalidAgentResponseError | None = None

        for _ in range(self._max_attempts):
            response = self._llm.tool(messages, [*tools, FINISH_TOOL_DEFINITION])
            if not response.tools and not response.content:
                messages.append(
                    Message.create_text(
                        Role.ASSISTANT,
                        "Your previous response was empty. "
                        "You must continue the investigation by calling at least"
                        "one available tool. If the investigation is complete "
                        "or cannot continue, call the `__agent__::finish` tool. "
                        "Do not return an empty response or plain text.",
                    )
                )
                continue

            if response.tools and response.tools[0].name == FINISH_TOOL_DEFINITION.name:
                response.finished = True
                response.content = response.tools[0].arguments["summary"]
                response.tools = []
            return response

        raise InvalidAgentResponseError(f"no valid tool answer after {self._max_attempts} attempts: {last_error}")
