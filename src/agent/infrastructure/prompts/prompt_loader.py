from pathlib import Path

_PROMPT_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """Read prompts/<name>.md as text."""
    path = _PROMPT_DIR / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()
