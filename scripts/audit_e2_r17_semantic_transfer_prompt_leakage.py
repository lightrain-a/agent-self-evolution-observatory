#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FORBIDDEN_LITERAL_TOKENS = (
    "PROCEDURAL_TRANSFORMATION",
    "INSTANCE_BINDING_LOCALIZATION",
    "primary_failure_family",
    "semantic_type",
    "matched_skeleton",
    "foreign_key_binding",
    "header_source_binding",
    "named_region_binding",
    "normalize_then_rank",
    "ordered_filter_rollup",
    "reconcile_then_aggregate",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    req(not args.output.exists(), "prompt-leakage audit output already exists")
    mind_eval = args.mindmemos_root / "src/mindmemos_eval"
    req(mind_eval.is_dir(), "MindMemOS mindmemos_eval source missing")
    sys.path.insert(0, str(mind_eval))
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv

    split_path = args.suite_root / "r17_split_manifest.json"
    metadata_path = args.suite_root / "r17_controlled_metadata.json"
    suite_manifest_path = args.suite_root / "suite_manifest.json"
    for path in (split_path, metadata_path, suite_manifest_path):
        req(path.is_file(), f"missing suite artifact: {path}")

    metadata_rows = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata = {str(row["id"]): row for row in metadata_rows}
    env = SpreadsheetBenchEnv(args.suite_root, Path("/tmp/e2-r17-semantic-transfer-prompt-audit"))
    cases = {case.id: case for case in env.load_cases("all")}
    req(set(cases) == set(metadata), "case/metadata task set mismatch")

    system_prompt = str(env.system_prompt())
    system_hits = [token for token in FORBIDDEN_LITERAL_TOKENS if token in system_prompt]
    req(not system_hits, f"semantic metadata leaked through system prompt: {system_hits}")

    rows: list[dict[str, Any]] = []
    total_hits: list[dict[str, Any]] = []
    for task_id in sorted(cases):
        messages = env.build_messages(cases[task_id])
        visible = json.dumps(messages, ensure_ascii=False, sort_keys=True)
        hits = [token for token in FORBIDDEN_LITERAL_TOKENS if token in visible]
        if task_id in visible:
            hits.append("TASK_ID_LITERAL")
        # The short family code is embedded in task ids but must not appear in visible messages either.
        family_code = str(metadata[task_id].get("family_code") or "")
        if family_code and family_code in visible:
            hits.append("FAMILY_CODE_LITERAL")
        row = {
            "task_id": task_id,
            "message_count": len(messages),
            "visible_message_sha256": hashlib.sha256(visible.encode("utf-8")).hexdigest(),
            "forbidden_hits": hits,
        }
        rows.append(row)
        if hits:
            total_hits.append(row)

    req(len(rows) == 162, f"unexpected task count: {len(rows)}")
    req(not total_hits, f"model-visible semantic/family metadata leakage detected: {total_hits[:5]}")

    split = json.loads(split_path.read_text(encoding="utf-8"))
    update_ids = [str(task) for tasks in split["e1_update_streams"].values() for task in tasks]
    heldout_ids = [str(task) for task in split["e1_common_heldout_probe"]]
    req(len(update_ids) == 96 and len(set(update_ids)) == 96, "update task shape drift")
    req(len(heldout_ids) == 18 and len(set(heldout_ids)) == 18, "heldout task shape drift")
    req(set(update_ids).isdisjoint(heldout_ids), "update/heldout overlap")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v1-model-visible-prompt-leakage-audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_SEMANTIC_TRANSFER_V1_MODEL_VISIBLE_PROMPT_LEAKAGE_AUDIT",
        "suite_root": str(args.suite_root),
        "suite_manifest_sha256": sha(suite_manifest_path),
        "split_manifest_sha256": sha(split_path),
        "metadata_sha256": sha(metadata_path),
        "tasks_checked": len(rows),
        "update_tasks": len(update_ids),
        "heldout_tasks": len(heldout_ids),
        "system_prompt_forbidden_hits": system_hits,
        "task_message_forbidden_hit_count": 0,
        "explicit_semantic_label_visible_to_actor": False,
        "explicit_family_identity_visible_to_actor": False,
        "task_id_visible_to_actor": False,
        "interpretation": (
            "The actor sees only the natural-language SpreadsheetBench task messages and common system prompt. "
            "Experiment-only semantic type, matched-skeleton labels, family identities/codes, and task ids are absent from model-visible text."
        ),
        "authority": {
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "paper_promotion": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
