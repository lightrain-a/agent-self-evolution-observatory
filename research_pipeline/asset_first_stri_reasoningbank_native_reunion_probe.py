#!/usr/bin/env python3
"""Zero-provider STRI operator probe for ReasoningBank's native memory path."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-P0-20260829"
DEFAULT_SOURCE_ROOT = Path(
    "/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026"
)
EXPECTED_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
SOURCE_FILES = {
    "induction": "third_party/src/minisweagent/memory/induce_memory.py",
    "selection": "third_party/src/minisweagent/memory/memory_management.py",
    "rollout": "third_party/src/minisweagent/run/extra/swebench.py",
    "agent": "third_party/src/minisweagent/agents/default.py",
}
EXPECTED_SOURCE_SHA256 = {
    "induction": "7e72fd27cbe3878d743c8135ee809b81d084c0c71ab4ec5f258638876a9ce3c6",
    "selection": "fe71285a878920d501013ab86b58ef12c9c08071ee0e690061774d5ff5588955",
    "rollout": "8365112cd2dd2f3dbd74eff611b5d166530c6ddac4b09b674ae384da96531951",
    "agent": "428a78335cbfb365ba8e6622effc8959104f08e8f32068727625bcb296da756c",
}
MEMORY_PROMPT_PREFIX = (
    "\n\nBelow are some memory items that I accumulated from past interaction "
    "from the environment that may be helpful to solve the task. You can use it "
    "when you feel it's relevant. In each step, please first explicitly discuss "
    "if you want to use each memory item or not, and then take action.\n"
)
BASE_SYSTEM = "You are a software engineering agent operating in a repository."
M1 = (
    "# Memory Item 1\n## Title Verify preconditions\n"
    "## Description Check repository state before editing.\n"
    "## Content Inspect the current state and validate assumptions before applying a change."
)
M2 = (
    "# Memory Item 2\n## Title Test the smallest change\n"
    "## Description Exercise the narrowest relevant regression.\n"
    "## Content Run the focused test first, then widen validation only if it passes."
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def render_selected_memory(selected_cases: list[dict[str, Any]]) -> str:
    """Exact projection used by ReasoningBank's SWE-bench runner after selection."""
    mem_items: list[str] = []
    for item in selected_cases:
        for memory_item in item["memory_items"]:
            mem_items.append(memory_item)
    return "\n\n".join(mem_items)


def render_first_system_message(base_system: str, selected_memory: str) -> str:
    """Exact memory suffix used by DefaultAgent.run before the first query."""
    if selected_memory:
        return base_system + MEMORY_PROMPT_PREFIX + selected_memory
    return base_system


def source_snapshot(source_root: Path) -> tuple[str, dict[str, dict[str, Any]], dict[str, bool]]:
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    sources: dict[str, dict[str, Any]] = {}
    texts: dict[str, str] = {}
    for key, relative in SOURCE_FILES.items():
        path = source_root / relative
        raw = path.read_bytes()
        texts[key] = raw.decode("utf-8")
        digest = sha256_bytes(raw)
        sources[key] = {
            "path": relative,
            "sha256": digest,
            "expected_sha256": EXPECTED_SOURCE_SHA256[key],
            "hash_matches": digest == EXPECTED_SOURCE_SHA256[key],
        }

    checks = {
        "pinned_commit_matches": commit == EXPECTED_COMMIT,
        "all_source_hashes_match": all(v["hash_matches"] for v in sources.values()),
        "induction_splits_on_blank_line": 'return response.split("\\n\\n")' in texts["induction"],
        "induction_persists_task_id": '"task_id": args.task.split(".")[-1]' in texts["induction"],
        "induction_persists_memory_items": '"memory_items": generated_memory_item' in texts["induction"],
        "selection_returns_whole_case": 'if item["task_id"] == sid:' in texts["selection"]
        and "out.append(reasoning_bank[i])" in texts["selection"],
        "rollout_flattens_items_within_case": 'for i in item["memory_items"]:' in texts["rollout"]
        and 'selected_memory = "\\n\\n".join(mem_items)' in texts["rollout"],
        "rollout_passes_memory_before_agent_run": "agent.run(task, selected_memory=selected_memory)" in texts["rollout"],
        "agent_injects_memory_before_first_step": 'self.add_message("system", system_message)' in texts["agent"]
        and "while True:" in texts["agent"]
        and texts["agent"].index('self.add_message("system", system_message)')
        < texts["agent"].index("while True:"),
    }
    return commit, sources, checks


