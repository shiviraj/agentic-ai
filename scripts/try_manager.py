"""Run the Manager with the real Analyser only.

Run:  OLLAMA_MODEL=llama3.1:8b python scripts/try_manager.py "implement health check endpoint"
"""

import logging
import os
import sys

from agent.application.manager.manager_service import ManagerService
from agent.domain.task.task import Task
from agent.domain.task.task_id import TaskId
from agent.infrastructure.agents.task_analyser_agent import TaskAnalyserAgent
from agent.infrastructure.persistence.task_repository import (
    InMemoryTaskRepository,
)
from agent.interface.cli.console_user_interaction import CLIUserInteraction

from agent.infrastructure.llm.llm_client_impl import LLMClientImpl


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    description = " ".join(sys.argv[1:]) or "implement health check endpoint"
    llm = LLMClientImpl(model=os.environ.get("OLLAMA_MODEL", "qwen3:4b"))

    manager = ManagerService(
        agents=[TaskAnalyserAgent(llm)],
        repository=InMemoryTaskRepository(),
        user=CLIUserInteraction(),
    )

    task = manager.run(Task(id=TaskId.generate(), prompt=description))

    print("\n=== result ===")
    print("status:      ", task.status.value)
    print("failure:     ", task.failure_reason)
    print("requirements:\n" + (task.requirements or "(none)"))


if __name__ == "__main__":
    main()
