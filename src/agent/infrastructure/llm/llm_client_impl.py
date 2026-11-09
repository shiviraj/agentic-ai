from collections.abc import Sequence
from typing import Any

import httpx
import ollama

from agent.application.port.llm_client import LLMClient
from agent.domain.errors import LlmUnavailableError
from agent.domain.llm.message import Message


class LLMClientImpl(LLMClient):
    def __init__(
        self,
        client: Any,  # lets tests pass a fake client
        model: str,
        num_ctx: int = 8192,
        temperature: float = 0.2,
    ) -> None:
        self._model = model
        self._num_ctx = num_ctx
        self._temperature = temperature
        self._client = client

    def chat(self, messages: Sequence[Message], schema: dict | None = None) -> str:
        if not messages:
            raise ValueError("chat() needs at least one message")

        payload = [{"role": m.role.value, "content": m.content} for m in messages]

        try:
            response = self._client.chat(
                model=self._model,
                messages=payload,
                options={
                    "num_ctx": self._num_ctx,
                    "temperature": self._temperature,
                },
                format=schema,
            )
        except (ollama.ResponseError, ConnectionError, httpx.HTTPError) as e:
            raise LlmUnavailableError(f"Ollama call failed for model '{self._model}': {e}") from e

        content = response.message.content
        if not content or not content.strip():
            raise LlmUnavailableError(f"Model '{self._model}' returned an empty answer")
        return content

    def tool(self, messages: Sequence[Message], tools: list[dict[str, Any]]) -> str:
        if not messages:
            raise ValueError("chat() needs at least one message")

        payload = [{"role": m.role.value, "content": m.content} for m in messages]

        try:
            response = self._client.chat(
                model=self._model,
                messages=payload,
                options={
                    "num_ctx": self._num_ctx,
                    "temperature": self._temperature,
                },
                tools=tools,
            )
        except (ollama.ResponseError, ConnectionError, httpx.HTTPError) as e:
            raise LlmUnavailableError(f"Ollama call failed for model '{self._model}': {e}") from e

        print("======================================")
        print(response)
        print("======================================")
        # content = response.message.content
        # if not content or not content.strip():
        #     raise LlmUnavailableError(f"Model '{self._model}' returned an empty answer")
        return response
