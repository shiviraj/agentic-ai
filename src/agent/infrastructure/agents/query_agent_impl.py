from agent.application.agent.query_agent import QueryAgent
from agent.application.port.llm_client import LLMClient
from agent.application.service.dto.analyze_query_result import AnalyzeQueryResult
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.domain.tool.tool import ToolDefinition
from agent.infrastructure.llm.finish_tool import FINISH_TOOL
from agent.infrastructure.llm.utils import to_ollama_tools
from agent.infrastructure.prompts.prompt_loader import load_prompt


class QueryAgentImpl(QueryAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._system_prompt = load_prompt("analyze_user_query")

    def run(self, conversation: Conversation, tools: list[ToolDefinition]) -> AnalyzeQueryResult:
        tools_definitions = [*to_ollama_tools(tools), FINISH_TOOL]
        messages = [Message(Role.SYSTEM, self._system_prompt), *conversation.get_messages()]
        response = self._llm_client.tool(messages=messages, tools=tools_definitions)
        if response.tools and response.tools[0].name == FINISH_TOOL["function"]["name"]:
            return AnalyzeQueryResult(content=response.tools[0].arguments["content"], tools=[], finished=True)

        return AnalyzeQueryResult(content=response.content, tools=response.tools, finished=False)
