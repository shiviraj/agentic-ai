import json
from typing import cast

from ollama import Client
from rich.console import Console

from agent.application.port.planner import Planner
from agent.application.services.tool_executor import ToolExecutor
from agent.domain.vo.plan_proposal import ProposedPlanStep, RequirementAnalysisResult
from agent.domain.vo.prompt import Prompt
from agent.infrastructure.prompt import PLAN_PROMPT, PROJECT_DISCOVERY_PROMPT, ANALYSE_REQUIREMENT_PROMPT, \
    SUMMARIZE_DISCOVERY_CONTEXT_PROMPT
from agent.infrastructure.schema import PLAN_SCHEMA, ANALYSIS_SCHEMA, SUMMARIZE_DISCOVERY_CONTEXT_SCHEMA, \
    FINISH_DISCOVERY_EXECUTION
from agent.infrastructure.tool_registry import ToolRegistry
from agent.infrastructure.tool_step_executor import MAX_ITERATIONS


class OllamaPlanner(Planner):
    """Infrastructure adapter implementing the Planner application port."""

    def __init__(self, client: Client, model: str, tool_registry: ToolRegistry, console: Console) -> None:
        self._client = client
        self._model = model
        self._tool_registry = tool_registry
        self._console = console

    def create_proposal(self, context: str | None, prompt: Prompt) -> list[ProposedPlanStep]:
        try:
            project_context = (
                context.strip() if context and context.strip() else "No project-specific context was provided.")

            system_prompt = PLAN_PROMPT.format(user_request=prompt.value, project_context=project_context, )

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": ("Generate the implementation plan for the request using the supplied project context " \
                                "and output schema."),
                },
            ]

            with self._console.status("[cyan]Generating plan...[/cyan]", spinner="bouncingBar", ):
                response = self._client.chat(
                    model=self._model,
                    messages=messages,
                    format=PLAN_SCHEMA,
                    options={"temperature": 0},
                )

            content = response.message.content

            if not isinstance(content, str) or not content.strip():
                raise ValueError("Model returned an empty plan proposal.")

            data = json.loads(content)

            if not isinstance(data, dict) or set(data) != {"steps"}:
                raise ValueError("Plan must be an object containing only 'steps'.")

            raw_steps = data["steps"]

            if not isinstance(raw_steps, list) or not 1 <= len(raw_steps):
                raise ValueError("Expected between 1 and 5 plan steps.")

            steps: list[ProposedPlanStep] = []

            for index, item in enumerate(raw_steps, start=1):
                if not isinstance(item, dict) or set(item) != {"title", "description"}:
                    raise ValueError(f"Plan step {index} must contain only " "'title' and 'description'.")

                title = item["title"]
                description = item["description"]

                if not isinstance(title, str) or not title.strip():
                    raise ValueError(f"Plan step {index} has an invalid title.")

                if not isinstance(description, str) or not description.strip():
                    raise ValueError(f"Plan step {index} has an invalid description.")

                steps.append(ProposedPlanStep(title=title.strip(), description=description.strip(), ))

            self._console.print("[green][bold]Generated plan successfully[/bold][/green]")
            return steps

        except (KeyError, TypeError, ValueError) as exc:
            self._console.print("[red]Failed to generate plan[/red]")
            raise RuntimeError("Ollama returned an invalid plan proposal.") from exc

    def discover_context(
            self,
            analysis_result: RequirementAnalysisResult,
            prompt: Prompt,
            tool_executor: ToolExecutor,
    ) -> str | None:
        if not analysis_result.require_context:
            return None

        finish_name = FINISH_DISCOVERY_EXECUTION["function"]["name"]

        discovery_tools = [
            *self._tool_registry.discovery_tools_definition,
            FINISH_DISCOVERY_EXECUTION,
        ]

        allowed_tools = {
            definition["function"]["name"]
            for definition in self._tool_registry.discovery_tools_definition
        }

        messages = [
            {
                "role": "system",
                "content": PROJECT_DISCOVERY_PROMPT.format(
                    context_request=analysis_result.context_request,
                    requirement=prompt.value,
                ),
            },
            {"role": "user", "content": prompt.value},
        ]

        context_parts: list[str] = []
        successful_evidence = False

        # Maps a normalized tool call to its previous result.
        # Repeated calls reuse the result rather than executing again.
        executed_calls: dict[str, str] = {}

        invalid_responses = 0
        max_invalid_responses = 3

        for iteration in range(MAX_ITERATIONS):
            with self._console.status("[cyan]Discovering context...[/cyan]", spinner="bouncingBar"):
                response = self._client.chat(
                    model=self._model,
                    messages=messages,
                    tools=discovery_tools,
                    options={"temperature": 0},
                )

            message = response.message
            tool_calls = message.tool_calls or []

            self._console.print(f"[dim]Discovery iteration {iteration + 1}: {len(tool_calls)} tool call(s)[/dim]")

            # Never interpret plain text as a tool call.
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

                if invalid_responses >= max_invalid_responses:
                    raise RuntimeError("Discovery model repeatedly returned responses without exactly one tool call.")
                continue

            tool_call = tool_calls[0]
            function = tool_call.function

            # Ollama tool calls normally expose these as attributes.
            # The fallback also supports dictionary-shaped responses.
            name = (function.name if hasattr(function, "name") else function["name"])
            arguments = (function.arguments if hasattr(function, "arguments") else function.get("arguments", {}))

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = None

            # Reject malformed arguments before executing anything.
            if not isinstance(arguments, dict):
                messages.append({"role": "assistant", "content": (
                    f"Invalid arguments returned for tool {name!r}. " "Call one tool with valid JSON arguments."), })
                continue

            # Preserve the actual assistant tool-call message.
            messages.append(message)

            # Handle the terminal tool separately. Never send it to
            # the regular project-tool executor.
            if name == finish_name:
                reason = arguments.get("reason")

                if not isinstance(reason, str) or not reason.strip():
                    messages.append({
                        "role": "tool",
                        "tool_name": name,
                        "content": json.dumps(
                            {"success": False, "error": "A non-empty completion reason is required."}),
                    })
                    continue

                if not successful_evidence:
                    messages.append({
                        "role": "tool",
                        "tool_name": name,
                        "content": json.dumps({
                            "success": False,
                            "error": (
                                "No successful discovery evidence has been "
                                "collected. Continue with an available "
                                "discovery tool or report the blocker."
                            ),
                        }),
                    })
                    continue

                self._console.print("[green][bold]Discovery completed successfully[/bold][/green]")
                return "\n\n".join(context_parts)

            # Only registered discovery tools may be executed here.
            if name not in allowed_tools:
                result_content = json.dumps(
                    {"success": False, "error": f"Tool {name!r} is not permitted during discovery."})
                messages.append({"role": "tool", "tool_name": name, "content": result_content})
                continue

            # Canonicalize arguments so key order doesn't cause duplicates.
            call_key = json.dumps(
                {"tool": name, "arguments": arguments},
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            )

            # If this exact call was already executed, reuse its result.
            if call_key in executed_calls:
                result_content = executed_calls[call_key]

                messages.append({"role": "tool", "tool_name": name, "content": result_content, })
                messages.append({"role": "user", "content": (
                    "This exact tool call was already executed. Use its returned result and choose a different action, or finish discovery if sufficient evidence has been collected."),
                                 })
                continue

            # Record the call result so it cannot be executed twice.
            try:
                tool = self._tool_registry.get_tool(name)
                result = tool_executor.execute(tool, arguments)

                if result.success:
                    result_content = json.dumps({"success": True, "data": result.data}, default=str)
                    successful_evidence = True
                else:
                    result_content = json.dumps({"success": False, "error": str(result.error)})

            except Exception as exc:
                result_content = json.dumps({"success": False, "error": str(exc)})

            executed_calls[call_key] = result_content

            messages.append({"role": "tool", "tool_name": name, "content": result_content})

            context_parts.append(
                f"Tool: {name}\nArguments: {json.dumps(arguments, default=str)}\nResult: {result_content}")

        raise RuntimeError(
            f"Project discovery exceeded {MAX_ITERATIONS} iterations without a valid completion tool call.")

    def analyze_requirement(self, prompt: Prompt) -> RequirementAnalysisResult:
        messages = [
            {"role": "system", "content": ANALYSE_REQUIREMENT_PROMPT},
            {"role": "user", "content": prompt.value}
        ]
        try:
            with self._console.status("[cyan]Analysing requirements...[/cyan]", spinner="bouncingBar"):
                response = self._client.chat(
                    model=self._model,
                    messages=messages,
                    format=ANALYSIS_SCHEMA,
                    options={"temperature": 0}
                )
            result = json.loads(response.message["content"])
            context_request = result["context_request"]
            require_context = cast(bool, result["require_context"])

            self._console.print("[green][bold]Analysed requirements successfully[/bold][/green]")
            return RequirementAnalysisResult(context_request=context_request, require_context=require_context)
        except (KeyError, TypeError, ValueError) as exc:
            self._console.print("[red]Failed to analysing requirements[/red]")
            raise RuntimeError("Ollama returned an invalid analysis proposal.") from exc

    def summarize_context(self, context: str, prompt: Prompt) -> str:
        if not context.strip():
            raise ValueError("Cannot summarize project context without discovery evidence.")

        system_prompt = SUMMARIZE_DISCOVERY_CONTEXT_PROMPT.format(user_request=prompt.value,
                                                                  discovery_evidence=context, )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "Summarize the supplied evidence according to the "
                    "instructions and JSON schema."
                ),
            },
        ]

        with self._console.status("[cyan]Summarizing context...[/cyan]", spinner="bouncingBar", ):
            response = self._client.chat(
                model=self._model,
                messages=messages,
                format=SUMMARIZE_DISCOVERY_CONTEXT_SCHEMA,
                options={"temperature": 0},
            )

        # Ollama versions may expose the message as an object or mapping.
        message = response.message
        content = (message.content if hasattr(message, "content") else message["content"])

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Discovery summarizer returned an empty response.")

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Discovery summarizer returned invalid JSON.") from exc

        # self._validate_discovery_context(data)

        self._console.print("[green bold]Summarized context successfully[/green bold]")

        # Return normalized JSON for the existing planner interface.
        return json.dumps(data, indent=2, ensure_ascii=False)
