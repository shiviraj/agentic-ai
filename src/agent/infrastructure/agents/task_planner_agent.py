from agent.application.port.llm_client import LLMClient
from agent.domain.agent.agent_result import AgentResult
from agent.domain.agent.agent_role import AgentRole
from agent.domain.errors import InvalidAgentOutputError, LlmUnavailableError
from agent.domain.task.task import Task
from agent.infrastructure.agents.llm_agent import LLMAgent
from agent.infrastructure.agents.parser.task_analysis_parser import TaskAnalysisParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


def _build_user_message(task: Task) -> str:
    lines = [f"Task: {task.prompt.value}"]
    if task.clarifications:
        lines.append("")
        lines.append("Questions already asked and the user's answers:")
        for question, answer in task.clarifications:
            lines.append(f"Q: {question}")
            lines.append(f"A: {answer}")
    return "\n".join(lines)


class TaskPlannerAgent(LLMAgent):
    def __init__(
        self, llm: LLMClient, parser: TaskPlannerParser | None = None, system_prompt: str | None = None
    ) -> None:
        super().__init__(llm, system_prompt or load_prompt("task_analyser"))
        self._parser = parser or TaskAnalysisParser()

    @property
    def role(self) -> AgentRole:
        return AgentRole.ANALYSER

    def run(self, task: Task) -> AgentResult:
        try:
            analysis = self._ask_json(_build_user_message(task), self._parser)
            print(analysis)
        except (InvalidAgentOutputError, LlmUnavailableError) as e:
            return AgentResult.failed(f"Task analyser could not finish: {e}")

        if analysis.ready:
            return AgentResult.done(analysis.requirements)
