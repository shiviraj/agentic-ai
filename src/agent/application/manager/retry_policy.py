from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    """All the 'stop, this is going nowhere' limits in one place."""

    max_review_retries: int = 3
    max_qa_retries: int = 3
    max_clarification_rounds: int = 3
    max_total_steps: int = 30

    def __post_init__(self) -> None:
        for name in (
            "max_review_retries",
            "max_qa_retries",
            "max_clarification_rounds",
            "max_total_steps",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must not be negative")

    def limit_for(self, loop_name: str) -> int:
        limits = {
            "review": self.max_review_retries,
            "qa": self.max_qa_retries,
            "clarification": self.max_clarification_rounds,
        }
        return limits[loop_name]
