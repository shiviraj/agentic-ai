from ollama import Client
from rich.console import Console

from agent.application.port.step_executor import StepExecutor
from agent.application.services.tool_executor import ToolExecutor
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.step_result import StepResult
from agent.infrastructure.prompt import STEP_EXECUTOR_PROMPT
from agent.infrastructure.tool_registry import ToolRegistry

MAX_ITERATIONS = 10


class ToolStepExecutor(StepExecutor):

    def __init__(self, client: Client, model: str, tool_registry: ToolRegistry, console: Console) -> None:
        self._client = client
        self._model = model
        self._tool_registry = tool_registry
        self._console = console

    def execute(self, step: PlanStep, tool_executor: ToolExecutor) -> StepResult:
        try:
            messages = [
                {"role": "system", "content": STEP_EXECUTOR_PROMPT},
                {"role": "user", "content": self._build_step_prompt(step)}
            ]
            for _ in range(MAX_ITERATIONS):
                with self._console.status("[green]Executing step [/]", spinner="bouncingBar"):
                    response = self._client.chat(
                        model=self._model,
                        tools=self._tool_registry.tools_definition,
                        messages=messages,
                        options={"temperature": 0}
                    )
                message = response["message"]
                # messages.append(message)
                tool_calls = message.tool_calls or []
                if not tool_calls:
                    return StepResult(success=True, step=step, data=message.content)

                for tool_call in tool_calls:
                    tool_name = tool_call.function["name"]
                    arguments = tool_call.function["arguments"] or {}
                    tool = self._tool_registry.get_tool(tool_name)
                    tool_result = tool_executor.execute(tool, arguments)
                    messages.append({"role": "tool", "tool_name": tool_name, "content": str(tool_result)})
            else:
                return StepResult(success=True, step=step)
        except Exception as exc:
            return StepResult(success=False, step=step, error=str(exc))

    @staticmethod
    def _build_step_prompt(step: PlanStep) -> str:
        return (
            f"Execute implementation plan step {step.sequence}.\n\n"
            f"Title: {step.title}\n"
            f"Description: {step.description}\n"
        )
