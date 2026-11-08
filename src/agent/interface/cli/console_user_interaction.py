from agent.application.port.user_interaction import UserInteraction


class CLIUserInteraction(UserInteraction):
    def ask(self, question: str) -> str:
        answer = input(f"\n? {question}\n> ").strip()
        return answer or "no answer given, use a common default"
