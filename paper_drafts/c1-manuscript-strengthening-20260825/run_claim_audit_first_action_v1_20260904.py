#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

REPLAY = HERE / "c1-b10-first-action-raw-replay-qualification-20260904.json"
MANIFEST = HERE / "c1-b10-first-action-private-provenance-manifest-20260904.json"
M2Z = HERE / "c1-b10-zero-provider-collision-mmd2-diagnostic-20260904.json"
ADJUDICATION = HERE / "c1-effective-experiment-plan-v2.1-m2z-adjudication-20260904.json"
PLAN_MD = HERE / "c1-effective-experiment-plan-v2.1-20260904.md"
PLAN_JSON = HERE / "c1-effective-experiment-plan-v2.1-20260904.json"
R7_SEAL = HERE / "claim-audit-r7-provenance-seal-20260829.json"
R7_REGISTRY = HERE / "claim-audit-r7-registry-20260829.json"
R7_RUNNER = HERE / "run_claim_audit_r7.py"
REPLAY_RUNNER = HERE / "qualify_b10_first_action_raw_replay_20260904.py"
MANIFEST_BUILDER = HERE / "build_b10_first_action_provenance_manifest_20260904.py"
M2Z_RUNNER = HERE / "analyze_b10_collision_mmd2_20260904.py"

INTRO = HERE / "source" / "sections" / "01_intro.tex"
RESULTS = HERE / "source" / "sections" / "04_variance_protocol.tex"
LIMITS = HERE / "source" / "sections" / "06_limitations_conclusion.tex"
APPENDIX = HERE / "source" / "sections" / "07_appendix.tex"
PDF = HERE / "source" / "main.pdf"

EXPECTED_SHA = {
    "replay": "2bac711b6ebec8b77568bdca3cd0ea47d62d2dde52add8e34f44493703ff88d7",
    "manifest": "49b5e62d0476e51c060bfc6ef280c43bd5fb0f809ab5394a2512342f0dd23dca",
    "m2z": "65901eaf5188fd2ffb071f7f4359e78dc26b71b1f0a1439e4f7e81410c1e9c56",
    "adjudication": "daf30ce5242d7551e46ea8e15221a2ee340a9b295098819b655bb955a8a9ce11",
    "plan_md": "42e7ca7cc8d954a514308443915e0de81d649d5b1e8060d5da3be0536b02ade6",
    "plan_json": "1ae5fd159dda44d06ee72ae052257d0dd694793e10297b944cd533e6e76e4d92",
    "r7_seal": "baad7e26fa297412c3959bb58d2df5bdd04d3de52d1175f6b0ea5e14d8caf4cf",
    "r7_registry": "4f9c7992437464c79d4c2ba71bfabe8f8e66638d72529c408eb8b11fbb3d8ebe",
    "r7_runner": "7d5bea14b3ca0e7fe7738ec182c3afb6f73bdf644a932b2966ec9b21f3ac8ac3",
    "replay_runner": "c3557a7429cf0ca4af15e5af34e4052b8a5bb1ea5a17854a2a8039400e4ce557",
    "manifest_builder": "7884ac5d5f3d6d97ed561d569f1dc27b6e2f976c8c1cde8e554250136b7c6f0e",
    "m2z_runner": "eb36501300acaa2281039d6b6de7eeb33769275a5a9ed4b5facc9b7ada68d65f",
    "intro": "613171ea671716665d769f6baf97e3a4b1cba8c8be98fb6cc984cee9dac66158",
    "results": "8f1a3fc94d5baf8bc27c530ab92afdf5cf25479a8fae55258d9422480acc69b2",
    "limits": "a5d5ed6bfa0ecbfdc383fd4d169e79714b3572e3cc6fed69f3fec5f4f2184dd9",
    "appendix": "5d8a3170b89743c3f3f193b15a99f1eca489d59423d727f56d4ca8c1ea02d268",
    "pdf": "1d8623c66b79998c17b4b145aa31b485ef79ee980e75ac5e834557ce2b8e1b73",
}

EXPECTED_PRIVATE_ROOTS = {
    "stage_records_sha256": "6496493b06cb769d1ed072c400b312d4e8e42681783a4c20ed080ac3ed10e74d",
    "raw_texts_sha256": "0303b51e9ee7bd5329452d584620a1a07f6b728027d167c32aba5919248eb574",
    "provider_responses_sha256": "254590ea7465cb84ba274f717c4a492295fe639f15d7b4b553b0fe7027ea34c9",
    "normalized_record_index_sha256": "6aa80edd346c273b781756726b09f2486aea20edc42bd06ca12203e8dd0706af",
    "combined_private_evidence_sha256": "7426ecf9cc58f2f29f82b8c1a862a98aabdbe644aa5dcaf85435b941f4a7eced",
}

