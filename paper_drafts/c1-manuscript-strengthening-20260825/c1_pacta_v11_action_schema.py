from __future__ import annotations

import hashlib
import json

# Frozen native Browser-Use action inventory for the C1 Shopping substrate.
# This object contains affordances only: no policy, memory, reasoning, task,
# response-envelope, current_state, or next_goal instructions.
TOOL_SPEC = {
    "click_element": {
        "arguments": {
            "index": {"type": "integer", "minimum": 0}
        },
        "required": ["index"],
        "additionalProperties": False,
    },
    "done": {
        "arguments": {
            "success": {"type": "boolean"},
            "text": {"type": "string", "minLength": 1},
        },
        "required": ["success", "text"],
        "additionalProperties": False,
    },
    "extract_content": {
        "arguments": {
            "goal": {"type": "string", "minLength": 1}
        },
        "required": ["goal"],
        "additionalProperties": False,
    },
    "go_back": {
        "arguments": {},
        "required": [],
        "additionalProperties": False,
    },
    "go_to_url": {
        "arguments": {
            "url": {"type": "string", "format": "uri"}
        },
        "required": ["url"],
        "additionalProperties": False,
    },
    "input_text": {
        "arguments": {
            "index": {"type": "integer", "minimum": 0},
            "text": {"type": "string"},
        },
        "required": ["index", "text"],
        "additionalProperties": False,
    },
    "scroll_down": {
        "arguments": {
            "amount": {"type": "integer", "minimum": 1}
        },
        "required": [],
        "additionalProperties": False,
    },
    "select_dropdown_option": {
        "arguments": {
            "index": {"type": "integer", "minimum": 0},
            "text": {"type": "string"},
        },
        "required": ["index", "text"],
        "additionalProperties": False,
    },
    "send_keys": {
        "arguments": {
            "keys": {"type": "string", "minLength": 1}
        },
        "required": ["keys"],
        "additionalProperties": False,
    },
    "switch_tab": {
        "arguments": {
            "page_id": {"type": "integer", "minimum": 0}
        },
        "required": ["page_id"],
        "additionalProperties": False,
    },
    "wait": {
        "arguments": {
            "seconds": {"type": "integer", "minimum": 1}
        },
        "required": ["seconds"],
        "additionalProperties": False,
    },
}

REQUIRED_NATIVE_MARKERS = (
    "You are an AI agent designed to automate browser tasks.",
    '"action":[{"one_action_name": {// action-specific parameter}}',
    '"input_text": {"index": 1, "text": "username"}',
    '"click_element": {"index": 3}',
    '"go_to_url": {"url": "https://example.com"}',
    '"extract_content": {"goal": "extract the names"}',
    "Use scroll to find elements",
    "use wait action",
    "Use the done action",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_schema() -> str:
    return json.dumps(
        {"tools": TOOL_SPEC},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def extract_minimal_action_schema(system_instruction: str) -> str:
    if not isinstance(system_instruction, str) or not system_instruction.strip():
        raise ValueError("empty native system instruction")
    missing = [marker for marker in REQUIRED_NATIVE_MARKERS if marker not in system_instruction]
    if missing:
        raise ValueError(f"native action protocol marker drift: {missing}")
    schema = canonical_schema()
    forbidden = (
        "current_state",
        "next_goal",
        "REUSABLE MEMORY",
        "ULTIMATE TASK",
        "evaluation_previous_goal",
        "You are an AI agent",
        "Your responses must",
    )
    leaked = [text for text in forbidden if text in schema]
    if leaked:
        raise ValueError(f"non-affordance prose leaked into action schema: {leaked}")
    return schema


def validate_action_object(action_object: object, schema_text: str) -> None:
    if schema_text != canonical_schema():
        raise ValueError("action schema drift")
    if not isinstance(action_object, dict) or len(action_object) != 1:
        raise ValueError("action object must contain exactly one tool")
    tool_name = next(iter(action_object))
    if tool_name not in TOOL_SPEC:
        raise ValueError(f"tool absent from extracted schema: {tool_name}")
    arguments = action_object[tool_name]
    if not isinstance(arguments, dict):
        raise ValueError("tool arguments must be an object")
    spec = TOOL_SPEC[tool_name]
    unknown = set(arguments) - set(spec["arguments"])
    missing = set(spec["required"]) - set(arguments)
    if unknown:
        raise ValueError(f"unknown arguments for {tool_name}: {sorted(unknown)}")
    if missing:
        raise ValueError(f"missing arguments for {tool_name}: {sorted(missing)}")
    for name, value in arguments.items():
        rule = spec["arguments"][name]
        expected = rule["type"]
        if expected == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
            raise ValueError(f"{tool_name}.{name} must be integer")
        if expected == "boolean" and not isinstance(value, bool):
            raise ValueError(f"{tool_name}.{name} must be boolean")
        if expected == "string" and not isinstance(value, str):
            raise ValueError(f"{tool_name}.{name} must be string")
        if "minimum" in rule and value < rule["minimum"]:
            raise ValueError(f"{tool_name}.{name} below minimum")
        if "minLength" in rule and len(value) < rule["minLength"]:
            raise ValueError(f"{tool_name}.{name} shorter than minimum")
