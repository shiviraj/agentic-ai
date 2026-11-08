"""Manual check: does the model remember what we said earlier?

Run:  OLLAMA_MODEL=llama3.1:8b python scripts/smoke_llm.py
"""

import os

from agent.domain.llm.message import Message, Role
from agent.infrastructure.llm.llm_client_impl import LLMClientImpl


def main() -> None:
    model = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
    llm = LLMClientImpl(model=model)

    history = [
        Message(Role.SYSTEM, "You are a short, helpful assistant."),
        Message(Role.USER, "My name is Shivam. Just say OK."),
    ]
    first = llm.chat(history)
    print("1st answer:", first)

    history.append(Message(Role.ASSISTANT, first))
    history.append(Message(Role.USER, "What is my name?"))
    second = llm.chat(history)
    print("2nd answer:", second)

    print("\nJSON mode test:")
    json_answer = llm.chat(
        [Message(Role.USER, 'Reply with JSON like {"ok": true}')],
        json_mode=True,
    )
    print(json_answer)


if __name__ == "__main__":
    main()
