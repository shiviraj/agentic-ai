from abc import abstractmethod

from agent.application.service.dto.analyze_query_result import AnalyzeQueryResult
from agent.domain.aggregate.conversation import Conversation
from agent.domain.tool.tool import ToolDefinition


class QueryAgent:
    @abstractmethod
    def run(self, conversation: Conversation, tools: list[ToolDefinition]) -> AnalyzeQueryResult: ...
