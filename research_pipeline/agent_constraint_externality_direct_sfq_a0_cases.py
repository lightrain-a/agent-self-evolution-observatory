from __future__ import annotations

import copy
from datetime import date
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_sq0_v3_cases import (
    choose_content,
    choose_manifest,
    choose_task,
    kv,
)
from research_pipeline.agent_constraint_externality_sq0_v4_cases import (
    _choose_modifier,
    evaluate_case_from_state,
)
from research_pipeline.agent_constraint_externality_sq0_v5_cases import (
    fg_case as v5_fg_case,
    tnf_case as v5_tnf_case,
)


def _replace(obj: Any, pairs: list[tuple[str, str]]) -> Any:
    if isinstance(obj, str):
        for old, new in pairs:
            obj = obj.replace(old, new)
        return obj
    if isinstance(obj, list):
        return [_replace(value, pairs) for value in obj]
    if isinstance(obj, dict):
        return {key: _replace(value, pairs) for key, value in obj.items()}
    return obj


def _dump(values: dict[str, Any]) -> str:
    return "\n".join(f"{key}={value}" for key, value in values.items())


def _recompute_fg(case: dict[str, Any]) -> None:
    rows = case["fixture"]["rows"]
    route = next(
        row
        for row in rows
        if row["app"] == "file_system"
        and str(row["values"].get("tilde_path", "")).endswith("/dispatch-route.txt")
    )
    route_kv = kv(str(route["values"]["content"]))

    def files(prefix: str) -> list[dict[str, Any]]:
        return [
            row
            for row in rows
            if row["app"] == "file_system"
            and Path(str(row["values"].get("tilde_path", ""))).name.startswith(prefix)
        ]

    policies: list[dict[str, Any]] = []
    for row in files("policy-"):
        values = kv(str(row["values"]["content"]))
        for key in ("MIN_SCORE", "PIVOT", "W1", "W2", "MOD"):
            values[key] = int(values[key])
        policies.append(values)
    cutoff = date.fromisoformat(route_kv["CUTOFF"])
    policy = max(
        (
            item
            for item in policies
            if item["PROJECT"] == route_kv["PROJECT"]
            and item["ACTIVE"] == "YES"
            and date.fromisoformat(item["EFFECTIVE"]) <= cutoff
        ),
        key=lambda item: date.fromisoformat(item["EFFECTIVE"]),
    )
    recipients: list[dict[str, Any]] = []
    for row in files("recipient-"):
        values = kv(str(row["values"]["content"]))
        values["PRIORITY"] = int(values["PRIORITY"])
        recipients.append(values)
    recipient = max(
        (
            item
            for item in recipients
            if item["ROUTE_KEY"] == policy["ROUTE_KEY"] and item["ACTIVE"] == "YES"
        ),
        key=lambda item: (item["PRIORITY"], item["EMAIL"]),
    )
    manifests: list[dict[str, Any]] = []
    for row in files("manifest-"):
        values = kv(str(row["values"]["content"]))
        values["SCORE"] = int(values["SCORE"])
        manifests.append(values)
    eligible = [
        item
        for item in manifests
        if item["REGION"] == policy["REGION"]
        and item["ROUTE_KEY"] == policy["ROUTE_KEY"]
        and item["SCORE"] >= policy["MIN_SCORE"]
    ]
    primary = choose_manifest(
        [item for item in eligible if item["ROLE"] == "PRIMARY"],
        policy["PRIMARY_MODE"],
        policy["PIVOT"],
    )
    secondary = choose_manifest(
        [item for item in eligible if item["ROLE"] == "SECONDARY"],
        policy["SECONDARY_MODE"],
        policy["PIVOT"],
    )
    check = (
        primary["SCORE"] * policy["W1"]
        + secondary["SCORE"] * policy["W2"]
        + recipient["PRIORITY"]
    ) % policy["MOD"]
    payloads = {
        Path(str(row["values"].get("tilde_path", ""))).name: str(
            row["values"].get("content", "")
        )
        for row in rows
        if row["app"] == "file_system"
    }
    case["expected"] = {
        "recipient": recipient["EMAIL"],
        "subject": (
            f"{route_kv['SUBJECT_PREFIX']}-{policy['POLICY_CODE']}-"
            f"{primary['TOKEN']}-{secondary['TOKEN']}-{check:02d}"
        ),
        "body": route_kv["BODY"],
        "attachment_contents": {
            primary["PAYLOAD_FILE"]: payloads[primary["PAYLOAD_FILE"]],
            secondary["PAYLOAD_FILE"]: payloads[secondary["PAYLOAD_FILE"]],
        },
    }


