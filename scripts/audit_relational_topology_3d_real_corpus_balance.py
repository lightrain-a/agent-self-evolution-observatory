from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.relational_topology_training_qualification import canonical_bytes

OBJECT_ID = "RELATIONAL-TOPOLOGY-STAGE-3D-20260831"
RUN_ID = f"{OBJECT_ID}-real-corpus-balance-qualification-v4"
PARENT_RUN_ID = f"{OBJECT_ID}-real-corpus-qualification-v3"
TOPOLOGY_MAX_ABS_PROPORTION_DELTA = 0.025
EXPECTED_CORPUS_SHA = {
    "IS-SUPPORT-12": "9884b2afd58e05ed0eb80864154765e55551e5f77632d4fbd6308d0af50dd58b",
    "IS-SUPPORT-14": "51e9e6011250970c660d91c75843919f55192b800423d8ad59a2cfb5c08c4b05",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def slot_of(row: dict[str, Any]) -> int:
    match = re.search(r"-S(\d{2})-IS-SUPPORT-(?:12|14)$", row["example_id"])
    if match is None:
        raise ValueError(f"malformed example id: {row['example_id']}")
    return int(match.group(1))


def signature(row: dict[str, Any]) -> str:
    t = row["topology_statistics"]
    value = {
        "active_components": t["active_components"],
        "max_degree": t["max_degree"],
        "diameter": t["diameter"],
        "shared_anchor_fraction": t["shared_anchor_fraction"],
        "largest_component": t["largest_component"],
    }
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def proportions(counter: Counter[str]) -> dict[str, float]:
    total = sum(counter.values())
    return {key: value / total for key, value in sorted(counter.items())}


def max_delta(left: dict[str, float], right: dict[str, float]) -> float:
    return max((abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in set(left) | set(right)), default=0.0)


def conditional(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for count in sorted({row["relation_count"] for row in rows}):
        values = Counter(signature(row) for row in rows if row["relation_count"] == count)
        result[str(count)] = {"n": sum(values.values()), "counts": dict(sorted(values.items())), "proportions": proportions(values)}
    return result


def shared_exact(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> tuple[bool, int]:
    peers = {(row["source_scene_id"], slot_of(row)): row for row in right if slot_of(row) in {0, 1}}
    checked = 0
    for row in left:
        slot = slot_of(row)
        if slot not in {0, 1}:
            continue
        checked += 1
        peer = peers.get((row["source_scene_id"], slot))
        if peer is None:
            return False, checked
        fields = (
            "relation_set", "relation_count", "topology_statistics", "exact_instruction",
            "exact_clip_token_count", "rng_seed", "source_scene_id", "object_ids",
        )
        if any(row[field] != peer[field] for field in fields):
            return False, checked
    return checked == len(peers) and checked > 0, checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--external-v3-dir", type=Path, required=True)
    parser.add_argument("--parent-git-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise SystemExit(f"output already exists: {args.output_dir}")

    parent = json.loads((args.parent_git_dir / "adjudication.json").read_text())
    if parent["run_id"] != PARENT_RUN_ID or parent["scientific_outcomes"] != 0:
        raise SystemExit("parent v3 artifact drift")
    rows: dict[str, list[dict[str, Any]]] = {}
    observed_sha: dict[str, str] = {}
    for regime in ("IS-SUPPORT-12", "IS-SUPPORT-14"):
        path = args.external_v3_dir / f"{regime}.jsonl"
        observed_sha[regime] = sha256_file(path)
        if observed_sha[regime] != EXPECTED_CORPUS_SHA[regime]:
            raise SystemExit(f"v3 corpus drift: {regime}: {observed_sha[regime]}")
        rows[regime] = read_jsonl(path)

    conditional_topology = {regime: conditional(value) for regime, value in rows.items()}
    common_count_deltas: dict[str, float] = {}
    for count in (1, 2):
        left = conditional_topology["IS-SUPPORT-12"][str(count)]["proportions"]
        right = conditional_topology["IS-SUPPORT-14"][str(count)]["proportions"]
        common_count_deltas[str(count)] = max_delta(left, right)
    topology_balance_pass = all(value <= TOPOLOGY_MAX_ABS_PROPORTION_DELTA for value in common_count_deltas.values())
    exact, checked = shared_exact(rows["IS-SUPPORT-12"], rows["IS-SUPPORT-14"])
    object_hist = {
        regime: dict(sorted(Counter(str(row["object_count"]) for row in value).items()))
        for regime, value in rows.items()
    }
    object_strata_exact = object_hist["IS-SUPPORT-12"] == object_hist["IS-SUPPORT-14"]
    gates = {
        "parent_v3_content_address_verified": True,
        "shared_slots_0_1_topology_exact": exact,
        "common_support_topology_distribution_balance": topology_balance_pass,
        "scene_object_strata_exact": object_strata_exact,
    }
    verdict = "PASS_REAL_CORPUS_BALANCE_QUALIFIED_GPU_QUALIFICATION_PROPOSABLE" if all(gates.values()) else "HOLD_REAL_CORPUS_TOPOLOGY_BALANCE"
    audit = {
        "object_id": OBJECT_ID, "run_id": RUN_ID, "parent_run_id": PARENT_RUN_ID,
        "status": "PASS" if all(gates.values()) else "FAIL", "gates": gates,
        "frozen_before_topology_distribution_inspection": {
            "metric": "max absolute topology-signature proportion delta",
            "common_relation_counts": [1, 2],
            "tolerance": TOPOLOGY_MAX_ABS_PROPORTION_DELTA,
            "note": "Counts 3-4 are treatment-induced support and are recorded but have no SUPPORT-12 matching target.",
        },
        "topology_signature_fields": ["active_components", "max_degree", "diameter", "shared_anchor_fraction", "largest_component"],
        "common_count_max_abs_proportion_delta": common_count_deltas,
        "conditional_topology": conditional_topology,
        "shared_subset": {"slots": [0, 1], "rows_compared": checked, "exact": exact},
        "scene_object_strata": {"exact": object_strata_exact, "object_count_histogram": object_hist},
        "corpus_sha256": observed_sha,
    }
    adjudication = {
        "object_id": OBJECT_ID, "run_id": RUN_ID, "parent_run_id": PARENT_RUN_ID,
        "verdict": verdict, "scientific_outcomes": 0, "scientific_gpu_runs": 0,
        "topology_audit_status": audit["status"], "gates": gates,
        "corpus_sha256": observed_sha,
        "authority": {
            "gpu_training_qualification_authority": False, "gpu_authority": False,
            "official_training": False, "p1": False, "provider_calls": 0,
            "scientific_gpu_runs": 0, "scientific_outcomes": 0,
            "next_gate": "PROPOSE_GPU_TRAINING_QUALIFICATION_AUTHORITY" if verdict.startswith("PASS_") else "STOP_HOLD_TOPOLOGY_BALANCE",
            "port_010": {"status": "HOLD_EVIDENCE_REVIEW_BLOCKED", "evidence_review": "BLOCK_BAKE_IN", "changed": False},
        },
        "historical_parent_note": "v3 remains immutable as the materialization/replay record; v4 is the superseding explicit topology-balance qualification.",
    }
    args.output_dir.mkdir(parents=True)
    (args.output_dir / "topology_balance.json").write_bytes(canonical_bytes(audit))
    (args.output_dir / "adjudication.json").write_bytes(canonical_bytes(adjudication))
    hashes = {path.name: sha256_file(path) for path in sorted(args.output_dir.iterdir()) if path.is_file()}
    (args.output_dir / "ARTIFACT_SHA256SUMS").write_text("".join(f"{value}  {name}\n" for name, value in hashes.items()))
    print(json.dumps({"verdict": verdict, "common_count_deltas": common_count_deltas, "shared_rows": checked}, sort_keys=True))
    return 0 if verdict.startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
