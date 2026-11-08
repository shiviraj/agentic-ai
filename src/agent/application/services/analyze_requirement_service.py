from agent.application.port.requirement_analyzer import RequirementAnalyzer
from agent.domain.policy.requirement_analysis_policy import RequirementAnalysisPolicy
from agent.domain.vo.user_request import Prompt
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult
from agent.shared.logger.logger import Logger


class AnalyzeRequirementService:
    def __init__(
        self, requirement_analyzer: RequirementAnalyzer, requirement_analysis_policy: RequirementAnalysisPolicy
    ) -> None:
        self._requirement_analyzer = requirement_analyzer
        self._requirement_analysis_policy = requirement_analysis_policy
        self._logger = Logger("AnalyzeRequirementService")

    def analyze(self, prompt: Prompt) -> RequirementAnalysisResult:
        self._logger.debug("Analyzing Requirement started")
        analysis_result = self._requirement_analyzer.analyze(prompt)
        self._logger.debug(f"Analyzing Requirement result: {analysis_result}")
        # self._requirement_analysis_policy.evaluate(analysis_result).enforce("Requirement Analysis failed")
        self._logger.info("Analysed requirements successfully", "green bold")
        return analysis_result
