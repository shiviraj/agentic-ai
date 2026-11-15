from agent.application.port.llm_client import LLMClient
from agent.domain.agent.investigation_agent import InvestigationAgent
from agent.domain.entity.message import Message
from agent.domain.tool.tool import ToolDefinition
from agent.domain.vo.tool_response import ToolResponse
from agent.infrastructure.agents.llm_agent import LLMAgent
from agent.infrastructure.prompts.prompt_loader import load_prompt


class InvestigationAgentImpl(LLMAgent, InvestigationAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, load_prompt("investigation_agent"))

    def execute(self, context: tuple[Message, ...], tools: tuple[ToolDefinition, ...]) -> ToolResponse:
        return self._tools(context, tools=tools)