def arm_record(selected_cases: list[dict[str, Any]]) -> dict[str, Any]:
    selected_memory = render_selected_memory(selected_cases)
    system_message = render_first_system_message(BASE_SYSTEM, selected_memory)
    return {
        "selected_case_ids": [item["task_id"] for item in selected_cases],
        "memory_item_count": sum(len(item["memory_items"]) for item in selected_cases),
        "selected_memory": selected_memory,
        "selected_memory_sha256": sha256_text(selected_memory),
        "first_system_message_sha256": sha256_text(system_message),
    }


def build_result(source_root: Path = DEFAULT_SOURCE_ROOT) -> dict[str, Any]:
    commit, sources, static_checks = source_snapshot(source_root)

    monolithic = [{"task_id": "case-A", "memory_items": [M1 + "\n\n" + M2]}]
    same_case_split = [{"task_id": "case-A", "memory_items": [M1, M2]}]
    same_case_reordered = [{"task_id": "case-A", "memory_items": [M2, M1]}]
    cross_case_top1 = [{"task_id": "case-A", "memory_items": [M1]}]
    id_placebo = [{"task_id": "case-ALIAS", "memory_items": [M1, M2]}]

    arms = {
        "A_monolithic_same_case": arm_record(monolithic),
        "B_split_same_case": arm_record(same_case_split),
        "C_split_same_case_reordered": arm_record(same_case_reordered),
        "D_split_cross_case_top1": arm_record(cross_case_top1),
        "E_case_id_placebo": arm_record(id_placebo),
    }
    a, b, c, d, e = (arms[key] for key in arms)
    observations = {
        "A_equals_B_selected_memory": a["selected_memory"] == b["selected_memory"],
        "A_equals_B_first_system_message": a["first_system_message_sha256"]
        == b["first_system_message_sha256"],
        "C_order_boundary_changes_prompt": c["first_system_message_sha256"]
        != a["first_system_message_sha256"],
        "D_case_boundary_top1_drops_fragment": d["first_system_message_sha256"]
        != a["first_system_message_sha256"],
        "E_case_id_not_rendered_after_selection": e["first_system_message_sha256"]
        == b["first_system_message_sha256"],
    }
    operator_pass = all(static_checks.values()) and all(observations.values())
    decision = (
        "NATIVE_WITHIN_CASE_REUNION_PASS_CASE_BOUNDARY_LOCALIZED"
        if operator_pass
        else "IMPLEMENTATION_OR_SOURCE_DRIFT_REQUIRES_DIAGNOSIS"
    )

    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "created_at_utc": "2026-08-29T00:00:00Z",
        "contract": "generated/asset-first-stri-reasoningbank-native-reunion-contract-20260829.json",
        "execution_class": "zero-provider deterministic source/operator probe",
        "provider_model_calls": 0,
        "gpu_seconds": 0,
        "source": {
            "repository": "https://github.com/google-research/reasoning-bank",
            "root": str(source_root),
            "commit": commit,
            "expected_commit": EXPECTED_COMMIT,
            "files": sources,
        },
        "static_checks": static_checks,
        "frozen_witness": {"M1": M1, "M2": M2},
        "arms": arms,
        "observations": observations,
        "decision": decision,
        "failure_differential": {
            "implementation_failure": not all(static_checks.values()),
            "scientific_negative": False,
            "localized_boundary": (
                "ReasoningBank reunites item fragmentation only after a case has been selected; "
                "cross-case fragmentation remains exposed to case-level top-n truncation, and item order is observable."
            ),
        },
        "claim_ceiling": (
            "Supports native pre-decision reunion for semantically identical item partitions nested "
            "inside one already-selected case. It does not establish cross-case invariance, "
            "order invariance, behavioral equivalence, task success, or performance improvement."
        ),
        "next_authorized_action": (
            "Audit availability of first-party per-case memory artifacts and runnable evaluation "
            "environment. Do not start model or GPU evaluation without a separately frozen contract."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_result(args.source_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": result["decision"], "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
