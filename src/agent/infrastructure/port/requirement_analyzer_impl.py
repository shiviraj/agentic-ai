import json
from typing import cast

from ollama import Client

from agent.application.port.requirement_analyzer import RequirementAnalyzer
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult
from agent.infrastructure.prompt import ANALYSE_REQUIREMENT_PROMPT
from agent.infrastructure.schema import ANALYSIS_SCHEMA
from agent.shared.logger.Logger import Logger


class RequirementAnalyzerImpl(RequirementAnalyzer):
    def __init__(self, client: Client, model: str) -> None:
        self._client = client
        self._model = model
        self._logger = Logger('RequirementAnalyzerImpl')

    def analyze(self, prompt: Prompt) -> RequirementAnalysisResult:
        messages = [
            {"role": "system", "content": ANALYSE_REQUIREMENT_PROMPT},
            {"role": "user", "content": prompt.value}
        ]
        try:
            with self._logger.status("Analysing requirements...", "bouncingBar", "cyan"):
                response = self._client.chat(
                    model=self._model,
                    messages=messages,
                    format=ANALYSIS_SCHEMA,
                    options={"temperature": 0}
                )
            result = json.loads(response.message["content"])
            context_request = result["context_request"]
            require_context = cast(bool, result["require_context"])

            self._logger.log("Analysed requirements successfully", "green bold")
            return RequirementAnalysisResult(context_request=context_request, require_context=require_context)
        except (KeyError, TypeError, ValueError) as exc:
            self._logger.log("Failed to analysing requirements", "red")
            raise RuntimeError("Ollama returned an invalid analysis proposal.") from exc
