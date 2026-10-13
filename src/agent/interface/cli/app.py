from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

EXIT_COMMAND = '.exit'
MESSAGE = """
Senior Backend Engineer Agent: 
.exit: exit the application.
Option + Enter for new line

How can I help you?
"""

GOODBYE = "Goodbye!!"


def is_exit_command(text: str) -> bool:
    """Return True only when the complete input is the exit command."""
    return text.strip() == EXIT_COMMAND


def create_key_bindings() -> KeyBindings:
    bindings = KeyBindings()

    @bindings.add(Keys.Enter)
    def submit_on_enter(event) -> None:
        event.current_buffer.validate_and_handle()

    @bindings.add(Keys.Escape, Keys.Enter)
    def newline_on_alt_enter(event) -> None:
        event.current_buffer.insert_text("\n")

    return bindings


def prompt_instruction() -> None:
    print(MESSAGE)


def user_prompt() -> tuple[bool, str]:
    session: PromptSession[str] = PromptSession(multiline=True, key_bindings=create_key_bindings())

    try:
        text = session.prompt(">")
    except KeyboardInterrupt, EOFError:
        return True, GOODBYE

    if is_exit_command(text):
        return True, GOODBYE

    return False, text.strip()
