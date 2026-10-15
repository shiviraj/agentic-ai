from __future__ import annotations
from collections.abc import Callable
from prompt_toolkit import PromptSession
from rich.console import Console
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.vo.prompt import Prompt
from agent.interface.cli.plan_display import display_plan
from agent.interface.cli.plan_execution import (execute_plan as execute_plan_with_feedback)
from agent.interface.cli.prompt_input import (GOODBYE, create_prompt_session, user_prompt)

PROMPT_INSTRUCTIONS = """\
Senior Backend Engineer Agent

Commands:
  .exit       Exit the application
  Option+Enter  Insert a new line
  Enter       Submit the prompt

How can I help you?
"""


def process_user_request(
        prompt: Prompt,
        process_prompt: Callable[[Prompt], ImplementationPlan],
        execute_plan: Callable[[ImplementationPlan], None],
        console: Console,
) -> None:
    with console.status("[cyan]Generating implementation plan...[/cyan]", spinner="dots", ):
        plan = process_prompt(prompt)
    display_plan(plan, console)
    execute_plan_with_feedback(plan, execute_plan, console)


def run_cli(
        process_prompt: Callable[[Prompt], ImplementationPlan],
        execute_plan: Callable[[ImplementationPlan], None],
) -> None:
    console = Console()
    session: PromptSession[str] = create_prompt_session()
    console.print(PROMPT_INSTRUCTIONS, style="cyan")

    try:
        while True:
            should_exit, prompt = user_prompt(session)
            if should_exit:
                console.print(GOODBYE, style="dim")
                break
            if not prompt:
                continue
            try:
                process_user_request(Prompt(prompt), process_prompt, execute_plan, console)
            except KeyboardInterrupt:
                console.print("\n[yellow]Request interrupted.[/yellow]\n")
            except Exception:
                console.print("\n[bold red]Failed to process the request.[/bold red]")
                console.print("[dim]Check the application logs for details.[/dim]\n")

    except KeyboardInterrupt:
        pass
