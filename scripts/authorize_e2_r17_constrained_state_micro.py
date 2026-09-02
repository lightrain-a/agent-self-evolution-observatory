#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--preflight", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "constrained-state authorization already exists")
    c = load(args.contract)
    p = load(args.preflight)
    csha = sha(args.contract)
    require(c.get("status") == "FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO", "contract drift")
    require(p.get("status") == "PASS_CONSTRAINED_STATE_MICRO_ZERO_PROVIDER_PREFLIGHT", "preflight not passing")
    require(p.get("contract_sha256") == csha and int(p.get("provider_calls", -1)) == 0, "preflight binding drift")
    require(p.get("scientific_outcomes_read") is False, "preflight crossed outcome boundary")
    require(not Path(c["run_root"]).exists() and not Path(c["lineage_lease_path"]).exists(), "run root/lease no longer fresh")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-single-case-constrained-state-micro-measurement-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "AUTHORIZED_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO_MEASUREMENT",
        "contract_path": str(args.contract.resolve()),
        "contract_sha256": csha,
        "preflight_path": str(args.preflight.resolve()),
        "preflight_sha256": sha(args.preflight),
        "mindmemos_commit": c["mindmemos"]["commit"],
        "single_use": True,
        "authority": {
            "scientific_experiment": True,
            "measurement_only": True,
            "provider_io": True,
            "updater": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "e3_confirmation": False,
            "paper_promotion": False,
            "submission": False,
        },
        "execution_scope": {
            "measurement_child": "E2-R17-SINGLE-CASE-CONSTRAINED-STATE-MICRO",
            "allowed_modes": ["e1"],
            "allowed_task_ids": c["heldout_task_ids"],
            "exact_k": 1,
            "allow_noninitial_skill": True,
            "state_arms": [row["arm"] for row in c["states"]],
            "state_skill_sha256": {row["arm"]: row["skill_sha256"] for row in c["states"]},
            "required_resolved_model": c["actor"]["resolved_model"],
            "identity_artifact_sha256": c["model_identity"]["sha256"],
            "suite_manifest_sha256": c["suite"]["suite_manifest_sha256"],
            "split_manifest_sha256": c["suite"]["split_manifest_sha256"],
            "max_turns": c["actor"]["max_turns"],
            "max_output_tokens": c["actor"]["max_output_tokens"],
            "provider_budget": {"required": True, "total_limit": 191, "per_unit_limit": 11},
            "exactly_once": True,
            "automatic_retry": False,
            "partial_effect_read": False,
            "lineage_lease_path": c["lineage_lease_path"],
        },
        "interpretation_boundary": "Development-only measurement of four deterministic skill states. No updater calls, no E3, no second backbone, no paper or submission authority.",
    }
    atomic(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
