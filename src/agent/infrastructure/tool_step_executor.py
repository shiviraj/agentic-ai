from ollama import Client
from rich.console import Console

from agent.application.port.step_executor import StepExecutor
from agent.domain.entity.plan_step import PlanStep
from agent.infrastructure.prompt import STEP_EXECUTOR_PROMPT
from agent.infrastructure.tool_registry import ToolRegistry

MAX_ITERATIONS = 10


class ToolStepExecutor(StepExecutor):

    def __init__(self, client: Client, model: str, tool_registry: ToolRegistry, console: Console) -> None:
        self._client = client
        self._model = model
        self._tool_registry = tool_registry
        self._tools = tool_registry.get_tools_definition()
        self._console = console

    def execute(self, step: PlanStep):
        try:
            messages = [
                {"role": "system", "content": STEP_EXECUTOR_PROMPT},
                {"role": "user", "content": self._build_step_prompt(step)}
            ]
            for _ in range(MAX_ITERATIONS):
                with self._console.status("[green]Executing step [/]", spinner="bouncingBar"):
                    response = self._client.chat(
                        model=self._model,
                        tools=self._tools,
                        messages=messages,
                        options={"temperature": 0}
                    )
                message = response["message"]
                # messages.append(message)
                tool_calls = message.tool_calls or []
                print(len(tool_calls), tool_calls)
                if not tool_calls:
                    return {
                        "success": True,
                        "step": step,
                        "result": message.content,
                        "error": None,
                    }

                for tool_call in tool_calls:
                    tool_name = tool_call.function["name"]
                    arguments = tool_call.function["arguments"] or {}
                    tool_result = self._tool_registry.execute(tool_name, arguments)
                    messages.append({"role": "tool", "tool_name": tool_name, "content": str(tool_result)})
        except Exception as exc:
            return {
                "success": False,
                "step": step,
                "result": None,
                "error": exc,
            }

    @staticmethod
    def _build_step_prompt(step: PlanStep) -> str:
        return (
            f"Execute implementation plan step {step.sequence}.\n\n"
            f"Title: {step.title}\n"
            f"Description: {step.description}\n"
        )
