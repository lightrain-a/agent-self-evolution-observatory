#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DESIGN = HERE / "o6-cross-writer-design.json"
INPUT_ROOT = Path("/home/wyt/code/agent-self-evolution-observatory-discovery-benchmark-20260821")
ART_ROOT = Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    d = json.loads(DESIGN.read_text(encoding="utf-8"))
    s1 = d["stage1_cross_writer_write_channel"]
    s2 = d["stage2_cross_writer_terminal_replication"]
    checks = {
        "identity": d["paper_id"] == "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE" and d["objection_id"] == "PROXY-O6",
        "matrix_binding": sha(REPO / "generated/stanford-r2-objection-matrix.json") == d["source_bindings"]["stanford_r2_objection_matrix"]["sha256"],
        "f0_binding": sha(ART_ROOT / "f0-write-channel.json") == d["source_bindings"]["original_f0"]["sha256"],
        "f2r1_binding": sha(ART_ROOT / "f2r1-confirmatory.json") == d["source_bindings"]["original_f2r1"]["sha256"],
        "o5_binding": sha(HERE / "o5-manuscript-evidence.json") == d["source_bindings"]["fresh_o5_no_memory"]["sha256"],
        "parquet_binding": sha(INPUT_ROOT / "generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet") == d["source_bindings"]["trajectory_parquet"]["sha256"],
        "success_prompt_binding": sha(INPUT_ROOT / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/prompts/reasoningbank_pass.md") == d["source_bindings"]["reasoningbank_success_prompt"]["sha256"],
        "failure_prompt_binding": sha(INPUT_ROOT / "generated/research-data/paper-yield-d5-c01/self-improve-fragility/webarena/src/walt/browser_use/custom/prompts/reasoningbank_fail.md") == d["source_bindings"]["reasoningbank_failure_prompt"]["sha256"],
        "terminal_support_binding": d["source_bindings"]["terminal_support"]["sha256"] == "b64635594251ac8f74251ea68b39a0c0c03b689b0708366be9c68ff193edd7ce",
        "terminal_task_config_binding": d["source_bindings"]["terminal_task_config"]["sha256"] == "d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6",
        "terminal_evaluator_binding": d["source_bindings"]["terminal_evaluator"]["sha256"] == "f78eb61554c811f9411e7d72e0bdf2b5baa27379cbf632ade7fe49ce51a3f30d",
        "four_frozen_sources": [x["task_id"] for x in d["frozen_source_units"]] == ["21", "22", "23", "25"],
        "stage1_exactly_eight_calls": s1["provider_calls"] == 8 and len(d["frozen_source_units"]) * len(s1["conditions"]) == 8,
        "stage1_writer_exact": s1["writer_model"]["requested"] == "glm-5.3" and s1["writer_model"]["temperature"] == 0.0 and s1["writer_model"]["provider_retries"] == 0 and s1["writer_model"]["substitution_allowed"] is False,
        "stage1_gate_frozen": s1["advance_to_stage2_if"] == {"all_8_provider_calls_complete": True, "exact_content_changed_pairs_min": 4, "title_set_changed_pairs_min": 3, "token_jaccard_threshold": None},
        "stage2_support_exact": s2["source_memory_tasks"] == ["21", "22", "23", "25"] and s2["future_tasks"] == ["164", "385", "387", "388"],
        "stage2_exactly_256_calls": s2["provider_calls"] == 256 and s2["source_future_cells"] * len(s2["conditions"]) * s2["rollouts_per_cell_per_condition"] == 256,
        "stage2_model_exact": s2["downstream_model"]["requested"] == "doubao-seed-2.0-mini" and s2["downstream_model"]["expected_resolved"] == "doubao-seed-2-0-mini-260215" and s2["downstream_model"]["provider_retries"] == 0 and s2["downstream_model"]["substitution_allowed"] is False,
        "stage2_gate_not_relaxed": s2["support_if"] == {"mean_absolute_success_rate_difference_min": 0.15, "permutation_p_lt": 0.05},
        "o5_not_primary_gate": s2["primary_gate_uses_o5_no_memory"] is False and d["source_bindings"]["fresh_o5_no_memory"]["reusable_in_stage2_descriptive_analysis"] is True,
        "economy_consistent": d["economy"] == {"stage1_calls": 8, "stage2_calls_if_stage1_passes": 256, "maximum_new_provider_calls": 264, "additional_no_memory_calls": 0, "training_runs": 0, "gpu_runs": 0, "early_stop_saves_if_stage1_fails": 256},
        "live_loop_still_blocked": d["live_loop_recheck"]["shopping_port_7770_reachable"] is False and d["live_loop_recheck"]["reset_port_4399_reachable"] is False and d["live_loop_recheck"]["scientific_authority"] is False,
        "no_claim_expansion_authority": d["authority"]["claim_expansion_authority"] is False and d["authority"]["submission_authority"] is False,
    }
    payload = {
        "schema_version": "1.0",
        "artifact_type": "o6-cross-writer-design-qa",
        "paper_id": d["paper_id"],
        "objection_id": d["objection_id"],
        "design_sha256": sha(DESIGN),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "summary": {"passed": sum(checks.values()), "total": len(checks), "stage1_provider_calls_before_contract": 0, "stage2_provider_calls_before_stage1_pass": 0},
        "scientific_authority": False,
        "experiment_authority": False,
    }
    out = HERE / "o6-cross-writer-design-qa.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
