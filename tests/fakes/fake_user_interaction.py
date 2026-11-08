from agent.application.port.user_interaction import UserInteraction


class FakeUserInteraction(UserInteraction):
    def __init__(self, answers: list[str] | None = None) -> None:
        self._answers = list(answers or [])
        self.asked: list[str] = []

    def ask(self, question: str) -> str:
        self.asked.append(question)
        return self._answers.pop(0) if self._answers else "default answer"
