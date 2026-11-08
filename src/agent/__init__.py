import os

from ollama import Client
from prompt_toolkit import PromptSession

from agent.application.manager.manager_service import ManagerService
from agent.application.manager.retry_policy import RetryPolicy
from agent.domain.task.task import Task
from agent.domain.task.task_id import TaskId
from agent.infrastructure.agents.task_planner_agent import TaskPlannerAgent
from agent.infrastructure.llm.llm_client_impl import LLMClientImpl
from agent.infrastructure.persistence.task_repository import InMemoryTaskRepository
from agent.infrastructure.prompt import PROMPT_INSTRUCTIONS
from agent.interface.cli.console_user_interaction import CLIUserInteraction
from agent.interface.cli.prompt_input import create_prompt_session, user_prompt
from agent.shared.logger.logger import Logger


def main() -> None:
    logger = Logger("Main")
    model = os.getenv("MODEL", "llama3.2:latest")
    host = os.getenv("API_URL", "http://localhost:11434")
    timeout = int(os.getenv("TIMEOUT", "60"))

    client = Client(host=host, timeout=timeout)
    llm_client = LLMClientImpl(client=client, model=model)

    session: PromptSession[str] = create_prompt_session()
    logger.info(PROMPT_INSTRUCTIONS, "cyan")

    manager_service = ManagerService(
        agents=[TaskPlannerAgent(llm=llm_client)],
        repository=InMemoryTaskRepository(),
        user=CLIUserInteraction(),
        policy=RetryPolicy(),
    )

    try:
        while True:
            should_exit, prompt = user_prompt(session)
            if should_exit:
                logger.info(prompt.value, "dim")
                break
            if not prompt:
                continue
            try:
                task = Task(id=TaskId.generate(), prompt=prompt)
                manager_service.run(task)
            except KeyboardInterrupt:
                logger.info("Request interrupted.", "yellow")
            except Exception as exc:
                logger.info(f"Failed to process the request. {exc}", "bold red")

    except KeyboardInterrupt:
        pass
