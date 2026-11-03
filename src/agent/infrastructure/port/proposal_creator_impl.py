import json

from ollama import Client

from agent.application.port.proposal_creator import ProposalCreator
from agent.domain.entity.plan_step import PlanStep
from agent.domain.vo.project_context import ProjectContext
from agent.domain.vo.prompt import Prompt
from agent.infrastructure.prompt import PLAN_PROMPT
from agent.infrastructure.schema import PLAN_SCHEMA
from agent.shared.logger.Logger import Logger


class ProposalCreatorImpl(ProposalCreator):
    def __init__(self, client: Client, model: str) -> None:
        self._client = client
        self._model = model
        self._logger = Logger('ProposalCreatorImpl')

    def create(self, prompt: Prompt, context: ProjectContext | None) -> list[PlanStep]:
        context_content = self._serialize_context(context)
        user_content = (
            f"Original requirement:\n{prompt.value}\n\n"
            f"Discovered project context:\n{context_content}\n\n"
            "Generate the implementation plan for the original requirement."
        )
        messages = [
            {"role": "system", "content": PLAN_PROMPT},
            {"role": "user", "content": user_content},
        ]
        with self._logger.status("Generating implementation plan...", "bouncingBar"):
            response = self._client.chat(
                model=self._model,
                messages=messages,
                format=PLAN_SCHEMA,
                options={"temperature": 0},
            )
        content = response.message["content"]
        self._logger.debug(f"Proposal creator llm response: {content}")
        plan_data = json.loads(content)

        steps_data = plan_data.get("steps") if isinstance(plan_data, dict) else None
        if not isinstance(steps_data, list) or not steps_data:
            self._logger.error("The implementation plan must contain a non-empty steps array.")
            raise RuntimeError("The implementation plan must contain a non-empty steps array.")

        try:
            proposed_steps = [
                PlanStep.create(step_data["title"], step_data["description"], index + 1)
                for index, step_data in enumerate(steps_data)
            ]
        except (TypeError, ValueError) as exc:
            self._logger.error(f"The implementation plan contains invalid step data. {exc}")
            raise RuntimeError(f"The implementation plan contains invalid step data. {exc}")
        return proposed_steps

    @staticmethod
    def _serialize_context(context: ProjectContext | None) -> str:
        if context is None:
            return "No project context was discovered."

        return json.dumps(
            {
                "files": [
                    {
                        "path": file.path,
                        "purpose": file.purpose,
                        "relevant_content": file.relevant_content,
                    }
                    for file in context.files
                ],
                "dependencies": context.dependencies,
                "conventions": context.conventions,
                "findings": context.findings,
                "unresolved_questions": context.unresolved_questions,
            },
            indent=2,
            ensure_ascii=False,
        )
