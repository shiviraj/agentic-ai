import json
from ollama import Client

from agent.application.port.planner import Planner
from agent.domain.vo.plan_proposal import PlanProposal, ProposedPlanStep
from agent.domain.vo.prompt import Prompt
from agent.infrastructure.prompt import PLAN_PROMPT
from agent.infrastructure.schema import PLAN_SCHEMA


class OllamaPlanner(Planner):
    """Infrastructure adapter implementing the Planner application port."""

    def __init__(self, client: Client, model: str) -> None:
        self._client = client
        self._model = model

    def generate_plan(self, prompt: Prompt) -> PlanProposal:
        message = [
            {"role": "system", "content": PLAN_PROMPT, },
            {"role": "user", "content": prompt.value},
        ]

        try:
            response = self._client.chat(
                model=self._model,
                messages=message,
                format=PLAN_SCHEMA,
                options={"temperature": 0}
            )
            content = response.message["content"]
            data = json.loads(content)
            raw_steps = data["steps"]

            if not isinstance(raw_steps, list) or not raw_steps:
                raise ValueError("Expected at least one plan step")

            steps = []
            for item in raw_steps:
                if not isinstance(item, dict):
                    raise ValueError("Each step must be an object")

                description = item.get("description")
                title = item.get("title")
                if (not isinstance(description, str) or not description.strip()
                        or not isinstance(title, str) or not title.strip()):
                    raise ValueError("Step descriptions and title cannot be empty")

                steps.append(ProposedPlanStep(description=description.strip(), title=title.strip()))

            return PlanProposal(steps=tuple(steps))

        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("Ollama returned an invalid plan proposal.") from exc
