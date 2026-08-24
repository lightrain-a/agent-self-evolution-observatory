from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = HERE / "source"
DIAG = json.loads((HERE / "existing-evidence-diagnostics.json").read_text())
O5 = json.loads((HERE / "o5-manuscript-evidence.json").read_text())
O6 = json.loads((HERE / "o6-final-evidence.json").read_text())
O6_REDUCTION = json.loads((HERE / "o6-full-bank-corruption-reduction.json").read_text())
CHRONOLOGY = json.loads((HERE / "f2r1-chronology-receipt.json").read_text())
EXPANSION = json.loads((HERE / "baseline-aligned-expansion-evidence.json").read_text())
FOLLOWUP = json.loads((HERE / "baseline-aligned-followup-evidence.json").read_text())
LOCALIZATION = json.loads((HERE / "transport-localization-evidence.json").read_text())
B11 = json.loads((HERE / "b11-scientific-evidence.json").read_text())
B11_CONCENTRATION = json.loads((HERE / "b11-concentration-evidence.json").read_text())
STORY_SEARCH = json.loads((HERE / "story-v4-argument-search-20260824.json").read_text())
STORY_V5 = json.loads((HERE / "story-v5-crossdomain-adjudication-20260824.json").read_text())
B12 = json.loads((HERE / "b12-crossdomain-reddit-evidence.json").read_text())
WORKING_MEMORY = json.loads((HERE / "b11-working-memory-localization-evidence.json").read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def approx_words(text: str) -> int:
    text = re.sub(r"\\[A-Za-z]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = re.sub(r"[$\\{}]", " ", text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))


def main() -> None:
    abstract = (SRC / "sections/00_abstract.tex").read_text()
    intro = (SRC / "sections/01_intro.tex").read_text()
    related = (SRC / "sections/05_related.tex").read_text()
    mechanism = (SRC / "sections/02_mechanism.tex").read_text()
    setup = (SRC / "sections/02b_setup.tex").read_text()
    f0 = (SRC / "sections/03_f0.tex").read_text()
    control = (SRC / "sections/03a_prompt_control.tex").read_text()
    downstream = (SRC / "sections/04_variance_protocol.tex").read_text()
    limits = (SRC / "sections/06_limitations_conclusion.tex").read_text()
    appendix = (SRC / "sections/07_appendix.tex").read_text()
    main_tex = (SRC / "main.tex").read_text()
    main_text = "\n".join([abstract, intro, related, mechanism, setup, f0, control, downstream, limits])
    all_text = main_text + "\n" + appendix

    e = EXPANSION["experiments"]
    acct = EXPANSION["execution_accounting"]
    cb = EXPANSION["claim_boundary"]
    fe = FOLLOWUP["experiments"]
    facct = FOLLOWUP["execution_accounting"]
    fcb = FOLLOWUP["claim_boundary_delta"]
    le = LOCALIZATION["experiments"]
    lacct = LOCALIZATION["execution_accounting"]
    lcb = LOCALIZATION["claim_boundary"]
    b11w = B11["writer_stage"]
    b11t = B11["terminal_stage"]
    b11acct = B11["execution_accounting"]
    b11cb = B11["claim_boundary_delta"]
    b11c = B11_CONCENTRATION["summary"]
    b12w = B12["writer_stage"]
    b12t = B12["terminal_stage"]
    b12acct = B12["execution_accounting"]
    b12cb = B12["claim_boundary"]
    checks: dict[str, bool] = {}

    checks["abstract_150_220"] = 150 <= approx_words(abstract) <= 220
    checks["stage_resolved_title"] = "\\title{Reward Errors Change Memory Before They Change Policy}" in main_tex
    checks["stage_resolved_story"] = all(x in intro for x in ["stage-resolved", "forced memory swap", "branch-specific policy uptake", "outcome-blind procedural memory"])
    checks["story_search_winner_bound"] = (
        STORY_SEARCH["status"] == "STORY_SEARCH_COMPLETE_WINNER_FROZEN"
        and STORY_SEARCH["winner"]["id"] == "S1-WRITE-TO-UPTAKE-BOTTLENECK"
        and STORY_SEARCH["winner"]["score"] == 98
        and STORY_SEARCH["system_story_contract"]["forbidden_story_mode"] == "experiment chronology / B-number diary"
        and all(x in STORY_SEARCH["winner"]["final_story_spine"][-2] for x in ["S/F", "raw", "no-memory", "structured"])
        and STORY_V5["status"] == "STORY_WINNER_PRESERVED_AFTER_REDDIT_REPLICATION"
        and STORY_V5["prior_winner"] == "S1-WRITE-TO-UPTAKE-BOTTLENECK"
        and STORY_V5["story_adjudication"]["winner_changes"] is False
        and STORY_V5["story_adjudication"]["new_story_role"] == "E5 generalization and failure boundary"
        and STORY_V5["next_experiment_policy"]["another_same_family_reddit_sweep"] == "STOP"
    )
    checks["no_research_os_process_language_main"] = all(x not in main_text for x in ["\\section{F0:", "\\section{C4:", "reviewer-requested", "Stanford-targeted", "Post-ready"])
    checks["system_section_order"] = [main_tex.index(x) for x in ["sections/01_intro", "sections/05_related", "sections/02_mechanism", "sections/02b_setup", "sections/03_f0", "sections/03a_prompt_control", "sections/04_variance_protocol", "sections/06_limitations_conclusion"]] == sorted(main_tex.index(x) for x in ["sections/01_intro", "sections/05_related", "sections/02_mechanism", "sections/02b_setup", "sections/03_f0", "sections/03a_prompt_control", "sections/04_variance_protocol", "sections/06_limitations_conclusion"])
    checks["experimental_setup_present"] = "\\section{Experimental Setup}" in setup

    checks["original_write_bound"] = (
        abs(DIAG["writer_structure"]["mean_token_jaccard_distance"] - 0.734789) < 1e-9
        and DIAG["execution_accounting"]["f0_writer_provider_failures"] == 2
        and all(x in all_text for x in ["0.735", "conditional on paired completion", "task 24", "task 47"])
    )
    checks["breadth_write_20_pair_bound"] = (
        EXPANSION["status"] == "BASELINE_ALIGNED_EXPANSION_COMPLETE_WITH_CROSS_POLICY_SUPPORT_STOP"
        and e["B2_write_breadth"]["combined_complete_pairs"] == 20
        and e["B2_write_breadth"]["combined_exact_content_change_rate"] == 1.0
        and e["B2_write_breadth"]["combined_title_set_change_rate"] == 1.0
        and abs(e["B2_write_breadth"]["new_mean_token_jaccard_distance"] - 0.65757) < 1e-9
        and abs(e["B2_write_breadth"]["pooled_20_pair_mean_token_jaccard_distance"] - 0.673014) < 1e-9
        and e["B2_write_breadth"]["new_distinct_intent_templates"] == 11
        and all(x in all_text for x in ["20/20", "0.65757", "0.673014", "11 intent-template"])
    )
    checks["prompt_rewording_control_bound"] = all(x in all_text for x in ["0.700", "0.595", "0.105", "0.0078"])
    checks["controlled_structural_diagnostic_bound"] = all(x in all_text for x in ["0.556", "0.247", "0.309"])

    checks["f2r1_chronology_bound"] = (
        CHRONOLOGY["status"] == "CHRONOLOGY_AND_UNIFORM_REPLICATION_VERIFIED"
        and CHRONOLOGY["relationship"]["confirmatory_was_designed_after_initial_nonpass"] is True
        and CHRONOLOGY["relationship"]["same_4x4_support"] is True
        and CHRONOLOGY["relationship"]["source_selection_changed"] is False
        and CHRONOLOGY["relationship"]["future_task_selection_changed"] is False
        and CHRONOLOGY["relationship"]["effect_floor_changed"] is False
        and CHRONOLOGY["relationship"]["alpha_changed"] is False
        and all(x in all_text for x in ["0.145833", "0.160128", "0.15625", "0.00074", "same-support"])
    )
    checks["forced_swap_not_native_transport"] = all(x in main_text for x in ["forced memory-swap", "forced-intervention sensitivity", "bypasses native retrieval", "not source-faithful retrieval transport"])

    checks["original_bank_retrieval_audit_bound"] = (
        e["B1_original_bank_exact_retrieval"]["shopping_heldout_tasks"] == 188
        and e["B1_original_bank_exact_retrieval"]["threshold_hits"] == 8
        and abs(e["B1_original_bank_exact_retrieval"]["hit_rate"] - 0.04255319) < 1e-12
        and e["B1_original_bank_exact_retrieval"]["original_frozen_future_hits"] == 0
        and all(x in all_text for x in ["8 of 188", "4.26\\%", "none of the four forced-terminal futures"])
    )
    checks["expanded_bank_retrieval_audit_bound"] = (
        e["B3_expanded_bank_exact_retrieval"]["source_memory_count"] == 20
        and e["B3_expanded_bank_exact_retrieval"]["shopping_heldout_tasks"] == 172
        and e["B3_expanded_bank_exact_retrieval"]["threshold_hits"] == 125
        and abs(e["B3_expanded_bank_exact_retrieval"]["hit_rate"] - 0.72674419) < 1e-12
        and e["B3_expanded_bank_exact_retrieval"]["offline_eligible_tasks"] == 36
        and e["B3_expanded_bank_exact_retrieval"]["eligible_intent_templates"] == 13
        and all(x in all_text for x in ["125 of 172", "72.7\\%", "36", "13 intent-template"])
    )
    checks["native_transport_negative_bound"] = (
        e["B4_native_retrieval_matched_branch_transport"]["complete_calls"] == 288
        and abs(e["B4_native_retrieval_matched_branch_transport"]["mean_absolute_success_rate_difference"] - 0.020833) < 1e-9
        and abs(e["B4_native_retrieval_matched_branch_transport"]["permutation_p"] - 0.428866) < 1e-9
        and e["B4_native_retrieval_matched_branch_transport"]["gate_pass"] is False
        and e["B4_native_retrieval_matched_branch_transport"]["zero_cells"] == 34
        and e["B4_native_retrieval_matched_branch_transport"]["joint_floor_cells"] == 18
        and e["B4_native_retrieval_matched_branch_transport"]["joint_ceiling_cells"] == 16
        and all(x in all_text for x in ["0.02083", "0.4289", "34/36", "18 joint", "16 joint"])
    )
    checks["native_no_memory_floor_fail_bound"] = (
        e["B5_native_support_no_memory"]["complete_calls"] == 144
        and abs(e["B5_native_support_no_memory"]["mean_absolute_memory_presence_effect"] - 0.045139) < 1e-9
        and abs(e["B5_native_support_no_memory"]["permutation_p"] - 0.00147) < 1e-9
        and e["B5_native_support_no_memory"]["gate_pass"] is False
        and e["B5_native_support_no_memory"]["geometry_counts"] == {"CLOSER_TO_FAILURE": 1, "CLOSER_TO_SUCCESS": 1, "EQUIDISTANT": 34}
        and all(x in all_text for x in ["0.04514", "0.00147", "0.15 practical", "34/36"])
    )
    checks["raw_writer_input_baseline_bound"] = (
        FOLLOWUP["status"] == "BASELINE_FOLLOWUP_COMPLETE_RAW_TRAJECTORY_AND_ENDPOINT_DIAGNOSTIC"
        and fe["B8_raw_writer_input_trajectory_baseline"]["complete_calls"] == 144
        and fe["B8_raw_writer_input_trajectory_baseline"]["provider_failures"] == 0
        and abs(fe["B8_raw_writer_input_trajectory_baseline"]["mean_absolute_rewrite_vs_raw_effect"] - 0.045139) < 1e-9
        and abs(fe["B8_raw_writer_input_trajectory_baseline"]["permutation_p"] - 0.00775) < 1e-9
        and fe["B8_raw_writer_input_trajectory_baseline"]["gate_pass"] is False
        and fe["B8_raw_writer_input_trajectory_baseline"]["all_four_equal_tasks"] == 31
        and fe["B8_raw_writer_input_trajectory_baseline"]["runner_tie_biased_secondary_excluded"] is True
        and all(x in all_text for x in ["raw writer-input", "0.00775", "31/36"])
    )
    checks["posthoc_endpoint_headroom_bound"] = (
        fe["B9_partial_reference_endpoint_headroom"]["provider_calls"] == 0
        and fe["B9_partial_reference_endpoint_headroom"]["rollouts_reused"] == 432
        and fe["B9_partial_reference_endpoint_headroom"]["multi_reference_tasks"] == 16
        and abs(fe["B9_partial_reference_endpoint_headroom"]["mean_absolute_success_failure_partial_difference_all"] - 0.019511) < 1e-9
        and abs(fe["B9_partial_reference_endpoint_headroom"]["mean_absolute_success_failure_partial_difference_multi_reference"] - 0.028274) < 1e-9
        and fe["B9_partial_reference_endpoint_headroom"]["binary_joint_floor_cells"] == 18
        and fe["B9_partial_reference_endpoint_headroom"]["partial_joint_floor_cells"] == 10
        and fe["B9_partial_reference_endpoint_headroom"]["binary_same_but_partial_branch_diff_cells"] == 3
        and fe["B9_partial_reference_endpoint_headroom"]["confirmatory_gate"] is None
        and all(x in all_text for x in ["post-hoc", "0.01951", "0.02827"])
    )
    b10 = le["B10_native_first_action_transport"]
    b10d = le["B10D_zero_call_process_diagnostic"]
    checks["native_first_action_transport_nonpass"] = (
        LOCALIZATION["status"] == "TRANSPORT_LOCALIZATION_COMPLETE"
        and b10["complete_calls"] == 432
        and b10["provider_failures_or_parse_failures"] == 0
        and abs(b10["mean_success_failure_first_action_tv"] - 0.069444) < 1e-9
        and abs(b10["permutation_p"] - 0.580094) < 1e-9
        and abs(b10["practical_tv_floor"] - 0.20) < 1e-12
        and b10["gate_pass"] is False
        and b10["states_with_nonzero_success_failure_tv"] == 9
        and b10["states_with_modal_success_failure_difference"] == 0
        and all(x in all_text for x in ["0.06944", "0.5801", "0.20 process floor", "0/36"])
    )
    checks["b10_posthoc_process_diagnostic_bounded"] = (
        b10d["states"] == 36
        and abs(b10d["coarse_action_family_mean_success_failure_tv"] - 0.027778) < 1e-9
        and abs(b10d["mean_next_goal_success_failure_excess_over_within"] - 0.016593) < 1e-9
        and abs(b10d["mean_next_goal_memory_vs_no_memory_distance"] - 0.554403) < 1e-9
        and abs(b10["mean_memory_presence_first_action_tv"] - 0.170139) < 1e-9
        and b10["states_where_either_memory_modal_differs_from_no_memory"] == 6
        and lcb["generic_memory_presence_first_action_effect_confirmatory"] is False
        and all(x in all_text for x in ["0.02778", "0.01659", "0.17014", "descriptive"])
    )
    checks["working_memory_posthoc_localization_bounded"] = (
        WORKING_MEMORY["status"] == "B11_WORKING_MEMORY_LOCALIZATION_COMPLETE_STOP"
        and WORKING_MEMORY["provider_calls"] == 0
        and WORKING_MEMORY["new_rollouts"] == 0
        and abs(WORKING_MEMORY["branch_specific_uptake"]["mean_pair_relative_shift"] - 0.0033469072206773693) < 1e-12
        and abs(WORKING_MEMORY["branch_specific_uptake"]["posthoc_permutation_p"] - 0.2051979480205198) < 1e-12
        and abs(WORKING_MEMORY["generic_common_core_tendency"]["mean_common_centroid_uptake"] - 0.022332304099109024) < 1e-12
        and abs(WORKING_MEMORY["generic_common_core_tendency"]["posthoc_signflip_p"] - 0.06639933600663993) < 1e-12
        and abs(WORKING_MEMORY["transport_linkage"]["pearson_working_memory_shift_vs_first_action_tv"] - 0.46437044778212805) < 1e-12
        and abs(WORKING_MEMORY["transport_linkage"]["pearson_working_memory_shift_vs_terminal_effect"] + 0.022965905301220373) < 1e-12
        and "select tasks by B11 attribution shift" in WORKING_MEMORY["stop_decision"]["forbidden"]
        and all(x in all_text for x in ["0.00335", "0.205", "0.02233", "0.0664", "0.464", "working-memory"])
    )
    checks["outcome_blind_structured_writer_bound"] = (
        B11["status"] == "B11_OUTCOME_BLIND_STRUCTURED_CONTROL_COMPLETE"
        and b11w["complete_calls"] == 20
        and b11w["provider_failures"] == 0
        and b11w["required_native_sources_complete"] == 11
        and abs(b11w["mean_neutral_to_success_token_jaccard_distance"] - 0.61179) < 1e-9
        and abs(b11w["mean_neutral_to_failure_token_jaccard_distance"] - 0.690062) < 1e-9
        and b11w["neutral_title_set_equals_success_sources"] == 0
        and b11w["neutral_title_set_equals_failure_sources"] == 0
        and b11t["complete_calls"] == 144
        and abs(b11t["mean_absolute_reward_conditioned_vs_neutral_effect"] - 0.045139) < 1e-9
        and abs(b11t["permutation_p"] - 0.0048) < 1e-9
        and abs(b11t["practical_effect_floor"] - 0.15) < 1e-12
        and b11t["primary_gate_pass"] is False
        and b11t["zero_effect_tasks"] == 32
        and b11t["all_five_arms_equal_tasks"] == 30
        and all(x in all_text for x in ["outcome-blind", "0.04514", "0.0048", "32/36", "30/36"])
    )
    checks["b11_concentration_bounded"] = (
        B11_CONCENTRATION["status"] == "B11_ZERO_CALL_CONCENTRATION_COMPLETE"
        and B11_CONCENTRATION["provider_calls"] == 0
        and abs(b11c["top1_share_of_absolute_effect_mass"] - 0.615385) < 1e-9
        and abs(b11c["top1_share_of_squared_effect_mass"] - 0.876712) < 1e-9
        and abs(b11c["top2_share_of_squared_effect_mass"] - 0.931507) < 1e-9
        and abs(b11c["minimum_leave_one_task_out_mean_effect"] - 0.017857) < 1e-9
        and b11c["sources_with_nonzero_effect"] == 2
        and b11c["native_selected_source_count"] == 11
        and all(x in all_text for x in ["61.5\\%", "87.7\\%", "0.01786", "2/11"])
    )
    checks["b12_reddit_crossdomain_bound"] = (
        B12["status"] == "B12_REDDIT_CROSSDOMAIN_REPLICATION_COMPLETE"
        and B12["qualification"]["offline_eligible_retrieval_hits"] == 8
        and B12["qualification"]["eligible_intent_templates"] == 2
        and B12["qualification"]["distinct_selected_source_tasks"] == 4
        and b12w["complete_pairs"] == 4
        and b12w["exact_content_change_pairs"] == 4
        and b12w["title_set_change_pairs"] == 4
        and abs(b12w["mean_token_jaccard_distance"] - 0.652342) < 1e-9
        and b12t["scientific_calls"] == 64
        and abs(b12t["mean_absolute_success_rate_difference"] - 0.125) < 1e-12
        and abs(b12t["permutation_p"] - 0.225268) < 1e-9
        and b12t["gate_pass"] is False
        and b12t["zero_effect_tasks"] == 6
        and b12t["nonzero_effect_tasks"] == 2
        and b12t["mean_signed_failure_minus_success"] == 0.0
        and b12t["all_leave_one_task_out_means_below_floor"] is True
        and b12t["leave_one_task_out_mean_range"] == [0.071429, 0.142857]
        and all(x in all_text for x in ["Reddit", "0.652", "0.125", "0.2253", "6/8", "0.071429--0.142857"])
    )
    checks["b12_uniform_repair_bound"] = (
        B12["execution_repair"]["parent_provider_posts"] == 8
        and B12["execution_repair"]["parent_scientific_pairs"] == 0
        and B12["execution_repair"]["all_8_writer_units_regenerated_fresh"] is True
        and B12["execution_repair"]["parent_successes_reused_for_science"] is False
        and B12["execution_repair"]["second_repair_allowed"] is False
        and all(x in appendix for x in ["4,096-token cap", "8,192", "regenerates all eight writer units fresh", "second repair is forbidden"])
    )
    checks["experiment_ladder_present"] = all(x in downstream for x in ["Stage-resolved evidence", "Write identification", "Forced leverage", "Native exposure", "First-action uptake", "Outcome-blind structured control", "Reddit cross-domain replication"])

    checks["o5_original_branch_location_preserved"] = (
        O5["status"] == "O5_FRESH_NO_MEMORY_CONTROL_COMPLETE"
        and O5["point_estimate_geometry_counts"] == {"BASELINE_CLOSER_TO_FAILURE": 2, "BASELINE_CLOSER_TO_SUCCESS": 6, "EQUIDISTANT": 8}
        and all(x in appendix for x in ["22/388", "25/387", "no new global significance test"])
    )
    checks["o6_cross_writer_boundary"] = (
        O6["status"] == "O6_CROSS_WRITER_BOUNDARY_COMPLETE"
        and O6["writer_stage"]["complete_pairs"] == 4
        and abs(O6["writer_stage"]["mean_token_jaccard_distance"] - 0.737482) < 1e-9
        and O6["terminal_stage"]["complete_calls"] == 256
        and abs(O6["terminal_stage"]["mean_absolute_success_rate_difference"] - 0.140625) < 1e-9
        and abs(O6["terminal_stage"]["permutation_p"] - 0.00012) < 1e-9
        and O6["terminal_stage"]["joint_gate_pass"] is False
        and all(x in all_text for x in ["0.737", "0.140625", "0.00012", "two sign reversals"])
    )
    checks["cross_policy_support_stop_not_null"] = (
        e["B6_cross_policy_support_stop"]["scientifically_usable_calls"] == 0
        and e["B6_cross_policy_support_stop"]["provider_posts_parent"] == 1
        and e["B6_cross_policy_support_stop"]["provider_posts_r1"] == 1
        and e["B6_cross_policy_support_stop"]["failure_reason"] == "length/no assistant text"
        and e["B6_cross_policy_support_stop"]["B7_executed"] is False
        and cb["cross_policy_terminal_transfer_status"] == "SUPPORT_STOP_ZERO_SCIENTIFIC_UNITS"
        and all(x in all_text for x in ["900-token", "2,200-token", "zero scientific units", "scientific null"])
    )

    checks["top1_retrieval_contract_preserved"] = (
        O6_REDUCTION["released_mechanism_facts"]["default_top_k"] == 1
        and abs(O6_REDUCTION["released_mechanism_facts"]["default_similarity_threshold"] - 0.3) < 1e-12
        and O6_REDUCTION["released_mechanism_facts"]["reward_conditioned_memory_document_used_in_retrieval_embedding"] is False
        and all(x in all_text for x in ["all-MiniLM-L6-v2", "top-$1$", "threshold 0.3"])
    )
    checks["live_transport_boundary_preserved"] = all(x in limits for x in ["fixed browser-state packets rather than live endpoints", "population risk are outside scope"])
    checks["semantic_diagnostics_bounded"] = all(x in appendix for x in ["token-set Jaccard", "operation-slot", "descriptive supporting evidence"])
    checks["corruption_decomposition_demoted"] = all(x in appendix for x in ["Bounded corruption-rate consequence", "not an empirical corruption sweep"])

    checks["execution_accounting_expansion"] = (
        acct["new_provider_posts"] == 498
        and acct["new_scientifically_usable_provider_completions"] == 464
        and acct["new_scientifically_usable_writer_calls"] == 32
        and acct["new_scientifically_usable_terminal_rollouts"] == 432
        and acct["cross_policy_support_failure_posts"] == 2
        and acct["updated_full_paper_observable_provider_posts_lower_bound"] == 1339
        and "original expansion adds 498 observable POSTs" in appendix
    )
    checks["execution_accounting_followup"] = (
        facct["followup_new_provider_posts"] == 144
        and facct["followup_new_scientifically_usable_provider_completions"] == 144
        and facct["baseline_program_provider_posts_total"] == 642
        and facct["baseline_program_scientifically_usable_completions_total"] == 608
        and facct["baseline_program_scientifically_usable_terminal_rollouts_total"] == 576
        and facct["full_paper_observable_provider_posts_lower_bound_after_followup"] == 1483
    )
    checks["execution_accounting_b10"] = (
        lacct["prior_followup_full_paper_provider_posts_lower_bound"] == 1483
        and lacct["b10_new_provider_posts"] == 432
        and lacct["b10_scientifically_usable_process_calls"] == 432
        and lacct["b10d_new_provider_posts"] == 0
        and lacct["full_paper_observable_provider_posts_lower_bound_after_b10"] == 1915
    )
    checks["execution_accounting_b11"] = (
        b11acct["prior_full_paper_observable_provider_posts_lower_bound_after_b10"] == 1915
        and b11acct["b11_writer_provider_posts"] == 20
        and b11acct["b11_terminal_provider_posts"] == 144
        and b11acct["b11_total_provider_posts"] == 164
        and b11acct["b11_scientifically_usable_provider_completions"] == 164
        and b11acct["full_paper_observable_provider_posts_lower_bound_after_b11"] == 2079
    )
    checks["execution_accounting_b12"] = (
        b12acct["prior_full_paper_observable_provider_posts_lower_bound"] == 2079
        and b12acct["parent_writer_provider_posts"] == 8
        and b12acct["r1_writer_provider_posts"] == 8
        and b12acct["r1_terminal_provider_posts"] == 64
        and b12acct["b12_observable_provider_posts_total"] == 80
        and b12acct["b12_scientifically_usable_calls"] == 72
        and b12acct["b12_scientifically_usable_writer_calls"] == 8
        and b12acct["b12_scientifically_usable_terminal_rollouts"] == 64
        and b12acct["full_paper_observable_provider_posts_lower_bound_after_b12"] == 2159
        and all(x in appendix for x in ["1,318 observable POSTs", "1,276 are scientifically usable", "60 writer calls", "784 terminal rollouts", "432 first-action rollouts", "at least 2,159"])
    )
    checks["inference_only_accounting"] = (
        "inference-only" in setup
        and "no training" in setup
        and "no local GPU fine-tuning" in setup
        and acct["training_runs"] == 0 and acct["gpu_runs"] == 0
        and facct["training_runs"] == 0 and facct["gpu_runs"] == 0
        and lacct["training_runs"] == 0 and lacct["gpu_runs"] == 0
        and b11acct["training_runs"] == 0 and b11acct["gpu_runs"] == 0
        and b12acct["training_runs"] == 0 and b12acct["gpu_runs"] == 0
    )
    checks["claim_boundary_matrix"] = (
        cb["write_channel_breadth_supported"] is True
        and cb["forced_swap_terminal_sensitivity_supported"] is True
        and cb["native_retrieval_matched_branch_transport_supported"] is False
        and cb["native_memory_presence_practical_effect_supported"] is False
        and cb["cross_policy_terminal_transfer_supported"] is None
        and cb["live_browser_transport_supported"] is False
        and fcb["raw_trajectory_practically_large_rewrite_effect_supported"] is False
        and fcb["partial_reference_metric_replaces_binary_gate"] is False
        and fcb["endpoint_resolution_explains_away_native_branch_nonpass"] is False
        and fcb["external_trajectory_retrieval_method_replication_claimed"] is False
        and lcb["B10_native_first_action_branch_transport_supported"] is False
        and lcb["generic_memory_presence_first_action_effect_confirmatory"] is False
        and lcb["model_theory_cause_established"] is False
        and b11cb["practically_large_reward_conditioned_effect_beyond_outcome_blind_structured_rewrite_supported"] is False
        and b11cb["generic_structured_memory_presence_confirmed"] is False
        and b11cb["neutral_writer_superiority_supported"] is False
        and b11cb["live_browser_transport_supported"] is False
        and b12cb["crossdomain_write_divergence_supported_on_four_required_reddit_sources"] is True
        and b12cb["crossdomain_reddit_native_practical_transport_supported"] is False
        and b12cb["uniform_failure_memory_harm_supported"] is False
        and b12cb["shopping_native_magnitude_is_universal_supported"] is False
        and b12cb["live_browser_transport_supported"] is False
        and all(x in limits for x in ["writer-invariant downstream effects remain unestablished", "provider-support stop", "released top-$1$/0.3 retrieval substrate"])
    )

    story_text = (REPO / "paper-story-reward-memory.js").read_text()
    reader_text = (REPO / "paper-reader-data.js").read_text()
    checks["paper_story_expansion_current"] = all(x in story_text for x in ["20/20", "72.7", "0.02083", "0.04514", "0.0048", "30/36", "61.5", "0.01786", "0.06944", "0.5801", "0.00335", "0.205", "Reddit", "0.125", "0.2253", "0.652", "branch-specific uptake", "support stop"])
    checks["paper_reader_expansion_current"] = all(x in reader_text for x in ["20/20", "125/172", "0.02083", "0.04514", ".0048", "30/36", "61.5", ".01786", "0.06944", ".00335", ".205", "Reddit", "0.125", ".2253", ".652", "branch-specific uptake"])

    pdf = HERE / "paper.pdf"
    pdfinfo = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    pages = int(re.search(r"^Pages:\s+(\d+)", pdfinfo, re.M).group(1))
    checks["compiled_pdf_present"] = pdf.exists() and pages >= 1
    page_text = {page: subprocess.check_output(["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"], text=True) for page in range(1, pages + 1)}

    def heading_page(label: str) -> int | None:
        target = re.sub(r"[^a-z]", "", label.lower())
        for page, text in page_text.items():
            for line in text.splitlines():
                if re.sub(r"[^a-z]", "", line.lower()) == target:
                    return page
        return None

    conclusion_page = heading_page("Conclusion")
    references_page = heading_page("References")
    checks["main_text_within_nine_pages"] = conclusion_page is not None and conclusion_page <= 9
    checks["references_not_before_conclusion"] = references_page is not None and conclusion_page is not None and references_page >= conclusion_page
    checks["expanded_pdf_reasonable_total_pages"] = pages <= 20

    payload = {
        "schema_version": "1.4",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision": "ICLR-STAGE-RESOLVED-B12-CROSSDOMAIN-20260824",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "abstract_words_approx": approx_words(abstract),
        "pdf_pages_total": pages,
        "main_text_pages": conclusion_page,
        "references_begin_page": references_page,
        "main_text_page_boundary": f"Conclusion appears on PDF page {conclusion_page}; references begin on PDF page {references_page}.",
        "checks": checks,
        "diagnostic_sha256": sha(HERE / "existing-evidence-diagnostics.json"),
        "o5_evidence_sha256": sha(HERE / "o5-manuscript-evidence.json"),
        "o6_evidence_sha256": sha(HERE / "o6-final-evidence.json"),
        "o6_full_bank_reduction_sha256": sha(HERE / "o6-full-bank-corruption-reduction.json"),
        "f2r1_chronology_receipt_sha256": sha(HERE / "f2r1-chronology-receipt.json"),
        "baseline_aligned_expansion_evidence_sha256": sha(HERE / "baseline-aligned-expansion-evidence.json"),
        "baseline_aligned_followup_evidence_sha256": sha(HERE / "baseline-aligned-followup-evidence.json"),
        "transport_localization_evidence_sha256": sha(HERE / "transport-localization-evidence.json"),
        "b11_scientific_evidence_sha256": sha(HERE / "b11-scientific-evidence.json"),
        "b11_concentration_evidence_sha256": sha(HERE / "b11-concentration-evidence.json"),
        "story_v4_argument_search_sha256": sha(HERE / "story-v4-argument-search-20260824.json"),
        "story_v5_crossdomain_adjudication_sha256": sha(HERE / "story-v5-crossdomain-adjudication-20260824.json"),
        "b12_crossdomain_reddit_evidence_sha256": sha(HERE / "b12-crossdomain-reddit-evidence.json"),
        "working_memory_posthoc_evidence_sha256": sha(HERE / "b11-working-memory-localization-evidence.json"),
        "paper_story_reward_memory_sha256": sha(REPO / "paper-story-reward-memory.js"),
        "paper_reader_data_sha256": sha(REPO / "paper-reader-data.js"),
        "paper_pdf_sha256": sha(pdf),
        "main_tex_sha256": sha(SRC / "main.tex"),
        "scientific_authority": False,
        "experiment_authority": False,
        "claim_expansion": False,
        "new_provider_calls_exact": b12acct["b12_observable_provider_posts_total"],
        "new_scientifically_usable_provider_calls": b12acct["b12_scientifically_usable_calls"],
        "new_scientifically_usable_writer_calls": b12acct["b12_scientifically_usable_writer_calls"],
        "new_terminal_rollouts": b12acct["b12_scientifically_usable_terminal_rollouts"],
        "new_process_rollouts": 0,
        "cross_policy_support_failure_posts": acct["cross_policy_support_failure_posts"],
        "prior_full_paper_observable_provider_posts_lower_bound": b12acct["prior_full_paper_observable_provider_posts_lower_bound"],
        "updated_full_paper_observable_provider_posts_lower_bound": b12acct["full_paper_observable_provider_posts_lower_bound_after_b12"],
        "baseline_program_provider_posts_total": 1318,
        "baseline_program_scientifically_usable_completions_total": 1276,
        "baseline_program_writer_calls_total": 60,
        "baseline_program_terminal_rollouts_total": 784,
        "baseline_program_process_rollouts_total": 432,
        "training_runs": 0,
        "gpu_runs": 0,
    }
    (HERE / "manuscript-qa.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
