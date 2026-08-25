from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "port010-vwe-within-source-v1"
VWE_DATASET_REVISION = "2e152f9f0d082066bb6bc1f8d72809581e664709"
VIBEWORLDING_GYM_REVISION = "ddb6ff54d34a2483859960743319f5d5e5b33e96"
VWE_DATASET_URL = "https://huggingface.co/datasets/usail-hkust/VWE-Bench"
VIBEWORLDING_GYM_URL = "https://github.com/usail-hkust/VibeWorlding-Gym"
TARGET_TYPES = ("Complex description", "Scene restatement")
CONTROL_TYPES = ("Asset-level edit (fuzzy)", "Scene critique", "Scene guidance")
QUERY_CATEGORY = "3D world refinement"
VERIFIER_TYPE = "unverified"
EXPECTED_TEST_CASES = 254
EXPECTED_TARGET_CASES = 35
EXPECTED_TARGET_GROUPS = 11
EXPECTED_ANALYSIS_CASES = 137
EXPECTED_CONTROL_CASES = 102
FORBIDDEN_OUTCOME_NAMES = {
    "final_map.json",
    "sft_trajectory.json",
    "sft_trajectory_verified.json",
    "reward.json",
    "results.json",
    "result.json",
    "outcome.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_path(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _canonical_sha(payload: Any) -> str:
    return _sha_bytes(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _source_group(source_dir: str) -> str:
    source_dir = str(source_dir or "").strip()
    if "___" not in source_dir:
        raise ValueError(f"source_dir lacks frozen delimiter: {source_dir}")
    group, suffix = source_dir.split("___", 1)
    if not group or not suffix:
        raise ValueError(f"source_dir is malformed: {source_dir}")
    return group


def _query_text(query: dict[str, Any]) -> str:
    # All eligible refinement-unverified cases in the pinned test release use
    # `description`. Keep a narrow fallback only so validation errors are clear
    # if the first-party schema changes in a future release.
    value = query.get("description")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("eligible refinement-unverified query lacks non-empty description")
    return value.strip()


def _direct_text_features(text: str) -> dict[str, int]:
    # These are surface diagnostics only, never semantic labels or treatment
    # definitions. They are frozen before outcome access and cannot authorize
    # an outcome-conditioned rematch.
    spatial_terms = (
        "left", "right", "front", "back", "behind", "beside", "between", "near", "far",
        "above", "below", "inside", "outside", "center", "middle", "around", "adjacent",
        "左", "右", "前", "后", "旁", "之间", "附近", "远", "上", "下", "内", "外", "中央", "中间", "周围",
    )
    return {
        "char_count": len(text),
        "utf8_bytes": len(text.encode("utf-8")),
        "line_count": max(1, len(text.splitlines())),
        "digit_count": sum(ch.isdigit() for ch in text),
        "spatial_lexicon_hits": sum(text.lower().count(term) for term in spatial_terms),
    }


def compile_preanalysis(*, metadata_root: Path, source_root: Path) -> dict[str, Any]:
    metadata_root = metadata_root.resolve()
    source_root = source_root.resolve()
    index_path = metadata_root / "index.json"
    if not index_path.is_file():
        raise ValueError("pinned VWE-Bench index.json is missing")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(index, list) or len(index) != EXPECTED_TEST_CASES:
        raise ValueError(f"expected {EXPECTED_TEST_CASES} first-party test cases")
    if len({str(row.get("id") or "") for row in index if isinstance(row, dict)}) != EXPECTED_TEST_CASES:
        raise ValueError("VWE-Bench test ids are not unique/complete")

    outcome_files = sorted(
        str(path.relative_to(metadata_root))
        for path in metadata_root.rglob("*")
        if path.is_file() and path.name.lower() in FORBIDDEN_OUTCOME_NAMES
    )
    if outcome_files:
        raise ValueError("preanalysis metadata root contains outcome-bearing files: " + ",".join(outcome_files[:8]))

    indexed: list[dict[str, Any]] = []
    for row in index:
        if not isinstance(row, dict):
            raise ValueError("VWE-Bench index row is not an object")
        cid = str(row.get("id") or "").strip()
        qpath = metadata_root / cid / "query.json"
        if not qpath.is_file():
            raise ValueError(f"missing first-party query.json:{cid}")
        query = json.loads(qpath.read_text(encoding="utf-8"))
        source_dir = str(row.get("source_dir") or "").strip()
        indexed.append(
            {
                "case_id": cid,
                "source_dir": source_dir,
                "source_group": _source_group(source_dir),
                "query_type": str(row.get("query_type") or ""),
                "query_tag": str(row.get("query_tag") or ""),
                "query_category": str(row.get("query_category") or ""),
                "verifier_type": str(row.get("verifier_type") or ""),
                "query_sha256": _sha_path(qpath),
                "query_schema": sorted(query.keys()),
                "text_features": _direct_text_features(_query_text(query))
                if row.get("query_category") == QUERY_CATEGORY and row.get("verifier_type") == VERIFIER_TYPE
                else {},
            }
        )

    target_rows = [row for row in indexed if row["query_type"] in TARGET_TYPES]
    if len(target_rows) != EXPECTED_TARGET_CASES:
        raise ValueError(f"expected {EXPECTED_TARGET_CASES} target cases")
    if any(row["query_category"] != QUERY_CATEGORY or row["verifier_type"] != VERIFIER_TYPE for row in target_rows):
        raise ValueError("target cases do not share frozen refinement-unverified route")

    target_groups = sorted({row["source_group"] for row in target_rows}, key=lambda x: int(x) if x.isdigit() else x)
    if len(target_groups) != EXPECTED_TARGET_GROUPS:
        raise ValueError(f"expected {EXPECTED_TARGET_GROUPS} target-bearing source groups")

    rows: list[dict[str, Any]] = []
    for row in indexed:
        if row["source_group"] not in target_groups:
            continue
        if row["query_category"] != QUERY_CATEGORY or row["verifier_type"] != VERIFIER_TYPE:
            continue
        if row["query_type"] in TARGET_TYPES:
            role = "TARGET"
        elif row["query_type"] in CONTROL_TYPES:
            role = "CONTROL"
        else:
            continue
        rows.append({**row, "analysis_role": role})

    if len(rows) != EXPECTED_ANALYSIS_CASES:
        raise ValueError(f"expected {EXPECTED_ANALYSIS_CASES} within-source analysis cases")
    if sum(row["analysis_role"] == "TARGET" for row in rows) != EXPECTED_TARGET_CASES:
        raise ValueError("target accounting mismatch")
    if sum(row["analysis_role"] == "CONTROL" for row in rows) != EXPECTED_CONTROL_CASES:
        raise ValueError("control accounting mismatch")

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["source_group"]].append(row)
    for group, members in groups.items():
        roles = Counter(row["analysis_role"] for row in members)
        if not roles["TARGET"] or not roles["CONTROL"]:
            raise ValueError(f"source group lacks both target and control:{group}")

    schemas = {tuple(row["query_schema"]) for row in rows}
    if len(schemas) != 1:
        raise ValueError("eligible within-source cohort does not share one query schema")
    expected_schema = ["description", "query_category", "query_tag", "query_type", "theme", "verification_criteria", "verifier_type"]
    if list(next(iter(schemas))) != expected_schema:
        raise ValueError("eligible first-party query schema changed")

    verifier_files = {
        "root_eval.py": source_root / "eval.py",
        "verifier_eval.py": source_root / "verifier" / "eval.py",
        "unverified_verifier.py": source_root / "verifier" / "unverified_verifier.py",
        "verifier_prompts.py": source_root / "verifier" / "prompts.py",
        "main.py": source_root / "main.py",
    }
    missing_source = [name for name, path in verifier_files.items() if not path.is_file()]
    if missing_source:
        raise ValueError("pinned VibeWorlding-Gym source missing: " + ",".join(missing_source))

    cohort_material = [
        {
            "case_id": row["case_id"],
            "source_group": row["source_group"],
            "query_type": row["query_type"],
            "analysis_role": row["analysis_role"],
            "query_sha256": row["query_sha256"],
            "text_features": row["text_features"],
        }
        for row in sorted(rows, key=lambda item: item["case_id"])
    ]
    group_summary = []
    for group in target_groups:
        members = groups[group]
        group_summary.append(
            {
                "source_group": group,
                "cases": len(members),
                "target": sum(row["analysis_role"] == "TARGET" for row in members),
                "control": sum(row["analysis_role"] == "CONTROL" for row in members),
                "query_type_counts": dict(sorted(Counter(row["query_type"] for row in members).items())),
            }
        )

    source_hashes = {name: _sha_path(path) for name, path in verifier_files.items()}
    plan = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _now(),
        "status": "PREOUTCOME_MATCHED_DESIGN_PROPOSAL_ONLY",
        "candidate_id": "PORT-010",
        "scientific_authority": False,
        "execution_authority": False,
        "design_review_authority": False,
        "outcomes_read": False,
        "provider_calls_executed": 0,
        "authority": {
            "live_problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
        "first_party_provenance": {
            "dataset_url": VWE_DATASET_URL,
            "dataset_revision": VWE_DATASET_REVISION,
            "index_sha256": _sha_path(index_path),
            "query_manifest_sha256": "3aacb5154856ad1fd7b92db4c5629e0a314c6c23947ede9409c3499083915fe2",
            "source_url": VIBEWORLDING_GYM_URL,
            "source_revision": VIBEWORLDING_GYM_REVISION,
            "source_file_sha256s": source_hashes,
        },
        "cohort": {
            "query_category": QUERY_CATEGORY,
            "verifier_type": VERIFIER_TYPE,
            "target_types": list(TARGET_TYPES),
            "control_types": list(CONTROL_TYPES),
            "source_group_rule": "exact prefix of first-party index.source_dir before the first literal '___' delimiter",
            "selection_rule": "retain every target-bearing source group; within those groups retain every refinement+unverified case whose first-party query_type is in TARGET_TYPES or CONTROL_TYPES; no outcome-conditioned dropping or rematching",
            "cases": len(rows),
            "target_cases": EXPECTED_TARGET_CASES,
            "control_cases": EXPECTED_CONTROL_CASES,
            "source_groups": len(groups),
            "shared_query_schema": expected_schema,
            "cohort_sha256": _canonical_sha(cohort_material),
            "group_summary": group_summary,
            "rows": cohort_material,
        },
        "pre_registered_analysis": {
            "primary_outcome": "first-party refine-unverified hard_pass / total_reward==1.0 from pinned verifier pipeline",
            "primary_contrast": "equal-source-group-weighted mean(target hard-pass rate - control hard-pass rate) across the 11 frozen target-bearing source groups",
            "primary_randomization_falsifier": "within each source_group, permute TARGET/CONTROL labels while preserving the frozen target/control counts; fixed RNG seed 20260825; 100000 Monte Carlo permutations; two-sided p-value with +1 correction",
            "control_family_falsifier": "repeat target contrast separately against Scene critique+Scene guidance and against Asset-level edit (fuzzy); a residual that appears only versus fuzzy edits does not support a broad complex-description boundary",
            "control_control_falsifier": "estimate the same within-source contrasts among non-target control query types; if TARGET-vs-CONTROL is not larger than ordinary control-family heterogeneity, return INCONCLUSIVE rather than residual-survives",
            "surface_sensitivity": "report the frozen direct text features (char_count, utf8_bytes, line_count, digit_count, spatial_lexicon_hits); no outcome-conditioned feature engineering, semantic relabeling, or rematching is allowed",
            "mechanism_decomposition": {
                "intent_understanding_failure": "official H3_VU score < 4",
                "realization_binding_failure": "official H3_VU >= 4 and H3_VR < 4",
                "geometry_collision_failure": "official H3_VU >= 4 and H3_VR >= 4 and official H4 pass == 0",
                "other_hard_constraint_failure": "official hard_pass == false after excluding the three ordered categories above; inspect official H1/H2 only, with no new human/model labels",
            },
            "stage_label_policy": "use only first-party verifier outputs; do not create new intent/layout/render labels from observed trajectories",
        },
        "remaining_gates": [
            "Kimi/approved design provider must compile or revise this proposal into the canonical evidence contract once provider infrastructure is restored.",
            "An independent reviewer model distinct from the designer must clear the contract before substrate preflight.",
            "The exact target agent model, exact unverified judge model, renderer/retrieval services, seeds/retries, and smoke unit cap must be frozen before outcome access.",
            "No main.py/eval.py outcome-producing execution is authorized by this proposal.",
            "External single-use human execution authority remains mandatory even after an execution-ready contract is compiled.",
        ],
    }
    plan["proposal_sha256"] = _canonical_sha({key: value for key, value in plan.items() if key not in {"generated_at", "proposal_sha256"}})
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile zero-outcome PORT-010 VWE first-party matched preanalysis proposal")
    parser.add_argument("--metadata-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "generated" / "port010-vwe-firstparty-preanalysis-proposal.json")
    args = parser.parse_args()
    payload = compile_preanalysis(metadata_root=args.metadata_root, source_root=args.source_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "proposal_sha256": payload["proposal_sha256"], "cohort": {k: payload["cohort"][k] for k in ("cases", "target_cases", "control_cases", "source_groups", "cohort_sha256")}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
