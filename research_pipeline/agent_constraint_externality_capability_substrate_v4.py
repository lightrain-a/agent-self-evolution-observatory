from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
PARENT_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v3-20260902.bundle"
PARENT_QUAL = GENERATED / "agent-constraint-externality-capability-substrate-recovery-qualification-r3-20260902.json"
OUTPUT_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
AUDIT_OUTPUT = GENERATED / "agent-constraint-externality-capability-substrate-v4-contract-20260902.json"
SUBSTRATE_ID = "ACE-APPWORLD-CAPABILITY-SUBSTRATE-V4-20260902"
HEADROOM_MULTIPLIER = 4 / 3


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build() -> dict[str, Any]:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import bundle_file_path_to_content, pack_bundle

    qual = json.loads(PARENT_QUAL.read_text(encoding="utf-8"))
    if qual.get("status") != "CAPABILITY_SUBSTRATE_V3_PUBLIC_REACHABILITY_PASS":
        raise RuntimeError("V4 requires V3 public reachability PASS.")
    oracle_max = max(int(row["tool_calls"]) for row in qual["public_oracle_results"])
    tool_budget = math.ceil(oracle_max * HEADROOM_MULTIPLIER)
    if oracle_max != 12 or tool_budget != 16:
        raise RuntimeError("V4 frozen headroom rule must resolve 12 public-oracle calls to budget 16.")

    contents = bundle_file_path_to_content(str(PARENT_BUNDLE), PASSWORD, SALT)
    spec = json.loads(contents["compiler_spec/family_spec.json"])
    if spec.get("object_id") != OBJECT_ID:
        raise RuntimeError("V3 spec object mismatch.")
    for family in spec["families"]:
        for arm in family["arms"]:
            arm["matching"]["tool_budget"] = tool_budget
    spec["substrate_revision"] = SUBSTRATE_ID
    spec["parent_protected_bundle_sha256"] = sha256_file(PARENT_BUNDLE)
    spec["substrate_repairs"] = list(dict.fromkeys([
        *spec.get("substrate_repairs", []),
        "TOOL_BUDGET_ORACLE_HEADROOM_4_OVER_3",
    ]))
    spec["tool_budget_rule"] = {
        "basis": "MAX_PUBLIC_ORACLE_TOOL_CALLS",
        "oracle_max": oracle_max,
        "headroom_multiplier": "4/3",
        "resolved_budget": tool_budget,
        "model_outcomes_used": False,
    }

    rebuild = contents["compiler_spec/rebuild_spec.py"]
    if rebuild.count('"tool_budget":12') != 2:
        raise RuntimeError("Expected exactly two frozen tool-budget templates in rebuild script.")
    rebuild = rebuild.replace('"tool_budget":12', f'"tool_budget":{tool_budget}')

    with tempfile.TemporaryDirectory(prefix="ace-substrate-v4-") as directory:
        root = Path(directory)
        for relative, content in contents.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if relative == "compiler_spec/family_spec.json":
                target.write_text(json.dumps(spec, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            elif relative == "compiler_spec/rebuild_spec.py":
                target.write_text(rebuild, encoding="utf-8")
            elif isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content, encoding="utf-8")
        packed = pack_bundle(str(OUTPUT_BUNDLE), str(root), ["compiler_spec"], PASSWORD, SALT, include_license=False)
    if "compiler_spec/family_spec.json" not in packed:
        raise RuntimeError("V4 protected bundle incomplete.")

    replay = bundle_file_path_to_content(str(OUTPUT_BUNDLE), PASSWORD, SALT, include_file_paths=["compiler_spec/family_spec.json"])
    replay_spec = json.loads(replay["compiler_spec/family_spec.json"])
    budgets = {arm["matching"]["tool_budget"] for family in replay_spec["families"] for arm in family["arms"]}
    if budgets != {16}:
        raise RuntimeError(f"V4 tool budget not globally matched: {budgets}")

    audit: dict[str, Any] = {
        "schema_version": "ace-appworld-capability-substrate-v4-contract-v1",
        "object_id": OBJECT_ID,
        "substrate_id": SUBSTRATE_ID,
        "status": "CAPABILITY_SUBSTRATE_V4_TOOL_BUDGET_QUALIFIED",
        "parent_bundle": {"path": str(PARENT_BUNDLE.relative_to(ROOT)), "sha256": sha256_file(PARENT_BUNDLE)},
        "active_bundle": {"path": str(OUTPUT_BUNDLE.relative_to(ROOT)), "sha256": sha256_file(OUTPUT_BUNDLE)},
        "public_oracle_qualification_sha256": sha256_file(PARENT_QUAL),
        "tool_budget_rule": {
            "oracle_max_tool_calls": oracle_max,
            "headroom_multiplier": "4/3",
            "formula": "ceil(max_public_oracle_tool_calls * 4 / 3)",
            "resolved_tool_call_cap": tool_budget,
            "model_outcomes_used_to_choose_cap": False,
        },
        "rationale": (
            "The verified public TNF oracle consumes 12 tool calls with no hidden IDs while performing normal discovery and filesystem checks. "
            "A cap equal to the oracle path leaves zero execution headroom and turns reasonable post-condition verification into artificial floor failure."
        ),
        "unchanged": {
            "task_text_from_v3": True,
            "family_count": 12,
            "constraint_count": 3,
            "coupling_levels": [0, 1, 2],
            "capability_thresholds": "UNCHANGED",
            "model": "qwen3.7-plus",
            "fg_measurements": "PRESERVED_IF_ALREADY_COMPLETED_BELOW_12",
            "update_surface": "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
        },
        "provider_requests": 0,
        "f0_scientific_outcomes_observed": 0,
    }
    audit["content_sha256"] = sha256_value(audit)
    write_json(AUDIT_OUTPUT, audit)
    return audit


def main() -> None:
    audit = build()
    print(json.dumps({"status": audit["status"], "active_bundle": audit["active_bundle"], "tool_cap": audit["tool_budget_rule"]["resolved_tool_call_cap"], "provider_requests": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
