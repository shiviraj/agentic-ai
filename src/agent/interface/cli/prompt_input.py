from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from agent.domain.vo.prompt import Prompt

EXIT_COMMAND = ".exit"
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


def user_prompt(session: PromptSession[str]) -> tuple[bool, Prompt]:
    try:
        text = session.prompt("> ")
    except (KeyboardInterrupt, EOFError):
        return True, Prompt(GOODBYE)
    if text.strip() == EXIT_COMMAND:
        return True, Prompt(GOODBYE)
    return False, Prompt(text.strip())
