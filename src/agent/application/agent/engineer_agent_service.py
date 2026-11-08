from agent.application.agent.dto.analyze_result import RequestCategory
from agent.application.agent.query_agent import QueryAgent
from agent.application.port.engineer_agent import EngineerAgent
from agent.domain.vo.user_request import UserRequest
from agent.shared.logger.logger import Logger


class EngineerAgentService:
    def __init__(self, agent: EngineerAgent, query_agent: QueryAgent):
        self._agent = agent
        self._query_agent = query_agent
        self._logger = Logger("EngineerAgentService")

    def run(self, request: UserRequest) -> str:
        with self._logger.status(message="Analyzing user request"):
            analyze_result = self._agent.analyze(request)
        self._logger.info("User request analysis completed")
        if analyze_result.category == RequestCategory.CONVERSATION:
            return analyze_result.response
        return analyze_result.response
