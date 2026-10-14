from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreatePlanCommand:
    task_id: UUID
    prompt: str
