import json

from ollama import Client

from agent.application.port.context_discoverer import ContextDiscoverer
from agent.application.services.tool_executor import ToolExecutor
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult
from agent.infrastructure.prompt import PROJECT_DISCOVERY_PROMPT
from agent.infrastructure.schema import FINISH_DISCOVERY_EXECUTION
from agent.infrastructure.tool_registry import ToolRegistry
from agent.infrastructure.tool_step_executor import MAX_ITERATIONS, MAX_INVALID_RESPONSES
from agent.shared.logger.Logger import Logger


class ContextDiscovererImpl(ContextDiscoverer):

    def __init__(self, client: Client, model: str, tool_registry: ToolRegistry, ) -> None:
        self._client = client
        self._model = model
        self._tool_registry = tool_registry
        self._logger = Logger("ContextDiscovererImpl")

    def discover(
            self,
            analysis_result: RequirementAnalysisResult,
            prompt: Prompt,
            tool_executor: ToolExecutor
    ) -> ProjectContext:
        finish_name = FINISH_DISCOVERY_EXECUTION["function"]["name"]
        discovery_tools = [*self._tool_registry.discovery_tools_definition, FINISH_DISCOVERY_EXECUTION]

        allowed_tools = {
            definition["function"]["name"]
            for definition in self._tool_registry.discovery_tools_definition
        }

        prompt_format = PROJECT_DISCOVERY_PROMPT.format(
            context_request=analysis_result.context_request,
            requirement=prompt.value
        )
        messages = [
            {"role": "system", "content": prompt_format},
            {"role": "user", "content": prompt.value},
        ]

        # Raw successful tool evidence is retained in findings until
        # dedicated structured extraction is implemented.
        findings: list[str] = []
        unresolved_questions: list[str] = []

        successful_evidence = False

        # Maps a normalized tool call to its previous result.
        # Repeated calls reuse the result instead of executing again.
        executed_calls: dict[str, str] = {}
        invalid_responses = 0

        for iteration in range(MAX_ITERATIONS):
            with self._logger.status("Discovering context...", "bouncingBar"):
                response = self._client.chat(
                    model=self._model,
                    messages=messages,
                    tools=discovery_tools,
                    options={"temperature": 0},
                )

            message = response.message
            tool_calls = message.tool_calls or []

            self._logger.debug(
                f"Discovery iteration {iteration + 1}: {len(tool_calls)} tool call(s), message: {message}")

            # Require exactly one tool call per model response.
            if len(tool_calls) != 1:
                invalid_responses += 1
                messages.append({"role": "assistant", "content": message.content or ""})
                messages.append({
                    "role": "user",
                    "content": (
                        "Invalid response: you must call exactly one "
                        "available tool. Do not write a report as text. "
                        "Continue discovery or call the registered "
                        f"{finish_name} tool when sufficient evidence "
                        "has been collected."
                    ),
                })

                if invalid_responses > MAX_INVALID_RESPONSES:
                    self._logger.error("Discovery model repeatedly returned responses without exactly one tool call.")
                    raise RuntimeError("Discovery model repeatedly returned responses without exactly one tool call.")
                continue

            tool_call = tool_calls[0]
            function = tool_call.function

            # Support attribute-based and dictionary-shaped tool calls.
            name = function["name"]
            arguments = function.get("arguments", {})

            # Preserve the assistant message containing the tool call.
            messages.append(message)

            # Handle the terminal tool separately.
            if name == finish_name:
                if not successful_evidence:
                    messages.append({
                        "role": "tool",
                        "name": name,
                        "content": json.dumps({
                            "success": False,
                            "error": (
                                "No successful discovery evidence has "
                                "been collected. Continue with an available "
                                "discovery tool or report the blocker."
                            ),
                        }),
                    })
                    continue

                return ProjectContext(findings=findings, unresolved_questions=unresolved_questions)

            # Only registered discovery tools may execute.
            if name not in allowed_tools:
                result_content = json.dumps(
                    {"success": False, "error": f"Tool {name!r} is not permitted during discovery."}
                )
                messages.append({"role": "tool", "name": name, "content": result_content})
                continue

            # Canonicalize arguments so dictionary key order does not
            # affect duplicate-call detection.
            call_key = json.dumps(
                {"tool": name, "arguments": arguments, "version": tool_executor.version},
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            )

            # Reuse the result of an identical tool call.
            if call_key in executed_calls:
                result_content = executed_calls[call_key]

                messages.append({"role": "tool", "tool_name": name, "content": result_content})
                messages.append({
                    "role": "user",
                    "content": (
                        "This exact tool call was already executed. "
                        "Use its returned result and choose a different "
                        "action, or finish discovery if sufficient "
                        "evidence has been collected."
                    ),
                })
                continue

            # Execute the registered tool.
            try:
                tool = self._tool_registry.get_tool(name)
                result = tool_executor.execute(tool, arguments)

                if result.success:
                    result_content = json.dumps({"success": True, "data": result.data}, default=str)
                    successful_evidence = True
                    findings.append(
                        f"Tool: {name}\nArguments: {json.dumps(arguments, default=str)}\nResult: {result_content}"
                    )
                else:
                    error_message = str(result.error)
                    result_content = json.dumps({"success": False, "error": error_message})
                    unresolved_questions.append(f"Discovery tool {name} failed: {error_message}")

            except Exception as exc:
                result_content = json.dumps({"success": False, "error": str(exc)})
                unresolved_questions.append(f"Discovery tool {name} raised an exception: {exc}")

            # Cache both successful and failed results so the same
            # arguments cannot trigger repeated execution.
            executed_calls[call_key] = result_content
            messages.append({"role": "tool", "tool_name": name, "content": result_content})
        self._logger.error(
            f"Project discovery exceeded {MAX_ITERATIONS} iterations without a valid completion tool call.")
        raise RuntimeError(
            f"Project discovery exceeded {MAX_ITERATIONS} iterations without a valid completion tool call."
        )
