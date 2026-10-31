from __future__ import annotations
from collections.abc import Callable
from prompt_toolkit import PromptSession
from rich.console import Console
from agent.domain.aggregate.implementation_plan import ImplementationPlan
from agent.domain.vo.prompt import Prompt
from agent.interface.cli.display_plan import display_plan
from agent.interface.cli.plan_execution import (execute_plan as execute_plan_with_feedback)
from agent.interface.cli.prompt_input import (GOODBYE, create_prompt_session, user_prompt)

PROMPT_INSTRUCTIONS = """\
Backend Engineer Agent

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
    plan = process_prompt(prompt)
    display_plan(plan, console)
    execute_plan_with_feedback(plan, execute_plan, console)