def fg_case(index: int) -> dict[str, Any]:
    sid = f"{index:02d}"
    case = _replace(
        copy.deepcopy(v5_fg_case(index)),
        [
            ("SQ0V5-", "DSFQA0-"),
            ("sq0v5-", "dsfqa0-"),
            ("V5FG", "DFA0FG"),
            ("V5R", "DA0R"),
            ("V5C", "DA0C"),
            ("V5P", "DA0P"),
            ("v5-qualified-blob-", "direct-a0-qualified-blob-"),
        ],
    )
    case["case_id"] = f"DIRECT-SFQ-A0-FG-{sid}"
    case["kind"] = "FG_DIRECT_SEMANTIC_A0"
    for row in case["fixture"]["rows"]:
        values = row["values"]
        if isinstance(values.get("id"), int):
            values["id"] += 7_000_000 + 1000 * index
        if isinstance(values.get("order_index"), int):
            values["order_index"] += 70_000 + 100 * index
        name = Path(str(values.get("tilde_path", ""))).name
        if name == "policy-b.txt":
            item = kv(str(values["content"]))
            item["PIVOT"] = str(int(item["PIVOT"]) + 3 + (index % 4))
            item["W1"] = str(int(item["W1"]) + 1 + (index % 2))
            item["W2"] = str(int(item["W2"]) + (index % 2))
            values["content"] = _dump(item)
        elif name.startswith("manifest-"):
            item = kv(str(values["content"]))
            item["SCORE"] = str(int(item["SCORE"]) + ((index + int(values["id"])) % 5) - 2)
            values["content"] = _dump(item)
        elif name.startswith("recipient-"):
            item = kv(str(values["content"]))
            item["PRIORITY"] = str(int(item["PRIORITY"]) + ((index + 1) % 3))
            values["content"] = _dump(item)
    case["target_local_resources"] = [
        str(value).replace("sq0v5", "dsfqa0").replace("SQ0V5", "DSFQA0")
        for value in case.get("target_local_resources", [])
    ]
    _recompute_fg(case)
    return case


def _recompute_tnf(case: dict[str, Any]) -> None:
    rows = case["fixture"]["rows"]
    route = next(
        row
        for row in rows
        if row["app"] == "simple_note"
        and str(row["values"].get("title", "")).startswith("dsfqa0-route-tnf-")
    )
    route_kv = kv(str(route["values"]["content"]))
    policies: list[dict[str, Any]] = []
    for row in rows:
        if row["app"] == "simple_note" and str(row["values"].get("title", "")).startswith(
            "dsfqa0-policy-"
        ):
            item = kv(str(row["values"]["content"]))
            item["title"] = row["values"]["title"]
            for key in (
                "EPOCH",
                "POLICY_PRIORITY",
                "PIVOT",
                "MODIFIER_PIVOT",
                "BASE",
                "WA",
                "WB",
                "MOD",
            ):
                item[key] = int(item[key])
            policies.append(item)
    cutoff = int(route_kv["CUTOFF_EPOCH"])
    policy = max(
        (
            item
            for item in policies
            if item["ACTIVE"] == "YES"
            and item["TIER"] == route_kv["REQUIRED_TIER"]
            and item["EPOCH"] <= cutoff
        ),
        key=lambda item: (item["EPOCH"], item["POLICY_PRIORITY"], item["title"]),
    )
    contents: list[dict[str, Any]] = []
    for row in rows:
        if row["app"] == "simple_note" and str(row["values"].get("title", "")).startswith(
            "dsfqa0-content-"
        ):
            item = kv(str(row["values"]["content"]))
            item["title"] = row["values"]["title"]
            item["SCORE"] = int(item["SCORE"])
            item["REVISION"] = int(item["REVISION"])
            contents.append(item)
    eligible = [
        item
        for item in contents
        if item["ROUTE_KEY"] == policy["ROUTE_KEY"] and item["PHASE"] == policy["PHASE"]
    ]
    primary = choose_content(
        [item for item in eligible if item["ROLE"] == "PRIMARY"],
        policy["PRIMARY_CONTENT_MODE"],
        policy["PIVOT"],
    )
    secondary = choose_content(
        [item for item in eligible if item["ROLE"] == "SECONDARY"],
        policy["SECONDARY_CONTENT_MODE"],
        policy["PIVOT"],
    )
    tasks: list[dict[str, Any]] = []
    for row in rows:
        if row["app"] == "todoist" and str(row["values"].get("title", "")).startswith(
            "dsfqa0-output-"
        ):
            item = kv(str(row["values"].get("description", "")).replace(";", "\n"))
            tasks.append(
                {
                    "TITLE": row["values"]["title"],
                    "ROUTE_KEY": item["ROUTE_KEY"],
                    "PHASE": item["PHASE"],
                    "PRIORITY": int(item["PRIORITY"]),
                    "WEIGHT": int(item["WEIGHT"]),
                }
            )
    task = choose_task(
        [item for item in tasks if item["ROUTE_KEY"] == policy["ROUTE_KEY"] and item["PHASE"] == policy["PHASE"]],
        policy["TASK_MODE"],
    )
    adjustments: list[dict[str, Any]] = []
    modifiers: list[dict[str, Any]] = []
    for row in rows:
        if row["app"] != "file_system" or "content" not in row["values"]:
            continue
        name = Path(str(row["values"].get("tilde_path", ""))).name
        if name.startswith("adjust-"):
            item = kv(str(row["values"]["content"]))
            item["name"] = name
            item["RANK"] = int(item["RANK"])
            item["DELTA"] = int(item["DELTA"])
            adjustments.append(item)
        elif name.startswith("modifier-"):
            item = kv(str(row["values"]["content"]))
            item["name"] = name
            item["RANK"] = int(item["RANK"])
            item["VALUE"] = int(item["VALUE"])
            modifiers.append(item)
    adjustment = max(
        (
            item
            for item in adjustments
            if item["ADJUST_KEY"] == policy["ADJUST_KEY"] and item["ACTIVE"] == "YES"
        ),
        key=lambda item: item["RANK"],
    )
    modifier = _choose_modifier(
        [item for item in modifiers if item["MOD_KEY"] == policy["MOD_KEY"] and item["ACTIVE"] == "YES"],
        policy["MODIFIER_MODE"],
        policy["MODIFIER_PIVOT"],
    )
    total = (
        policy["BASE"]
        + primary["REVISION"] * policy["WA"]
        + secondary["SCORE"] * policy["WB"]
        + task["PRIORITY"]
        + task["WEIGHT"]
        + adjustment["DELTA"]
        + modifier["VALUE"]
    ) % policy["MOD"]
    output_path = (
        f"{route_kv['OUTPUT_DIR']}{task['TITLE']}-{policy['PHASE']}-"
        f"{primary['TOKEN']}-{secondary['TOKEN']}-{modifier['TOKEN']}.txt"
    )
    output_content = (
        f"POLICY={policy['POLICY_CODE']}\n"
        f"PRIMARY={primary['TOKEN']}:{primary['PAYLOAD']}\n"
        f"SECONDARY={secondary['TOKEN']}:{secondary['PAYLOAD']}\n"
        f"TASK={task['TITLE']}\n"
        f"ADJUST={adjustment['DELTA']}\n"
        f"MODIFIER={modifier['TOKEN']}:{modifier['VALUE']}\n"
        f"TOTAL={total}"
    )
    case["expected"] = {"output_path": output_path, "output_content": output_content}


