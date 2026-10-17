import json
from typing import cast

from ollama import Client
from rich.console import Console

from agent.application.port.planner import Planner
from agent.domain.vo.plan_proposal import ProposedPlanStep, RequirementAnalysisResult
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.tool_result import ToolResult
from agent.infrastructure.prompt import PLAN_PROMPT, PROJECT_DISCOVERY_PROMPT, ANALYSE_REQUIREMENT_PROMPT
from agent.infrastructure.schema import PLAN_SCHEMA, ANALYSIS_SCHEMA
from agent.infrastructure.tool_registry import ToolRegistry
from agent.infrastructure.tool_step_executor import MAX_ITERATIONS


class OllamaPlanner(Planner):
    """Infrastructure adapter implementing the Planner application port."""

    def __init__(self, client: Client, model: str, tool_registry: ToolRegistry, console: Console) -> None:
        self._client = client
        self._model = model
        self._tool_registry = tool_registry
        self._tools = tool_registry.get_tools_definition()
        self._console = console

    def create_proposal(self, context: str, prompt: Prompt) -> list[ProposedPlanStep]:
        try:
            user_content = f"Original request:\n{prompt.value}"
            if context:
                user_content += "\n\nExisting project context:\n" f"{context}"
            messages = [{"role": "system", "content": PLAN_PROMPT}, {"role": "user", "content": user_content}]

            with self._console.status("[cyan]Generating plan...[/cyan]", spinner="bouncingBar"):
                response = self._client.chat(
                    model=self._model,
                    messages=messages,
                    format=PLAN_SCHEMA,
                    options={"temperature": 0}
                )
            data = json.loads(response.message["content"])
            raw_steps = data["steps"]

            if not isinstance(raw_steps, list) or not raw_steps:
                raise ValueError("Expected at least one plan step")

            steps = []
            for item in raw_steps:
                if not isinstance(item, dict):
                    raise ValueError("Each step must be an object")

                description = item.get("description")
                title = item.get("title")
                if (not isinstance(description, str) or not description.strip()
                        or not isinstance(title, str) or not title.strip()):
                    raise ValueError("Step descriptions and title cannot be empty")

                steps.append(ProposedPlanStep(description=description.strip(), title=title.strip()))
            self._console.print("[green]Generated plan[/green]")
            return steps

        except (KeyError, TypeError, ValueError) as exc:
            self._console.print("[red]Failed to generating plan[/red]")
            raise RuntimeError("Ollama returned an invalid plan proposal.") from exc

    def discover_context(self, analysis_result: RequirementAnalysisResult, prompt: Prompt) -> str | None:
        if not analysis_result.require_context:
            return None

        try:
            messages = [
                {
                    "role": "system",
                    "content": PROJECT_DISCOVERY_PROMPT.format(
                        context_request=analysis_result.context_request,
                        user_request=prompt.value
                    ),
                },
                {"role": "user", "content": prompt.value},
            ]
            context_parts = []
            for _ in range(MAX_ITERATIONS):
                with self._console.status("[cyan]Discovering context...[/cyan]", spinner="bouncingBar"):
                    response = self._client.chat(
                        model=self._model,
                        tools=self._tools,
                        messages=messages,
                        options={"temperature": 0}
                    )
                message = response.message
                messages.append(cast(dict[str, str], cast(object, message)))
                tool_calls = message.tool_calls or []
                if not tool_calls:
                    if message.content:
                        context_parts.append(f"Discovery findings:\n{message.content}")
                    break

                for tool_call in tool_calls:
                    name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    if not isinstance(arguments, dict):
                        raise RuntimeError(f"Invalid arguments returned for tool: {name}")

                    try:
                        result = self._tool_registry.execute(name, arguments)
                    except Exception:
                        result = ToolResult(success=False, error="Tool execution failed")

                    if result.success:
                        result_content = json.dumps(result.data, default=str, )
                    else:
                        result_content = json.dumps({"error": str(result.error), })

                    messages.append({"role": "tool", "tool_name": name, "content": result_content})

                    context_parts.append(
                        f"Tool: {name}\n"
                        f"Arguments: {json.dumps(arguments, default=str)}\n"
                        f"Result: {result_content}"
                    )
            else:
                raise RuntimeError("Project discovery exceeded the maximum number of iterations.")

            if not context_parts:
                raise RuntimeError("Project context was required, but no useful context was gathered.")

            self._console.print("[green]Discovered context[/green]")
            return "\n\n".join(context_parts)
        except Exception:
            self._console.print("[red]Failed to discover context[/red]")
            raise RuntimeError("Failed to discover context")

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

            self._console.print("[green]Analysed requirements[/green]")
            return RequirementAnalysisResult(context_request=context_request, require_context=require_context)
        except (KeyError, TypeError, ValueError) as exc:
            self._console.print("[red]Failed to analysing requirements[/red]")
            raise RuntimeError("Ollama returned an invalid analysis proposal.") from exc
