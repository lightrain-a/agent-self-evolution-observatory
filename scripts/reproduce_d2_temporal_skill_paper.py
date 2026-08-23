#!/usr/bin/env python3
"""Recompute headline C06 probe statistics from the public summary artifact."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "generated" / "d2-temporal-skill-independent-probes-20260822.json"
POP = ROOT / "generated" / "d2-temporal-skill-f5-first-observation-population-completion-20260823.json"
STRONG = ROOT / "generated" / "d2-temporal-skill-f9f10-strong-control-20260823.json"
SEMANTIC = ROOT / "generated" / "d2-temporal-skill-f11-semantic-audit-20260823.json"
SATURATION = ROOT / "generated" / "d2-temporal-skill-source-saturation-20260823.json"
FIG_SCRIPT = ROOT / "scripts" / "plot_d2_temporal_skill_probe_results.py"


def exact_one_sided(discordant: int, favorable: int) -> float:
    if discordant == 0:
        return 1.0
    return sum(math.comb(discordant, k) for k in range(favorable, discordant + 1)) / (2 ** discordant)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    d = json.loads(ART.read_text())
    f0 = d["f0_text_skill_card"]
    f1 = d["f1_callable_output_manipulation_check"]
    f2 = d["f2_downstream_finding_confirmatory"]
    f3 = d["f3_executable_skill_state"]
    f4 = d["f4_crossmodel_executable_replication"]
    f5 = d["f5_all_remaining_executable_replication"]
    f5r2 = d["f5r2_support_recovered_extension"]
    f6 = d["f6_strong_offtarget_control_diagnostic"]
    f8 = d["f8_frozen_population_support_recovery_extension"]
    pop = json.loads(POP.read_text())["first_observation_population"]
    strong = json.loads(STRONG.read_text())
    semantic = json.loads(SEMANTIC.read_text())
    saturation = json.loads(SATURATION.read_text())

    f0_delta = f0["arms"]["targeted_skill"]["accuracy"] - f0["arms"]["matched_generic_skill"]["accuracy"]
    f0_p = exact_one_sided(f0["primary_targeted_vs_generic"]["discordant"], f0["primary_targeted_vs_generic"]["targeted_only_correct"])
    assert abs(f0_delta - 1/13) < 1e-12 and abs(f0_p - 0.5) < 1e-12

    f1_delta = f1["arms"]["targeted_callable_skill"]["accuracy"] - f1["arms"]["matched_generic_helper"]["accuracy"]
    f1_p = exact_one_sided(f1["primary_targeted_vs_generic"]["discordant"], f1["primary_targeted_vs_generic"]["targeted_only_success"])
    assert abs(f1_delta - 13/24) < 1e-12 and abs(f1_p - 1/8192) < 1e-12

    f2_delta = f2["arms"]["targeted_callable_skill"]["accuracy"] - f2["arms"]["matched_generic_helper"]["accuracy"]
    f2_p = exact_one_sided(f2["primary_targeted_vs_generic"]["discordant"], f2["primary_targeted_vs_generic"]["targeted_only_success"])
    assert abs(f2_delta + 0.05) < 1e-12 and abs(f2_p - 0.875) < 1e-12

    f3_delta = f3["arms"]["targeted_executable_skill"]["accuracy"] - f3["arms"]["matched_generic_executable_helper"]["accuracy"]
    f3_p = exact_one_sided(f3["primary_targeted_vs_generic"]["discordant"], f3["primary_targeted_vs_generic"]["targeted_only_success"])
    f3_no_p = exact_one_sided(f3["secondary_targeted_vs_no_skill"]["discordant"], f3["secondary_targeted_vs_no_skill"]["targeted_only_success"])
    assert abs(f3_delta - 4/19) < 1e-12 and abs(f3_p - 0.109375) < 1e-12
    assert abs(f3_no_p - 0.015625) < 1e-12
    assert f3["frozen_gate"]["magnitude_floor_met"] is True and f3["frozen_gate"]["pass"] is False

    f4_delta = f4["arms"]["targeted_executable_skill"]["accuracy"] - f4["arms"]["matched_generic_executable_helper"]["accuracy"]
    f4_p = exact_one_sided(f4["primary_targeted_vs_generic"]["discordant"], f4["primary_targeted_vs_generic"]["targeted_only_success"])
    f4_no_p = exact_one_sided(f4["secondary_targeted_vs_no_skill"]["discordant"], f4["secondary_targeted_vs_no_skill"]["targeted_only_success"])
    assert abs(f4_delta - 2/19) < 1e-12 and abs(f4_p - 0.3125) < 1e-12
    assert abs(f4_no_p - 0.03125) < 1e-12
    assert f4["frozen_gate"]["pass"] is False and f4["p_values_pooled_with_f3"] is False

    f5_delta = f5["arms"]["targeted_executable_skill"]["accuracy"] - f5["arms"]["matched_generic_executable_helper"]["accuracy"]
    f5_p = exact_one_sided(f5["primary_targeted_vs_generic"]["discordant"], f5["primary_targeted_vs_generic"]["targeted_only_success"])
    f5_no_p = exact_one_sided(f5["secondary_targeted_vs_no_skill"]["discordant"], f5["secondary_targeted_vs_no_skill"]["targeted_only_success"])
    assert abs(f5_delta - 1/7) < 1e-12 and abs(f5_p - 0.5) < 1e-12
    assert abs(f5_no_p - 0.125) < 1e-12
    assert f5["frozen_gate"]["pass"] is False and f5["pvalue_pooling_with_f3_or_f4"] is False
    assert f5["qualification"]["passed"] == 7 and f5["qualification"]["failed_support"] == 17
    assert f5["runtime_repair"]["new_initial_model_calls"] == 0

    f5r2_delta = f5r2["arms"]["targeted_executable_skill"]["accuracy"] - f5r2["arms"]["matched_generic_executable_helper"]["accuracy"]
    f5r2_p = exact_one_sided(f5r2["primary_targeted_vs_generic"]["discordant"], f5r2["primary_targeted_vs_generic"]["targeted_only_success"])
    f5r2_no_p = exact_one_sided(f5r2["secondary_targeted_vs_no_skill"]["discordant"], f5r2["secondary_targeted_vs_no_skill"]["targeted_only_success"])
    assert abs(f5r2_delta - 1/5) < 1e-12 and abs(f5r2_p - 0.5) < 1e-12
    assert abs(f5r2_no_p - 1.0) < 1e-12 and f5r2["frozen_gate"]["pass"] is False
    assert f5r2["new_candidates_added"] == 0 and f5r2["frozen_f5_candidates_recovered"] == 5

    f6_delta = f6["targeted_f3"]["accuracy"] - f6["offtarget_executable_control"]["accuracy"]
    f6_p = exact_one_sided(f6["targeted_vs_offtarget"]["discordant"], f6["targeted_vs_offtarget"]["targeted_only_success"])
    assert abs(f6_delta - 5/19) < 1e-12 and abs(f6_p - 0.0625) < 1e-12
    assert f6["diagnostic_only"] is True and f6["primary_closure_authority"] is False
    assert f6["new_initial_model_calls"] == 0

    f8_t = f8["arms"]["targeted_executable_skill"]
    f8_g = f8["arms"]["matched_generic_executable_helper"]
    f8_delta = f8_t["accuracy"] - f8_g["accuracy"]
    f8_p = exact_one_sided(
        f8["primary_targeted_vs_generic"]["discordant"],
        f8["primary_targeted_vs_generic"]["targeted_only_success"],
    )
    f8_no_p = exact_one_sided(
        f8["secondary_targeted_vs_no_skill"]["discordant"],
        f8["secondary_targeted_vs_no_skill"]["targeted_only_success"],
    )
    assert f8["requested_endpoints"] == 7
    assert f8["repeated_endpoint_count"] == 5
    assert f8["repeated_endpoints_scientific_authority"] is False
    assert f8_t["success"] == 5 and f8_g["success"] == 0
    assert abs(f8_delta - 5/7) < 1e-12 and abs(f8_p - 0.03125) < 1e-12
    assert abs(f8_no_p - 0.0625) < 1e-12
    assert f8["frozen_gate"]["pass"] is True
    assert f8["family_concentration"]["all_first_time_endpoints_stl_decompose"] is True
    assert f8["full_12_endpoint_rerun_diagnostic"]["scientific_authority"] is False

    pop_t = pop["arms"]["targeted_executable_skill"]
    pop_g = pop["arms"]["matched_generic_executable_helper"]
    pop_delta = pop_t["accuracy"] - pop_g["accuracy"]
    pop_p = exact_one_sided(pop["targeted_vs_generic"]["discordant"], pop["targeted_vs_generic"]["targeted_only_success"])
    assert pop["available_endpoints"] == 20
    assert pop_t["success"] == 10 and pop_g["success"] == 2
    assert abs(pop_delta - 0.4) < 1e-12 and abs(pop_p - 0.00390625) < 1e-12
    assert pop["formal_closure_authority"] is False

    f9 = strong["f9_qwen"]
    f10 = strong["f10_deepseek"]
    f9_delta = f9["primary"]["paired_risk_difference"]
    f9_p = exact_one_sided(f9["primary"]["discordant"], f9["primary"]["targeted_only"])
    f10_delta = f10["primary"]["paired_risk_difference"]
    f10_p = exact_one_sided(f10["primary"]["discordant"], f10["primary"]["targeted_only"])
    assert f9["arms"]["targeted"]["success"] == 5 and f9["arms"]["substantive_offtarget"]["success"] == 1
    assert abs(f9_delta - 0.5) < 1e-12 and abs(f9_p - 0.0625) < 1e-12
    assert f10["arms"]["targeted"]["success"] == 5 and f10["arms"]["substantive_offtarget"]["success"] == 2
    assert abs(f10_delta - 1/3) < 1e-12 and abs(f10_p - 0.125) < 1e-12
    assert strong["crossmodel_adjudication"]["pvalue_pooling"] is False

    sem = semantic["reviewers"]["deepseek-v4-pro-260425"]
    sem_t = sem["strict_correct"]["targeted_executable_skill"]
    sem_g = sem["strict_correct"]["matched_generic_executable_helper"]
    sem_n = sem["strict_correct"]["no_skill"]
    sem_p = exact_one_sided(sem["targeted_vs_generic"]["discordant"], sem["targeted_vs_generic"]["targeted_only_correct"])
    assert semantic["reviewers_requested"] == 2 and semantic["reviewers_voting"] == 1
    assert sem_t == 6 and sem_g == 2 and sem_n == 0
    assert abs(sem["targeted_vs_generic"]["paired_risk_difference"] - 4/7) < 1e-12
    assert abs(sem_p - 0.109375) < 1e-12
    assert semantic["reviewers"]["kimi-k3"]["status"] == "NONVOTING_PROVIDER_OR_PARSE_FAILURE"
    assert semantic["adjudication"]["deterministic_f8_gate_unchanged"] is True
    assert semantic["adjudication"]["semantic_gate_reproduced"] is False
    assert semantic["adjudication"]["semantic_robustness_established"] is False

    assert saturation["predeclared_minimum_fresh_task_pairs"] == 16
    assert saturation["model_outcomes_observed_for_f12"] == 0
    assert saturation["timesage_mt_l2"]["fresh_stl_candidates_after_excluding_f9_pool"] == 0
    assert saturation["timesage_mt_l1"]["broad_strong_control_metadata_candidates"] == 12
    assert saturation["decision"] == "STOP_NEW_C06_EXPERIMENTS_CURRENT_SAME_SUBSTRATE_SOURCE_SATURATED"

    print(f"artifact_sha256={sha256(ART)}")
    print(f"F0 target-generic delta={f0_delta:.6f} p={f0_p:.12f} gate=FAIL")
    print(f"F1 manipulation target-generic delta={f1_delta:.6f} p={f1_p:.12f} gate=PASS")
    print(f"F2 downstream target-generic delta={f2_delta:.6f} p={f2_p:.12f} gate=FAIL")
    print(f"F3 executable target-generic delta={f3_delta:.6f} p={f3_p:.12f} magnitude=PASS primary=FAIL")
    print(f"F3 executable target-no-skill p={f3_no_p:.12f}")
    print(f"F4 cross-model target-generic delta={f4_delta:.6f} p={f4_p:.12f} primary=FAIL")
    print(f"F4 cross-model target-no-skill p={f4_no_p:.12f}")
    print(f"F5 all-remaining target-generic delta={f5_delta:.6f} p={f5_p:.12f} primary=FAIL")
    print(f"F5 all-remaining target-no-skill p={f5_no_p:.12f} qualified=7 support_failures=17")
    print(f"F5-R2 recovered target-generic delta={f5r2_delta:.6f} p={f5r2_p:.12f} target-no-skill-p={f5r2_no_p:.12f} primary=FAIL")
    print(f"F6 posthoc target-offtarget delta={f6_delta:.6f} p={f6_p:.12f} diagnostic_only=TRUE")
    print(f"F8 dedup first-time target-generic delta={f8_delta:.6f} p={f8_p:.12f} gate=PASS endpoints=7 repeated_zero_authority=5")
    print(f"F8 dedup target-no-skill p={f8_no_p:.12f} family=stl_decompose")
    print(f"F5 frozen-population first-observation completion delta={pop_delta:.6f} p={pop_p:.12f} endpoints=20 formal_closure=FALSE")
    print(f"F9 non-STL strong-control Qwen delta={f9_delta:.6f} p={f9_p:.12f} primary=FAIL")
    print(f"F10 non-STL strong-control DeepSeek delta={f10_delta:.6f} p={f10_p:.12f} primary=FAIL")
    print(f"F11 blinded semantic audit strict target-generic={sem_t}/7 vs {sem_g}/7 p={sem_p:.12f} semantic_gate=FAIL deterministic_F8_unchanged=TRUE")
    print("F12 source audit NO_GO: L2 fresh STL=0; L1 fresh broad=12 < minimum 16; model_outcomes=0")
    print("numeric_recompute=PASS")

    if "--figure" in sys.argv:
        subprocess.run([sys.executable, str(FIG_SCRIPT)], check=True)
        print("figure_recompute=PASS")


if __name__ == "__main__":
    main()
