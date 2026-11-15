from agent.application.port.llm_client import LLMClient
from agent.domain.agent.dto.engineer_agent_result import EngineerAgentResult
from agent.domain.agent.engineer_agent import EngineerAgent
from agent.domain.entity.message import Message
from agent.infrastructure.agents.llm_agent import LLMAgent
from agent.infrastructure.agents.parser.engineer_agent_result_parser import EngineerAgentResultParser
from agent.infrastructure.prompts.prompt_loader import load_prompt


class EngineerAgentImpl(LLMAgent, EngineerAgent):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client, load_prompt("engineer_agent"))
        self._parser = EngineerAgentResultParser()

    def execute(self, context: tuple[Message, ...]) -> EngineerAgentResult:
        return self._ask_json(context, self._parser)
