import os

from ollama import Client
from prompt_toolkit import PromptSession
from rich.console import Console

from agent.application.agent.engineer_agent_service import EngineerAgentService
from agent.application.agent.query_agent import QueryAgent
from agent.infrastructure.agents.engineer_agent_impl import EngineerAgentImpl
from agent.infrastructure.llm.llm_client_impl import LLMClientImpl
from agent.infrastructure.prompt import PROMPT_INSTRUCTIONS
from agent.interface.cli.user_input import create_prompt_session, user_request
from agent.shared.logger.logger import Logger


def main() -> None:
    logger = Logger("Main")
    model = os.getenv("MODEL", "llama3.2:latest")
    host = os.getenv("API_URL", "http://localhost:11434")
    timeout = int(os.getenv("TIMEOUT", "60"))

    client = Client(host=host, timeout=timeout)
    llm_client = LLMClientImpl(client=client, model=model)

    session: PromptSession[str] = create_prompt_session()
    console = Console()
    console.print(f"[cyan]{PROMPT_INSTRUCTIONS}[/cyan]")

    query_agent = QueryAgent()
    engineer_agent = EngineerAgentImpl(llm_client=llm_client)

    agent = EngineerAgentService(agent=engineer_agent, query_agent=query_agent)

    try:
        while True:
            try:
                should_exit, request = user_request(session)
            except ValueError as e:
                logger.warn(f"Invalid prompt: {e}")
                continue
            if should_exit:
                logger.info(request.value, "dim")
                break
            try:
                response = agent.run(request)
                console.print(f"Agent:\t{response}\n")
            except KeyboardInterrupt:
                logger.info("Request interrupted.", "yellow")
            except Exception as exc:
                logger.info(f"Failed to process the request. {exc}", "bold red")

    except KeyboardInterrupt:
        pass
