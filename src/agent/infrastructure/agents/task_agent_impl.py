from agent.application.agent.task_agent import TaskAgent
from agent.application.port.llm_client import LLMClient
from agent.domain.aggregate.conversation import Conversation
from agent.domain.llm.message import Message, Role
from agent.domain.vo.task_analysis import TaskAnalysis
from agent.infrastructure.agents.parser.analyze_task_parser import AnalyzeTaskParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class TaskAgentImpl(TaskAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._parser = AnalyzeTaskParser()
        self._system_prompt = load_prompt("analyze_task")

    def run(self, conversation: Conversation) -> TaskAnalysis:
        messages = [Message(Role.SYSTEM, self._system_prompt), *conversation.get_messages()]
        response = self._llm_client.chat(messages, schema=self._parser.schema)
        return self._parser.parse(response.content)
