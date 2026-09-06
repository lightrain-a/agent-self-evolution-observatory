from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_family import family_from_case
from research_pipeline.agent_constraint_externality_direct_sfq_a0_cases import _recompute_fg, _recompute_tnf
from research_pipeline.agent_constraint_externality_sq0_v3_cases import kv


def _replace(value: Any, pairs: list[tuple[str, str]]) -> Any:
    if isinstance(value, str):
        for old, new in pairs:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_replace(item, pairs) for item in value]
    if isinstance(value, dict):
        return {key: _replace(item, pairs) for key, item in value.items()}
    return value


def freshen_case(template: dict[str, Any], ordinal: int) -> dict[str, Any]:
    """Create a fresh instance without changing the Direct-SFQ decision recipe.

    Only instance identifiers, database row ids/order indices, target-local path/title
    names, and output identity strings change. The routing/selection operators,
    candidate counts, tool surface, and semantic evaluator remain unchanged.
    """
    case = copy.deepcopy(template)
    sid = str(template["case_id"]).rsplit("-", 1)[-1]
    tag = f"r{ordinal:03d}"
    id_offset = ordinal * 1000
    order_offset = ordinal * 100

    if "-FG-" in str(template["case_id"]):
        old_dir = f"dsfqa0-fg-{sid}"
        new_dir = f"{old_dir}-{tag}"
        case = _replace(case, [(old_dir, new_dir)])
        for row in case["fixture"]["rows"]:
            values = row["values"]
            if isinstance(values.get("id"), int):
                values["id"] += 30_000_000 + id_offset
            if isinstance(values.get("order_index"), int):
                values["order_index"] += 300_000 + order_offset
        route = next(
            row for row in case["fixture"]["rows"]
            if row["app"] == "file_system"
            and Path(str(row["values"].get("tilde_path", ""))).name == "dispatch-route.txt"
        )
        route_spec = kv(str(route["values"]["content"]))
        route_spec["SUBJECT_PREFIX"] = str(route_spec["SUBJECT_PREFIX"]) + tag.upper()
        route_spec["BODY"] = str(route_spec["BODY"]) + f" Instance {ordinal:03d}."
        route["values"]["content"] = "\n".join(f"{key}={value}" for key, value in route_spec.items())
        _recompute_fg(case)
        case["target_local_resources"] = [
            f"file_system:~/agent_externality/{new_dir}/*",
            f"gmail:outbound:{route_spec['SUBJECT_PREFIX']}",
        ]
        case["case_id"] = f"ACE-DEVRES-FG-{ordinal:03d}-TEMPLATE"
        case["kind"] = "FG_REPEAT_DEV_RESERVE_V1"
        return case

    old_dir = f"dsfqa0-tnf-{sid}"
    new_dir = f"{old_dir}-{tag}"
    pairs = [
        (old_dir, new_dir),
        (f"dsfqa0-route-tnf-{sid}", f"dsfqa0-route-tnf-{sid}-{tag}"),
        (f"dsfqa0-policy-{sid}-", f"dsfqa0-policy-{sid}-{tag}-"),
        (f"dsfqa0-content-{sid}-", f"dsfqa0-content-{sid}-{tag}-"),
        (f"dsfqa0-output-{sid}-", f"dsfqa0-output-{sid}-{tag}-"),
    ]
    case = _replace(case, pairs)
    for row in case["fixture"]["rows"]:
        values = row["values"]
        if isinstance(values.get("id"), int):
            values["id"] += 40_000_000 + id_offset
        if isinstance(values.get("order_index"), int):
            values["order_index"] += 400_000 + order_offset
    _recompute_tnf(case)
    case["case_id"] = f"ACE-DEVRES-TNF-{ordinal:03d}-TEMPLATE"
    case["kind"] = "TNF_REPEAT_DEV_RESERVE_V1"
    return case


def reserve_family(template: dict[str, Any], ordinal: int) -> dict[str, Any]:
    return family_from_case(freshen_case(template, ordinal), ordinal)


__all__ = ["freshen_case", "reserve_family"]