def tnf_case(index: int) -> dict[str, Any]:
    sid = f"{index:02d}"
    case = _replace(
        copy.deepcopy(v5_tnf_case(index)),
        [
            ("SQ0V5-", "DSFQA0-"),
            ("sq0v5-", "dsfqa0-"),
            ("V5ADJ", "DA0ADJ"),
            ("V5MOD", "DA0MOD"),
            ("V5C", "DA0C"),
            ("V5P", "DA0P"),
            ("V5RK", "DA0RK"),
        ],
    )
    case["case_id"] = f"DIRECT-SFQ-A0-TNF-{sid}"
    case["kind"] = "TNF_DIRECT_SEMANTIC_A0"
    for row in case["fixture"]["rows"]:
        values = row["values"]
        if isinstance(values.get("id"), int):
            values["id"] += 7_500_000 + 1000 * index
        if isinstance(values.get("order_index"), int):
            values["order_index"] += 75_000 + 100 * index
        if row["app"] == "simple_note" and str(values.get("title", "")).startswith(
            "dsfqa0-policy-"
        ):
            item = kv(str(values["content"]))
            item["BASE"] = str(int(item["BASE"]) + 3 + index)
            item["PIVOT"] = str(int(item["PIVOT"]) + 2 + (index % 3))
            item["MODIFIER_PIVOT"] = str(int(item["MODIFIER_PIVOT"]) + (index % 2))
            values["content"] = _dump(item)
        elif row["app"] == "simple_note" and str(values.get("title", "")).startswith(
            "dsfqa0-content-"
        ):
            item = kv(str(values["content"]))
            item["SCORE"] = str(int(item["SCORE"]) + ((index + int(values["id"])) % 5) - 2)
            item["REVISION"] = str(int(item["REVISION"]) + ((index + 1) % 3))
            values["content"] = _dump(item)
        elif row["app"] == "todoist" and str(values.get("title", "")).startswith(
            "dsfqa0-output-"
        ):
            item = kv(str(values.get("description", "")).replace(";", "\n"))
            item["PRIORITY"] = str(int(item["PRIORITY"]) + (index % 3))
            item["WEIGHT"] = str(int(item["WEIGHT"]) + ((index + 2) % 4))
            values["description"] = "; ".join(f"{key}={value}" for key, value in item.items())
        elif row["app"] == "file_system":
            name = Path(str(values.get("tilde_path", ""))).name
            if name.startswith("adjust-"):
                item = kv(str(values["content"]))
                item["DELTA"] = str(int(item["DELTA"]) + 1 + (index % 4))
                values["content"] = _dump(item)
            elif name.startswith("modifier-"):
                item = kv(str(values["content"]))
                item["VALUE"] = str(int(item["VALUE"]) + 1 + ((index + 1) % 3))
                values["content"] = _dump(item)
    case["target_local_resources"] = [
        str(value).replace("sq0v5", "dsfqa0").replace("SQ0V5", "DSFQA0")
        for value in case.get("target_local_resources", [])
    ]
    _recompute_tnf(case)
    return case


def build_cases() -> list[dict[str, Any]]:
    return [fg_case(index) for index in range(1, 7)] + [tnf_case(index) for index in range(1, 7)]


__all__ = ["build_cases", "fg_case", "tnf_case", "evaluate_case_from_state"]
