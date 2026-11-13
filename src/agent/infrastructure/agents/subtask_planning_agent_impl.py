from agent.application.agent.subtask_planning_agent import SubtaskPlanningAgent
from agent.application.port.llm_client import LLMClient
from agent.domain.aggregate.conversation import Conversation
from agent.domain.aggregate.execution_plan import ExecutionPlan
from agent.domain.llm.message import Message, Role
from agent.infrastructure.agents.parser.execution_plan_parser import ExecutionPlanParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class SubtaskPlanningAgentImpl(SubtaskPlanningAgent):
    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client
        self._parser = ExecutionPlanParser()
        self._system_prompt = load_prompt("plan_subtask")

    def run(self, conversation: Conversation) -> ExecutionPlan:
        messages = [Message(Role.SYSTEM, self._system_prompt), *conversation.get_messages()]
        response = self._llm_client.chat(messages=messages, schema=self._parser.schema)
        return self._parser.parse(response.content)
