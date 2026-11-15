from agent.application.port.llm_client import LLMClient
from agent.domain.agent.analysis_agent import AnalysisAgent
from agent.domain.entity.message import Message
from agent.domain.vo.task_analysis import AnalysisResult
from agent.infrastructure.agents.llm_agent import LLMAgent
from agent.infrastructure.agents.parser.analysis_result_parser import AnalysisResultParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class AnalysisAgentImpl(LLMAgent, AnalysisAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, load_prompt("analysis_agent"))
        self._parser = AnalysisResultParser()

    def execute(self, context: tuple[Message, ...]) -> AnalysisResult:
        return self._ask_json(context, self._parser)
