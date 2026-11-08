"""Manual check of the Task Analyser with the real model.

Run:  OLLAMA_MODEL=llama3.1:8b python scripts/try_analyser.py "implement health check endpoint"
"""

import os
import sys

from agent.domain.agent.agent_result import ResultStatus
from agent.domain.task.task import Task
from agent.domain.task.task_id import TaskId
from agent.infrastructure.agents.task_analyser_agent import TaskAnalyserAgent
from agent.infrastructure.llm.llm_client_impl import LLMClientImpl


def main() -> None:
    description = " ".join(sys.argv[1:]) or "implement health check endpoint"
    llm = LLMClientImpl(model=os.environ.get("OLLAMA_MODEL", "qwen3:4b"))
    agent = TaskAnalyserAgent(llm)
    task = Task(id=TaskId.generate(), prompt=description)

    for round_number in range(1, 4):  # at most 3 rounds of questions
        result = agent.run(task)
        print(f"\n--- round {round_number}: {result.status.value} ---")

        if result.status == ResultStatus.DONE:
            print("Requirements:\n" + result.output)
            return
        if result.status == ResultStatus.FAILED:
            print("Failed:", result.output)
            return

        for question in result.questions:
            answer = input(f"{question}\n> ")
            task.add_clarification(question, answer)

    print("Still not clear after 3 rounds.")


if __name__ == "__main__":
    main()
