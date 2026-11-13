from agent.application.agent.task_decomposition_agent import TaskDecompositionAgent
from agent.application.port.llm_client import LLMClient
from agent.domain.aggregate.conversation import Conversation
from agent.domain.aggregate.task import Task
from agent.domain.llm.message import Message, Role
from agent.infrastructure.agents.parser.task_decomposition_parser import TaskDecompositionParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class TaskDecompositionAgentImpl(TaskDecompositionAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._parser = TaskDecompositionParser()
        self._system_prompt = load_prompt("task_decomposition")

    def run(self, conversation: Conversation) -> e:
        messages = [Message(Role.SYSTEM, self._system_prompt), *conversation.get_messages()]
        response = self._llm_client.chat(messages=messages, schema=self._parser.schema)
        return self._parser.parse(response.content)
