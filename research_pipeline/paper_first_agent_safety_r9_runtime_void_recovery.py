from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    execution_dir = Path(args.execution_dir)
    journal_path = execution_dir / "runtime-journal.json"
    journal_before_sha = sha_file(journal_path)
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    bad = [row for row in journal["episodes"].values() if row.get("status") == "protocol_inconclusive"]
    if len(bad) != 1:
        raise RuntimeError(f"expected exactly one inconclusive row, found {len(bad)}")
    row = bad[0]
    allowed = (
        str(row.get("inconclusive_reason") or "").startswith("BrokenPipeError:")
        and int(row.get("agent_model_calls_reserved") or 0) == 0
        and int(row.get("classifier_evaluations_reserved") or 0) == 0
        and int(row.get("actions_executed") or 0) == 0
        and row.get("harmbench_prediction") is None
        and row.get("harmbench_response") is None
        and row.get("text_output") is None
    )
    if not allowed:
        raise RuntimeError("inconclusive row contains behavioral realization and cannot be voided")
    episode_id = row["episode_id"]
    audit_path = execution_dir / "runtime-void-attempts" / f"{episode_id}.json"
    atomic_json(audit_path, row)
    journal.setdefault("runtime_void_attempts", {})[episode_id] = {
        "failure_layer": "runtime",
        "reason": row["inconclusive_reason"],
        "behavior_realized": False,
        "agent_model_calls_reserved": 0,
        "classifier_evaluations_reserved": 0,
        "actions_executed": 0,
        "audit_path": str(audit_path),
        "audit_sha256": sha_file(audit_path),
        "replacement_attempt_authorized": True,
        "scientific_effect": "NONE",
    }
    del journal["episodes"][episode_id]
    counters = journal["counters"]
    if counters["behavior_episode_starts"] <= 0 or counters["protocol_inconclusive_episodes"] != 1:
        raise RuntimeError("journal counter precondition drift")
    counters["behavior_episode_starts"] -= 1
    counters["protocol_inconclusive_episodes"] -= 1
    journal["status"] = "R9_F0_RUNTIME_JOURNAL_ACTIVE"
    atomic_json(journal_path, journal)
    receipt = {
        "schema_version": "1.0",
        "status": "RECOVERED_RUNTIME_VOID_BEFORE_BEHAVIOR_REALIZATION",
        "failure_layer": "runtime",
        "episode_id": episode_id,
        "reason": row["inconclusive_reason"],
        "journal_before_sha256": journal_before_sha,
        "journal_after_sha256": sha_file(journal_path),
        "void_attempt_audit_sha256": sha_file(audit_path),
        "behavior_realized": False,
        "model_or_classifier_budget_consumed": False,
        "completed_episode_rerun": False,
        "replacement_attempt_authorized": True,
        "scientific_effect": "NONE",
        "scientific_authority": False,
    }
    atomic_json(Path(args.output), receipt)
    atomic_json(execution_dir / "runtime-void-recovery-receipt.json", receipt)
    print(json.dumps(receipt, separators=(",", ":")))


if __name__ == "__main__":
    main()
