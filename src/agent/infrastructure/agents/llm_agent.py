from typing import TypeVar

from pydantic import ValidationError

from agent.application.port.llm_client import LLMClient
from agent.domain.agent.agent import Agent
from agent.domain.errors import InvalidAgentOutputError
from agent.domain.llm.message import Message, Role
from agent.infrastructure.agents.parser.output_parser import OutputParser

T = TypeVar("T")


class LLMAgent(Agent):
    """Base class for agents that think by calling the LLM and expect JSON back."""

    def __init__(self, llm: LLMClient, system_prompt: str, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self._llm = llm
        self._system_prompt = system_prompt
        self._max_attempts = max_attempts

    def _ask_json(self, user_content: str, parser: OutputParser[T]) -> T:
        """Ask the LLM, check the answer, and retry with feedback if it is bad.

        `validate` turns the parsed dict into a result, or raises InvalidAgentOutputError.
        """
        messages = [
            Message(Role.SYSTEM, self._system_prompt),
            Message(Role.USER, user_content),
        ]
        last_error: InvalidAgentOutputError | None = None

        for _ in range(self._max_attempts):
            reply = self._llm.chat(messages, parser.schema)
            try:
                return parser.parse(reply)
            except InvalidAgentOutputError as e:
                last_error = e
                # Show the model its own bad answer and what was wrong with it
                messages.append(Message(Role.ASSISTANT, reply))
                messages.append(
                    Message(
                        Role.USER,
                        f"Your last answer was not valid: {e}. Reply again with ONLY the corrected JSON object.",
                    )
                )

        raise InvalidAgentOutputError(f"no valid answer after {self._max_attempts} attempts: {last_error}")


def format_errors(e: ValidationError) -> str:
    return "; ".join(f"{'.'.join(str(p) for p in err['loc']) or 'answer'}: {err['msg']}" for err in e.errors())
