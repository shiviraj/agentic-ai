from agent.application.port.requirement_analyzer import RequirementAnalyzer
from agent.domain.policy.requirement_analysis_policy import RequirementAnalysisPolicy
from agent.domain.vo.prompt import Prompt
from agent.domain.vo.requirement_analysis_result import RequirementAnalysisResult


class AnalyzeRequirementService:
    def __init__(self, requirement_analyzer: RequirementAnalyzer,
                 requirement_analysis_policy: RequirementAnalysisPolicy) -> None:
        self._requirement_analyzer = requirement_analyzer
        self._requirement_analysis_policy = requirement_analysis_policy

    def analyze(self, prompt: Prompt) -> RequirementAnalysisResult:
        analysis_result = self._requirement_analyzer.analyze(prompt)
        self._requirement_analysis_policy.evaluate(analysis_result).enforce("Requirement Analysis failed")
        return analysis_result
