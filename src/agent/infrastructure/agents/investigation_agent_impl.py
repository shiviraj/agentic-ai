from agent.application.port.llm_client import LLMClient
from agent.domain.agent.dto.investigation_agent_result import InvestigationAgentResult
from agent.domain.agent.investigation_agent import InvestigationAgent
from agent.domain.entity.message import Message, Role
from agent.domain.tool.finish_tool_definition import FINISH_TOOL_DEFINITION
from agent.domain.tool.tool import ToolDefinition
from agent.infrastructure.prompts.prompt_loader import load_prompt


class InvestigationAgentImpl(InvestigationAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._system_prompt = load_prompt("investigation_agent")

    def execute(self, context: list[Message], tools: list[ToolDefinition]) -> InvestigationAgentResult:
        messages = [Message.create_text(role=Role.SYSTEM, content=self._system_prompt), *context]
        response = self._llm_client.tool(messages=messages, tools=tools)
        if response.tools and response.tools[0].name == FINISH_TOOL_DEFINITION.name:
            return InvestigationAgentResult(content=response.tools[0].arguments["content"], tools=[], finished=True)

        return InvestigationAgentResult(content=response.content, tools=response.tools, finished=False)
