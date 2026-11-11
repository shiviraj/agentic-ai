from agent.application.agent.plan_agent import PlanAgent
from agent.application.port.llm_client import LLMClient
from agent.domain.aggregate.conversation import Conversation
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.llm.message import Message, Role
from agent.infrastructure.agents.parser.plan_task_parser import PlanTaskParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class PlanAgentImpl(PlanAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._parser = PlanTaskParser()
        self._system_prompt = load_prompt("plan_task")

    def run(self, conversation: Conversation) -> ImplementationPlan:
        messages = [Message(Role.SYSTEM, self._system_prompt), *conversation.get_messages()]
        response = self._llm_client.chat(messages=messages, schema=self._parser.schema)
        return self._parser.parse(response.content)
