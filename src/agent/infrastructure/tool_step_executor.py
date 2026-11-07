import json
from typing import Any

from ollama import Client

from agent.application.port.step_executor import StepExecutor
from agent.application.services.tool_executor import ToolExecutor
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.step_result import StepResult
from agent.infrastructure.prompt import STEP_EXECUTOR_PROMPT
from agent.infrastructure.schema import FINISH_STEP_EXECUTION
from agent.infrastructure.tool_registry import ToolRegistry
from agent.shared.logger.logger import Logger

MAX_ITERATIONS = 20
MAX_INVALID_RESPONSES = 5


class ToolStepExecutor(StepExecutor):
    def __init__(self, client: Client, model: str, tool_registry: ToolRegistry) -> None:
        self._client = client
        self._model = model
        self._tool_registry = tool_registry
        self._logger = Logger("ToolStepExecutor")

    def execute(self, step: PlanStep, tool_executor: ToolExecutor, previous_results: list[StepResult]) -> StepResult:
        finish_name = FINISH_STEP_EXECUTION["function"]["name"]
        tools = [*self._tool_registry.tools_definition, FINISH_STEP_EXECUTION]
        allowed_tools = {definition["function"]["name"] for definition in self._tool_registry.tools_definition}

        previous_context = self._serialize_previous_results(previous_results)

        messages = [
            {
                "role": "system",
                "content": STEP_EXECUTOR_PROMPT.format(
                    current_step=f"Title: {step.title}\nDescription: {step.description}",
                    plan_progress=(
                        "Execute only the current step. The orchestrator controls progression to subsequent steps."
                    ),
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Previous execution results:\n{previous_context}\n\n"
                    "Execute the current step according to the system "
                    "instructions. Begin by selecting one appropriate tool."
                ),
            },
        ]

        executed_calls: dict[str, str] = {}
        invalid_responses = 0
        try:
            for iteration in range(MAX_ITERATIONS):
                with self._logger.status("Executing step...", "bouncingBar"):
                    response = self._client.chat(
                        model=self._model,
                        tools=tools,
                        messages=messages,
                        options={"temperature": 0},
                    )

                message = response.message
                tool_calls = message.tool_calls or []

                self._logger.debug(
                    f"Discovery iteration {iteration + 1}: {len(tool_calls)} tool call(s), message: {message}"
                )

                if len(tool_calls) != 1:
                    invalid_responses += 1

                    if not tool_calls:
                        messages.append(
                            {
                                "role": "assistant",
                                "content": message.content or "",
                            }
                        )

                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "Invalid response. You must make exactly ONE "
                                "actual tool call in this response. Do not "
                                "return ordinary text. Continue the current "
                                "step or call finish_step if the step has "
                                "reached a terminal outcome."
                            ),
                        }
                    )

                    if invalid_responses >= MAX_INVALID_RESPONSES:
                        return StepResult(
                            success=False, step=step, error="Model repeatedly failed to return exactly one tool call."
                        )

                    continue

                tool_call = tool_calls[0]
                function = tool_call.function

                name = function["name"]
                arguments = function.get("arguments", {})

                messages.append(message)

                if not isinstance(arguments, dict):
                    result_content = json.dumps({"success": False, "error": "Tool arguments must be a JSON object."})
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": name,
                            "content": result_content,
                        }
                    )
                    continue

                # The finish tool terminates this step and is never
                # executed through the ordinary project-tool executor.
                if name == finish_name:
                    return self._build_finish_result(step, arguments)

                # Prevent unregistered tools from being executed.
                if name not in allowed_tools:
                    result_content = json.dumps(
                        {
                            "success": False,
                            "error": f"Tool {name!r} is not registered.",
                        }
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_name": name,
                            "content": result_content,
                        }
                    )
                    continue

                call_key = json.dumps(
                    {"tool_name": name, "arguments": arguments, "version": tool_executor.version},
                    sort_keys=True,
                    separators=(",", ":"),
                    default=str,
                )

                # Reuse the previous result instead of executing twice.
                if call_key in executed_calls:
                    result_content = executed_calls[call_key]
                    messages.append({"role": "tool", "tool_name": name, "content": result_content})
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "You repeated an identical tool call. Its result is already "
                                "available above. Do not call it again. Choose a different "
                                "registered tool that provides missing information, or call "
                                f"{finish_name} if the step is complete. "
                                "You must make exactly one native tool call."
                            ),
                        }
                    )
                    continue

                # Execute each distinct tool call at most once.
                try:
                    tool = self._tool_registry.get_tool(name)
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
                    result_content = json.dumps(
                        {
                            "success": False,
                            "error": str(exc),
                        }
                    )

                executed_calls[call_key] = result_content

                messages.append({"role": "tool", "tool_name": name, "content": result_content})

            return StepResult(
                success=False,
                step=step,
                error=(f"Step exceeded the maximum of {MAX_ITERATIONS} LLM iterations without a finish_step call."),
            )

        except Exception as exc:
            return StepResult(success=False, step=step, error=str(exc))

    @staticmethod
    def _build_finish_result(step: PlanStep, arguments: dict[str, Any]) -> StepResult:
        status = arguments.get("status")
        summary = arguments.get("summary")

        if status not in {"success", "failure", "blocked"}:
            return StepResult(
                success=False,
                step=step,
                error="finish_step returned an invalid status.",
            )

        if not isinstance(summary, str) or not summary.strip():
            return StepResult(
                success=False,
                step=step,
                error="finish_step must provide a non-empty summary.",
            )

        data = {"status": status, "summary": summary}

        return StepResult(success=(status == "success"), step=step, data=data)

    @staticmethod
    def _serialize_previous_results(previous_results: list[StepResult]) -> str:
        if not previous_results:
            return "No previous steps have been executed."

        results = []

        for result in previous_results:
            results.append(
                {
                    "step": {
                        "title": result.step.title,
                        "description": result.step.description,
                    },
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                }
            )

        return json.dumps(results, indent=2, default=str)
