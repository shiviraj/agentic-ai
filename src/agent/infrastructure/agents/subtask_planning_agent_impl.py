from agent.application.port.llm_client import LLMClient
from agent.domain.agent.subtask_planning_agent import SubtaskPlanningAgent
from agent.domain.aggregate.execution_plan import ExecutionPlan
from agent.domain.entity.message import Message
from agent.infrastructure.agents.llm_agent import LLMAgent
from agent.infrastructure.agents.parser.execution_plan_parser import ExecutionPlanParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class SubtaskPlanningAgentImpl(LLMAgent, SubtaskPlanningAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, load_prompt("subtask_planning_agent"))
        self._parser = ExecutionPlanParser()

    def execute(self, context: tuple[Message, ...]) -> ExecutionPlan:
        return self._ask_json(context, self._parser)
