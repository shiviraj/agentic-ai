from agent.application.port.llm_client import LLMClient
from agent.domain.agent.decomposition_agent import DecompositionAgent
from agent.domain.aggregate.task import Task
from agent.domain.entity.message import Message
from agent.infrastructure.agents.llm_agent import LLMAgent
from agent.infrastructure.agents.parser.task_parser import TaskParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class DecompositionAgentImpl(LLMAgent, DecompositionAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, load_prompt("decomposition_agent"))
        self._parser = TaskParser()

    def execute(self, context: tuple[Message, ...]) -> Task:
        return self._ask_json(context, self._parser)
