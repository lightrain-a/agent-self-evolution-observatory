from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from c1_pacta_v11_action_schema import TOOL_SPEC


class FirstActionParseError(ValueError):
    pass


@dataclass(frozen=True)
class FirstActionResult:
    action_object: dict[str, Any]
    canonical_action: str
    signature: str
    mode: str


def _signature(action_object: dict[str, Any]) -> str:
    tool_name = next(iter(action_object))
    arguments = action_object[tool_name]
    if tool_name == "click_element":
        return f"click_element:{arguments.get('index')}"
    return tool_name


def _result(action_object: object, mode: str) -> FirstActionResult:
    if not isinstance(action_object, dict) or len(action_object) != 1:
        raise FirstActionParseError("action object must contain exactly one tool")
    tool_name = next(iter(action_object))
    if tool_name not in TOOL_SPEC:
        raise FirstActionParseError(f"tool absent from frozen action schema: {tool_name}")
    if not isinstance(action_object[tool_name], dict):
        raise FirstActionParseError("tool arguments must be a valid JSON object")
    canonical = json.dumps(action_object, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return FirstActionResult(action_object, canonical, _signature(action_object), mode)


def _collect_action_lists(value: object) -> list[list[object]]:
    found: list[list[object]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "action" and isinstance(child, list):
                found.append(child)
            found.extend(_collect_action_lists(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_collect_action_lists(child))
    return found


def _strict(text: str) -> FirstActionResult:
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise FirstActionParseError("full envelope must be a JSON object")
    candidates = _collect_action_lists(payload)
    if len(candidates) != 1:
        raise FirstActionParseError("strict envelope must contain exactly one action list")
    actions = candidates[0]
    if not actions:
        raise FirstActionParseError("action list is empty")
    return _result(actions[0], "strict_full_envelope")


def _string_end(text: str, start: int) -> int:
    if start >= len(text) or text[start] != '"':
        raise FirstActionParseError("string scanner start drift")
    escaped = False
    index = start + 1
    while index < len(text):
        char = text[index]
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            return index + 1
        index += 1
    raise FirstActionParseError("unterminated string")


def _skip_ws(text: str, index: int) -> int:
    while index < len(text) and text[index] in " \t\r\n":
        index += 1
    return index


def _action_array_starts(text: str) -> list[int]:
    starts: list[int] = []
    index = 0
    while index < len(text):
        if text[index] != '"':
            index += 1
            continue
        try:
            end = _string_end(text, index)
        except FirstActionParseError:
            break
        try:
            key = json.loads(text[index:end])
        except json.JSONDecodeError:
            index = end
            continue
        after = _skip_ws(text, end)
        if key == "action" and after < len(text) and text[after] == ":":
            value_start = _skip_ws(text, after + 1)
            if value_start < len(text) and text[value_start] == "[":
                starts.append(value_start)
        index = end
    return starts


def _first_object_slice(text: str, array_start: int) -> str:
    index = _skip_ws(text, array_start + 1)
    if index >= len(text) or text[index] != "{":
        raise FirstActionParseError("first action is absent, non-object, or truncated")
    start = index
    depth = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start:index + 1]
                if depth < 0:
                    raise FirstActionParseError("first action object closes ambiguously")
        index += 1
    raise FirstActionParseError("first action object is truncated")


def parse_first_action(text: str) -> FirstActionResult:
    if not isinstance(text, str) or not text.strip():
        raise FirstActionParseError("empty response")
    stripped = text.strip()
    try:
        return _strict(stripped)
    except (json.JSONDecodeError, FirstActionParseError, TypeError):
        pass

    starts = _action_array_starts(stripped)
    if not starts:
        raise FirstActionParseError("recovery found no action list")
    fragment = _first_object_slice(stripped, starts[0])
    try:
        action_object = json.loads(fragment)
    except json.JSONDecodeError as exc:
        raise FirstActionParseError("first action object is invalid JSON") from exc
    return _result(action_object, "first_action_only_recovery")
