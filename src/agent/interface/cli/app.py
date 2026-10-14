from __future__ import annotations

from collections.abc import Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from rich.console import Console

from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.vo.prompt import Prompt

EXIT_COMMAND = ".exit"

PROMPT_INSTRUCTIONS = """\
Senior Backend Engineer Agent

Commands:
  .exit       Exit the application
  Option+Enter  Insert a new line
  Enter       Submit the prompt

How can I help you?
"""

GOODBYE = "Goodbye!!"


def create_key_bindings() -> KeyBindings:
    """Configure Enter to submit and Escape+Enter to insert a newline."""
    bindings = KeyBindings()

    @bindings.add(Keys.Enter)
    def submit_on_enter(event) -> None:
        event.current_buffer.validate_and_handle()

    @bindings.add(Keys.Escape, Keys.Enter)
    def newline_on_alt_enter(event) -> None:
        event.current_buffer.insert_text("\n")

    return bindings


def create_prompt_session() -> PromptSession[str]:
    """Create one reusable interactive prompt session."""
    return PromptSession(multiline=True, key_bindings=create_key_bindings(), history=FileHistory(".agent_history"))


def user_prompt(session: PromptSession[str]) -> tuple[bool, str]:
    try:
        text = session.prompt("> ")
    except (KeyboardInterrupt, EOFError):
        return True, GOODBYE
    prompt = text.strip()
    if prompt == EXIT_COMMAND:
        return True, GOODBYE
    return False, prompt


def display_plan(plan: ImplementationPlan, console: Console) -> None:
    """Present a generated plan without changing domain state."""
    console.print("\n[bold green]Plan generated successfully.[/bold green]")
    console.print(f"Plan ID: {plan.id.value}")
    console.print(f"Status: {plan.status.value}")
    console.print("\n[bold]Implementation steps[/bold]")

    for step in plan.steps:
        console.print(f"  {step.sequence}. {step.title}\n  {step.description}")


def run_cli(process_prompt: Callable[[Prompt], ImplementationPlan]) -> None:
    console = Console()
    session = create_prompt_session()
    console.print(PROMPT_INSTRUCTIONS, style="cyan")
    try:
        while True:
            should_exit, prompt = user_prompt(session)

            if should_exit:
                console.print(prompt, style="dim")
                break

            if not prompt:
                continue

            try:
                with console.status("[cyan]Generating implementation plan...[/cyan]", spinner="dots"):
                    result = process_prompt(Prompt(prompt))

                display_plan(result, console)

            except KeyboardInterrupt:
                console.print("\n[yellow]Request interrupted.[/yellow]\n")

            except Exception:
                console.print("\n[bold red]Failed to process the request.[/bold red]")
                console.print("[dim]Check the application logs for details.[/dim]\n")

    except KeyboardInterrupt:
        pass
