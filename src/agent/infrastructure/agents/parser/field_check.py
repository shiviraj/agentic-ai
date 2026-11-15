from typing import Any

from agent.domain.errors import InvalidAgentResponseError


def require_str(data: dict[str, Any], key: str, min_length: int = 1) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise InvalidAgentResponseError(f"'{key}' must be a string")
    if len(value.strip()) < min_length:
        raise InvalidAgentResponseError(f"'{key}' is too short")
    return value.strip()


def require_bool(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise InvalidAgentResponseError(f"'{key}' must be true or false")
    return value


def require_str_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list):
        raise InvalidAgentResponseError(f"'{key}' must be a list")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise InvalidAgentResponseError(f"'{key}' must only contain non-empty strings")
    return [item.strip() for item in value]
