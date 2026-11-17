from typing import TypeVar

from agent.domain.agent.agent import Agent
from agent.domain.entity.message import Message
from agent.domain.tool.tool import ToolDefinition
from agent.domain.vo.tool_response import ToolResponse
from agent.infrastructure.agent.llm_agent import LLMAgent
from agent.infrastructure.agent.parser.output_parser import OutputParser
from agent.infrastructure.llm.llm_client import LLMClient
from agent.infrastructure.prompts.prompt_loader import load_prompt

T = TypeVar("T")


class AgentImpl(LLMAgent[T], Agent[T]):
    def __init__(self, llm_client: LLMClient, prompt: str, parser: OutputParser[T]):
        super().__init__(llm_client, load_prompt(prompt))
        self._parser = parser

    def execute(self, context: tuple[Message, ...]) -> T:
        return self._ask_json(context, self._parser)

    def execute_tools(self, context: tuple[Message, ...], tools: tuple[ToolDefinition, ...]) -> ToolResponse:
        return self._tools(context, tools=tools)
