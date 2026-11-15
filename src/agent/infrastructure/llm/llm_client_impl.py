from collections.abc import Sequence
from typing import Any

import httpx
import ollama
from ollama import Client as OllamaClient

from agent.application.port.llm_client import LLMClient
from agent.domain.entity.message import Message
from agent.domain.errors import LlmUnavailableError
from agent.domain.tool.tool import ToolCall, ToolDefinition
from agent.domain.vo.tool_response import ToolResponse
from agent.infrastructure.llm.utils import to_ollama_payload, to_ollama_tools


class LLMClientImpl(LLMClient):
    def __init__(
        self,
        client: OllamaClient,
        model: str,
        num_ctx: int = 8192,
        temperature: float = 0.2,
    ) -> None:
        self._model = model
        self._num_ctx = num_ctx
        self._temperature = temperature
        self._client = client

    def chat(self, messages: Sequence[Message], schema: dict[str, Any] | None = None) -> str:
        try:
            response = self._client.chat(
                model=self._model,
                messages=to_ollama_payload(messages),
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

    def tool(self, messages: Sequence[Message], tools: Sequence[ToolDefinition]) -> ToolResponse:
        try:
            response = self._client.chat(
                model=self._model,
                messages=to_ollama_payload(messages),
                options={
                    "num_ctx": self._num_ctx,
                    "temperature": self._temperature,
                },
                tools=to_ollama_tools(tools),
            )
        except (ollama.ResponseError, ConnectionError, httpx.HTTPError) as e:
            raise LlmUnavailableError(f"Ollama call failed for model '{self._model}': {e}") from e

        content = response.message.content or ""
        tool_calls = [
            ToolCall(
                provider=tool_call.function.name.split("::")[0],
                name=tool_call.function.name.split("::")[1],
                arguments=tool_call.function.arguments,
            )
            for tool_call in response.message.tool_calls or []
        ]
        return ToolResponse(content=content, tools=tool_calls, finished=False)
