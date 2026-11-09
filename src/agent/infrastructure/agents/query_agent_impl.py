from agent.application.agent.query_agent import QueryAgent
from agent.application.port.llm_client import LLMClient
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.domain.tool.tool import ToolDefinition
from agent.infrastructure.agents.utils import to_ollama_tools
from agent.infrastructure.prompts.prompt_loader import load_prompt


class QueryAgentImpl(QueryAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        # self._parser = AnalyzeUserRequestParser()
        self._system_prompt = load_prompt("analyze_user_query")

    def run(self, conversation: Conversation, tools: list[ToolDefinition]) -> str:
        tools_definitions = to_ollama_tools(tools)
        messages = [Message(Role.SYSTEM, self._system_prompt), *conversation.get_messages()]
        print("-----------------------")
        print(messages)
        print("-----------------------")
        print(tools)
        print("-----------------------")
        print(tools_definitions)
        print("-----------------------")
        response = self._llm_client.tool(messages=messages, tools=tools_definitions)
        print(response)
        print("-----------------------")
        return response
        # return self._parser.parse(response)