PREOUTCOME_SEAL = "dc3e5c4b297c4598b65669e5e68c7d7a2d9cff2d"
IMPLEMENTATION_CHECKPOINT = "ccbcabe8ee4fe5727552fb9f9ae8cd47c79ce0dc"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def path_record(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def check_hashes() -> dict[str, dict[str, str]]:
    files = {
        "replay": REPLAY,
        "manifest": MANIFEST,
        "m2z": M2Z,
        "adjudication": ADJUDICATION,
        "plan_md": PLAN_MD,
        "plan_json": PLAN_JSON,
        "r7_seal": R7_SEAL,
        "r7_registry": R7_REGISTRY,
        "r7_runner": R7_RUNNER,
        "replay_runner": REPLAY_RUNNER,
        "manifest_builder": MANIFEST_BUILDER,
        "m2z_runner": M2Z_RUNNER,
        "intro": INTRO,
        "results": RESULTS,
        "limits": LIMITS,
        "appendix": APPENDIX,
        "pdf": PDF,
    }
    records: dict[str, dict[str, str]] = {}
    for key, path in files.items():
        require(path.is_file(), f"missing audit input: {key}: {path}")
        actual = sha(path)
        require(actual == EXPECTED_SHA[key], f"SHA drift for {key}: expected {EXPECTED_SHA[key]}, got {actual}")
        records[key] = path_record(path)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Replayable claim/provenance audit for C1 first-action stochasticity refinement.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    evidence_files = check_hashes()
    replay = load(REPLAY)
    manifest = load(MANIFEST)
    m2z = load(M2Z)
    adjudication = load(ADJUDICATION)
    plan = load(PLAN_JSON)

    claims: list[dict[str, Any]] = []

    def add(cid: str, description: str, passed: bool, detail: Any) -> None:
        claims.append({"id": cid, "description": description, "pass": bool(passed), "detail": detail})

    add(
        "CFA01",
        "Historical R7 claim audit remains immutable; the 2026-09-04 refinement is additive rather than a rewrite of historical evidence.",
        sha(R7_SEAL) == EXPECTED_SHA["r7_seal"] and sha(R7_REGISTRY) == EXPECTED_SHA["r7_registry"] and sha(R7_RUNNER) == EXPECTED_SHA["r7_runner"],
        {"r7_seal_sha256": sha(R7_SEAL), "r7_registry_sha256": sha(R7_REGISTRY), "r7_runner_sha256": sha(R7_RUNNER)},
    )

    geometry = manifest.get("geometry") or {}
    category_roots = manifest.get("category_roots") or {}
    add(
        "CFA02",
        "First-action raw provenance is first-class and content-addressed across stage records, raw provider text objects, provider receipts, and normalized action identity.",
        manifest.get("status") == "PASS_CONTENT_ADDRESSED_PRIVATE_FIRST_ACTION_PROVENANCE"
        and geometry == {
            "scientific_units": 36,
            "conditions": ["success_memory", "failure_memory", "no_memory"],
            "draws_per_state_per_condition": 4,
            "provider_records": 432,
            "stage_records": 432,
            "raw_text_objects": 432,
            "provider_response_receipts": 432,
        }
        and category_roots == EXPECTED_PRIVATE_ROOTS
        and len(manifest.get("records") or []) == 432,
        {"geometry": geometry, "category_roots": category_roots, "manifest_records": len(manifest.get("records") or [])},
    )

    replayed = replay.get("replayed_historical_primary") or {}
    raw_replay = replay.get("raw_provenance_replay") or {}
    add(
        "CFA03",
        "Historical B10 raw text replays through the frozen normalizer and exactly recovers the published first-action primary result.",
        replay.get("status") == "PASS_B10_FIRST_ACTION_RAW_REPLAY"
        and raw_replay.get("stage_records_verified") == 432
        and raw_replay.get("content_addressed_raw_texts_verified") == 432
        and raw_replay.get("raw_to_historical_action_signature_matches") == 432
        and abs(float(replayed.get("mean_success_failure_tv_full_precision")) - 0.06944444444444445) < 1e-15
        and abs(float(replayed.get("permutation_p_full_precision")) - 0.5800941990580094) < 1e-15
        and replayed.get("modal_success_failure_changes") == "0/36",
        {"raw_provenance_replay": raw_replay, "replayed_primary": replayed},
    )

    add(
        "CFA04",
        "The scientific unit is the frozen matched Shopping state (n=36); repeated provider draws are nested measurements, not independent scientific units.",
        (replay.get("geometry") or {}).get("matched_branch_comparison_states") == 36
        and (replay.get("geometry") or {}).get("success_failure_draws_per_state") == "4+4"
        and (replay.get("geometry") or {}).get("scientific_unit") == "matched frozen Shopping state; repeated calls are nested measurements"
        and (plan.get("scientific_unit") or {}).get("provider_repeats_are_scientific_units") is False,
        {"replay_geometry": replay.get("geometry"), "plan_scientific_unit": plan.get("scientific_unit")},
    )

    design_binding = m2z.get("preoutcome_design_binding") or {}
    inference = m2z.get("inference") or {}
    add(
        "CFA05",
        "Collision/MMD2 statistic, alpha, randomization scheme, and bootstrap were sealed before the M2-Z outcome was opened.",
        design_binding.get("seal_commit") == PREOUTCOME_SEAL
        and (design_binding.get("plan_md") or {}).get("sha256") == EXPECTED_SHA["plan_md"]
        and (design_binding.get("plan_json") or {}).get("sha256") == EXPECTED_SHA["plan_json"]
        and inference.get("permutation_repetitions") == 100000
        and inference.get("permutation_seed") == 20260824
        and abs(float(inference.get("alpha")) - 0.05) < 1e-15
        and (inference.get("bootstrap") or {}).get("repetitions") == 10000
        and (inference.get("bootstrap") or {}).get("seed") == 20260904,
        {"preoutcome_design_binding": design_binding, "inference": inference, "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT},
    )

    summary = m2z.get("summary") or {}
    add(
        "CFA06",
        "Replay-qualified post-hoc collision/MMD2 does not support aggregate success/failure first-action separation on the frozen 36-state panel.",
        m2z.get("status") == "M2Z_ZERO_PROVIDER_COLLISION_MMD2_COMPLETE"
        and m2z.get("decision") == "D2_STOCHASTICITY_ADJUSTED_SEPARATION_NOT_SUPPORTED"
        and abs(float(summary.get("mean_collision_mmd2_u"))) < 1e-15
        and summary.get("positive_u_states") == 1
        and summary.get("zero_u_states") == 33
        and summary.get("negative_u_states") == 2
        and abs(float(summary.get("one_sided_randomization_p")) - 0.5800941990580094) < 1e-15
        and summary.get("support_rule_pass") is False
        and (m2z.get("execution") or {}).get("new_provider_calls") == 0,
        {"summary": summary, "decision": m2z.get("decision"), "execution": m2z.get("execution")},
    )

    results_text = RESULTS.read_text(encoding="utf-8")
    add(
        "CFA07",
        "Main-text baselines map each evaluation surface to a distinct alternative explanation rather than adding an unrelated memory-method leaderboard.",
        all(
            token in results_text
            for token in [
                "Evaluation-surface baselines on the same frozen system",
                "Write-only",
                "Retrieval-only",
                "Endpoint-only",
                "Forced-only",
                "Stage-resolved",
                "Alternative left aliased",
            ]
        ),
        {"table_label": "tab:evaluation-surface-baselines"},
    )

    intro_text = INTRO.read_text(encoding="utf-8")
    limits_text = LIMITS.read_text(encoding="utf-8")
    appendix_text = APPENDIX.read_text(encoding="utf-8")
    joined = "\n".join([intro_text, results_text, limits_text, appendix_text])
    required_claim_tokens = [
        "after exposure and before stable action uptake",
        "not a causal mediation coefficient",
        "does not establish equivalence",
        "post-hoc rather than an independent prospective replication",
        "Replay-qualified first-action stochasticity diagnostic",
        "432 stage records",
    ]
    add(
        "CFA08",
        "Manuscript claim boundary remains conservative: non-support is not equivalence, the reanalysis is post-hoc, and causal mediation remains outside the claim set.",
        all(token in joined for token in required_claim_tokens),
        {"required_tokens": required_claim_tokens, "present": {token: token in joined for token in required_claim_tokens}},
    )

    topup = adjudication.get("prospective_first_action_topup") or {}
    add(
        "CFA09",
        "Prospective first-action top-up is closed by default and may reopen only if independent submission review identifies post-hoc status as verdict-changing.",
        adjudication.get("status") == "M2Z_COMPLETE_KEEP_MEASUREMENT_CLAIM_PROSPECTIVE_TOPUP_CLOSED_BY_DEFAULT"
        and topup.get("default_authorized") is False
        and topup.get("adaptive_topup_for_significance") is False
        and "fresh independent submission review" in str(topup.get("reopen_only_if") or ""),
        {"prospective_first_action_topup": topup},
    )

    add(
        "CFA10",
        "The compiled 15-page manuscript is bound to the audited source revision.",
        sha(PDF) == EXPECTED_SHA["pdf"],
        {"pdf": evidence_files["pdf"], "source_hashes": {key: evidence_files[key] for key in ["intro", "results", "limits", "appendix"]}},
    )

    status = "PASS" if all(claim["pass"] for claim in claims) else "FAIL"
    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-first-action-provenance-claim-audit-v1",
        "date": "2026-09-04",
        "status": status,
        "summary": {
            "claims_total": len(claims),
            "claims_passed": sum(bool(claim["pass"]) for claim in claims),
            "claims_failed": sum(not bool(claim["pass"]) for claim in claims),
        },
        "claims": claims,
        "evidence": evidence_files,
        "audit_runner": path_record(Path(__file__).resolve()),
        "private_provenance_root": EXPECTED_PRIVATE_ROOTS["combined_private_evidence_sha256"],
        "preoutcome_design_seal": PREOUTCOME_SEAL,
        "implementation_checkpoint": IMPLEMENTATION_CHECKPOINT,
        "execution": {"new_scientific_provider_calls": 0, "new_gpu_runs": 0, "network_required": False},
        "authority": {"claim_expansion": False, "submission": False, "new_provider_execution": False},
    }
    require(status == "PASS", f"claim audit failed: {[claim['id'] for claim in claims if not claim['pass']]}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "summary": payload["summary"], "private_provenance_root": payload["private_provenance_root"], "new_provider_calls": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
