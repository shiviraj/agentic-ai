from ollama import Client

from agent.application.port.step_executor import StepExecutor
from agent.domain.entity.plan_step import PlanStep
from agent.infrastructure.prompt import STEP_EXECUTOR_PROMPT
from agent.infrastructure.tool_registry import ToolRegistry


class ToolStepExecutor(StepExecutor):

    def __init__(self, client: Client, model: str, tool_registry: ToolRegistry) -> None:
        self._client = client
        self._model = model
        self._tools = tool_registry.get_tools_definition()

    def execute(self, step: PlanStep):
        try:
            messages = [
                {"role": "system", "content": STEP_EXECUTOR_PROMPT},
                {"role": "user", "content": self._build_step_prompt(step)}
            ]
            print(messages)
            response = self._client.chat(
                model=self._model,
                tools=self._tools,
                messages=messages,
                options={"temperature": 0}
            )
            print(response)
        except Exception as e:
            print(e)

    @staticmethod
    def _build_step_prompt(step: PlanStep) -> str:
        return (
            f"Execute implementation plan step {step.sequence}.\n\n"
            f"Title: {step.title}\n"
            f"Description: {step.description}\n"
        )
