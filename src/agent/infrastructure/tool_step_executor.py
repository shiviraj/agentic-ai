import json
from typing import Any

from ollama import Client
from rich.console import Console

from agent.application.port.step_executor import StepExecutor
from agent.application.services.tool_executor import ToolExecutor
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.step_result import StepResult
from agent.infrastructure.prompt import STEP_EXECUTOR_PROMPT
from agent.infrastructure.schema import FINISH_STEP_EXECUTION
from agent.infrastructure.tool_registry import ToolRegistry

MAX_ITERATIONS = 10
MAX_INVALID_RESPONSES = 3


class ToolStepExecutor(StepExecutor):

    def __init__(self, client: Client, model: str, tool_registry: ToolRegistry, console: Console) -> None:
        self._client = client
        self._model = model
        self._tool_registry = tool_registry
        self._console = console

    def execute(self, step: PlanStep, tool_executor: ToolExecutor) -> StepResult:
        finish_name = FINISH_STEP_EXECUTION["function"]["name"]

        tools = [
            *self._tool_registry.tools_definition,
            FINISH_STEP_EXECUTION,
        ]

        allowed_tools = {
            definition["function"]["name"]
            for definition in self._tool_registry.tools_definition
        }

        messages = [
            {
                "role": "system",
                "content": STEP_EXECUTOR_PROMPT.format(
                    current_step=self._build_step_prompt(step),
                    plan_progress=(
                        "Execute only the current step. The orchestrator "
                        "controls progression to subsequent steps."
                    ),
                ),
            },
            {"role": "user", "content": (
                "Execute the current step according to the system instructions. Begin by selecting one appropriate tool."),
             },
        ]

        # Maps a canonical tool call to its result.
        # Identical calls will never execute twice during this step.
        executed_calls: dict[str, str] = {}

        invalid_responses = 0

        try:
            for iteration in range(MAX_ITERATIONS):
                with self._console.status(f"[green]Executing step {step.sequence}...[/]", spinner="bouncingBar", ):
                    response = self._client.chat(
                        model=self._model,
                        tools=tools,
                        messages=messages,
                        options={"temperature": 0},
                    )

                message = response.message
                tool_calls = message.tool_calls or []

                self._console.print(f"[dim]Iteration {iteration + 1}: {len(tool_calls)} tool call(s)[/dim]")

                # Enforce exactly one tool call per response.
                if len(tool_calls) != 1:
                    invalid_responses += 1

                    # Do not append a multi-tool-call assistant message:
                    # its tool calls would remain unresolved in history.
                    if not tool_calls:
                        messages.append({"role": "assistant", "content": message.content or "", })

                    messages.append({
                        "role": "user",
                        "content": (
                            "Invalid response. You must make exactly ONE "
                            "actual tool call in this response. Do not "
                            "return ordinary text. Continue the current "
                            "step or call finish_step if the step has "
                            "reached a terminal outcome."
                        ),
                    })

                    if invalid_responses >= MAX_INVALID_RESPONSES:
                        return StepResult(
                            success=False,
                            step=step,
                            error="Model repeatedly failed to return exactly one tool call.",
                        )

                    continue

                tool_call = tool_calls[0]
                function = tool_call.function

                # Support Ollama objects and dictionary-shaped responses.
                tool_name = (function.name if hasattr(function, "name") else function["name"])
                arguments = (function.arguments if hasattr(function, "arguments") else function.get("arguments", {}))

                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = None

                # Preserve the actual assistant tool-call message.
                messages.append(message)

                if not isinstance(arguments, dict):
                    result_content = json.dumps({"success": False, "error": "Tool arguments must be a JSON object.", })
                    messages.append({"role": "tool", "tool_name": tool_name, "content": result_content, })
                    continue

                # The finish tool terminates this step and is never
                # executed through the ordinary project-tool executor.
                if tool_name == finish_name:
                    return self._build_finish_result(step, arguments)

                # Prevent unregistered tools from being executed.
                if tool_name not in allowed_tools:
                    result_content = json.dumps({"success": False, "error": f"Tool {tool_name!r} is not registered.", })
                    messages.append({"role": "tool", "tool_name": tool_name, "content": result_content, })
                    continue

                call_key = json.dumps({"tool": tool_name, "arguments": arguments, }, sort_keys=True,
                                      separators=(",", ":"), default=str, )

                # Reuse the previous result instead of executing twice.
                if call_key in executed_calls:
                    result_content = executed_calls[call_key]
                    messages.append({"role": "tool", "tool_name": tool_name, "content": result_content, })
                    messages.append({"role": "user", "content": (
                        "This exact tool call has already been executed. Use its previous result and choose a different action, or call finish_step if the step is complete or cannot proceed."),
                                     })
                    continue

                # Execute each distinct tool call at most once.
                try:
                    tool = self._tool_registry.get_tool(tool_name)
                    tool_result = tool_executor.execute(tool, arguments)

                    result_content = json.dumps(
                        {
                            "success": tool_result.success,
                            "data": tool_result.data,
                            "error": (str(tool_result.error) if tool_result.error is not None else None),
                        },
                        default=str,
                    )
                except Exception as exc:
                    result_content = json.dumps({"success": False, "error": str(exc), })

                executed_calls[call_key] = result_content

                messages.append({"role": "tool", "tool_name": tool_name, "content": result_content, })

            return StepResult(success=False, step=step, error=(
                f"Step exceeded the maximum of {MAX_ITERATIONS} " "LLM iterations without a finish_step call."), )

        except Exception as exc:
            return StepResult(success=False, step=step, error=str(exc), )

    @staticmethod
    def _build_finish_result(step: PlanStep, arguments: dict[str, Any]) -> StepResult:
        status = arguments.get("status")
        summary = arguments.get("summary")
        validation_results = arguments.get("validation_results")
        files_changed = arguments.get("files_changed")
        errors = arguments.get("errors")
        remaining_work = arguments.get("remaining_work")

        if status not in {"success", "failure", "blocked"}:
            return StepResult(success=False, step=step, error="finish_step returned an invalid status.", )

        if not isinstance(summary, str) or not summary.strip():
            return StepResult(success=False, step=step, error="finish_step must provide a non-empty summary.", )

        for field_name, value in (
                ("validation_results", validation_results),
                ("files_changed", files_changed),
                ("errors", errors),
                ("remaining_work", remaining_work),
        ):
            if not isinstance(value, list) or not all(
                    isinstance(item, str) for item in value
            ):
                return StepResult(success=False, step=step, error=f"finish_step returned invalid {field_name}.", )

        data = {
            "status": status,
            "summary": summary,
            "validation_results": validation_results,
            "files_changed": files_changed,
            "errors": errors,
            "remaining_work": remaining_work,
        }

        return StepResult(
            success=(status == "success"),
            step=step,
            data=data,
            error=(
                "; ".join(errors)
                or summary
                if status != "success"
                else None
            ),
        )

    @staticmethod
    def _build_step_prompt(step: PlanStep) -> str:
        return (
            f"Step sequence: {step.sequence}\n"
            f"Title: {step.title}\n"
            f"Description: {step.description}\n"
        )
