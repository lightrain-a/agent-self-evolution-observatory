from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "e2-r17-typed-state-consumer-v1"
EXPECTED_KEYS = {
    "scope",
    "verification_rule",
    "tool_recovery_rule",
    "completion_gate",
    "local_fact_policy",
    "reusable_primitives",
}
ALLOWED_PRIMITIVES = {"VERIFY_OUTPUT", "RECOVER_TOOL_ERROR", "COMPLETE_WORKFLOW"}


class TypedStateConsumerError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TypedStateConsumerError(message)


def compile_consumer_directives(state: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(state, dict), "typed state must be one object")
    _require(set(state) == EXPECTED_KEYS, "typed state keys drifted")

    scope = state["scope"]
    verification = state["verification_rule"]
    recovery = state["tool_recovery_rule"]
    completion = state["completion_gate"]
    local_policy = state["local_fact_policy"]
    primitives = state["reusable_primitives"]

    _require(scope in {"cross_workbook", "same_instance_only"}, "unknown scope")
    _require(verification in {"save_reload_verify", "none"}, "unknown verification_rule")
    _require(
        recovery in {"refresh_metadata_repair_args_retry_once", "blind_retry", "none"},
        "unknown tool_recovery_rule",
    )
    _require(
        completion in {"write_save_reload_verify", "write_only", "save_only"},
        "unknown completion_gate",
    )
    _require(
        local_policy in {"exclude_from_cross_workbook_state", "carry_forward"},
        "unknown local_fact_policy",
    )
    _require(isinstance(primitives, list), "reusable_primitives must be a list")
    _require(len(primitives) == len(set(primitives)), "reusable_primitives contains duplicates")
    _require(set(primitives) <= ALLOWED_PRIMITIVES, "unknown reusable primitive")

    if scope == "cross_workbook":
        _require(
            local_policy == "exclude_from_cross_workbook_state",
            "cross_workbook state cannot carry forward instance-local facts",
        )
    if local_policy == "carry_forward":
        _require(scope == "same_instance_only", "carry_forward requires same_instance_only scope")

    _require(
        (verification != "none") == ("VERIFY_OUTPUT" in primitives),
        "verification rule and VERIFY_OUTPUT primitive disagree",
    )
    _require(
        (recovery != "none") == ("RECOVER_TOOL_ERROR" in primitives),
        "recovery rule and RECOVER_TOOL_ERROR primitive disagree",
    )
    _require(
        completion == "write_save_reload_verify" if "COMPLETE_WORKFLOW" in primitives else completion != "write_save_reload_verify",
        "completion gate and COMPLETE_WORKFLOW primitive disagree",
    )

    verify_action = "RELOAD_VERIFY" if verification == "save_reload_verify" else "UNKNOWN"
    if recovery == "refresh_metadata_repair_args_retry_once":
        recovery_action = "REFRESH_REPAIR_RETRY_ONCE"
    elif recovery == "blind_retry":
        recovery_action = "RETRY_UNCHANGED"
    else:
        recovery_action = "UNKNOWN"

    if completion == "write_save_reload_verify":
        completion_action = "NOT_COMPLETE"
    elif completion in {"write_only", "save_only"}:
        completion_action = "COMPLETE"
    else:  # guarded above; retained for fail-closed clarity
        raise TypedStateConsumerError("unmapped completion_gate")

    if scope == "cross_workbook":
        local_action = "DO_NOT_TRANSFER"
    elif local_policy == "carry_forward":
        local_action = "TRANSFER"
    else:
        local_action = "UNKNOWN"

    return {
        "consumer_schema": SCHEMA_VERSION,
        "scope": "CROSS_WORKBOOK" if scope == "cross_workbook" else "SAME_INSTANCE_ONLY",
        "verify_after_save": verify_action,
        "stale_sheet_failure": recovery_action,
        "completion_before_reload": completion_action,
        "cross_workbook_local_fact": local_action,
        "reusable_primitives": sorted(primitives),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    state = json.loads(args.input.read_text(encoding="utf-8"))
    directives = compile_consumer_directives(state)
    args.output.write_text(json.dumps(directives, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
