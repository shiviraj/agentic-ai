class PolicyViolationError(Exception):
    def __init__(self, message: str, errors: list[str]) -> None:
        self.message = message
        self.errors = errors
