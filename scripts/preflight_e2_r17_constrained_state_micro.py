#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime


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
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), "constrained-state preflight already exists")
    c = load(args.contract)
    require(c.get("status") == "FROZEN_E2_R17_SINGLE_CASE_CONSTRAINED_STATE_MICRO", "contract status drift")
    require(not any((c.get("authority") or {}).values()), "contract unexpectedly grants authority")
    for label, item in c["bound_code"].items():
        path = ROOT / item["path"]
        require(path.is_file() and sha(path) == item["sha256"], f"bound code drift: {label}")
    initial = Path(c["initial_skill"]["path"])
    require(initial.is_file() and sha(initial) == c["initial_skill"]["sha256"], "initial skill drift")
    initial_text = initial.read_text(encoding="utf-8")
    for state in c["states"]:
        if state["arm"] == "g0_base":
            require(Path(state["skill_path"]).resolve() == initial.resolve(), "G0 must be exact initial skill")
        else:
            path = ROOT / state["skill_path"]
            require(path.is_file() and sha(path) == state["skill_sha256"], f"state skill drift: {state['arm']}")
            require(path.read_text(encoding="utf-8") == initial_text + state["append_text"], f"deterministic construction drift: {state['arm']}")
    suite = Path(c["suite"]["root"])
    require(sha(suite / "suite_manifest.json") == c["suite"]["suite_manifest_sha256"], "suite manifest drift")
    require(sha(suite / "r17_split_manifest.json") == c["suite"]["split_manifest_sha256"], "split manifest drift")
    actor_python, _ = validate_actor_runtime({"runtime": c["actor_runtime"]})
    require(actor_python.is_file(), "actor runtime missing")
    identity = ROOT / c["model_identity"]["path"]
    require(identity.is_file() and sha(identity) == c["model_identity"]["sha256"], "identity drift")
    require(load(identity).get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "identity not passing")
    mind = Path(c["mindmemos"]["root"])
    head = subprocess.check_output(["git", "-C", str(mind), "rev-parse", "HEAD"], text=True).strip()
    require(head == c["mindmemos"]["commit"], "MindMemOS commit drift")
    require(not subprocess.check_output(["git", "-C", str(mind), "status", "--short"], text=True).strip(), "MindMemOS dirty")
    require(not Path(c["run_root"]).exists(), "run root already exists")
    require(not Path(c["lineage_lease_path"]).exists(), "lineage lease already exists")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-single-case-constrained-state-micro-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_CONSTRAINED_STATE_MICRO_ZERO_PROVIDER_PREFLIGHT",
        "contract_path": str(args.contract),
        "contract_sha256": sha(args.contract),
        "states_bound": 4,
        "heldout_units": 72,
        "provider_calls": 0,
        "provider_claims": 0,
        "updater_calls": 0,
        "scientific_outcomes_read": False,
        "partial_effect_read": False,
        "analyzer_run": False,
        "next_gate": "MINT_SINGLE_USE_CONSTRAINED_STATE_MEASUREMENT_AUTHORITY",
    }
    atomic(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
