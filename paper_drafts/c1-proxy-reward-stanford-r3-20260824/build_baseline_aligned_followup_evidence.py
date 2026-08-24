#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
PATHS = {
    'prior_expansion': HERE / 'baseline-aligned-expansion-evidence.json',
    'b8_contract': Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b8-raw-trajectory-baseline-20260824/b8-contract.json'),
    'b8_result': Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b8-raw-trajectory-baseline-20260824/b8-result.json'),
    'b8_tie_geometry': Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b8-raw-trajectory-baseline-20260824/b8-tie-aware-geometry.json'),
    'b9_contract': Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b9-partial-reference-coverage-20260824/b9-contract.json'),
    'b9_result': Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b9-partial-reference-coverage-20260824/b9-result.json'),
}
EXPECTED = {
    'prior_expansion': '707d9c089585c1c1895fa7c260a191ba1824eb99d30efe30fd12ba23b563f885',
    'b8_contract': '3327b5d6316b86b8579ca73c60a3cae7e8e8e7578390b5a8f51f8b450cd90cb3',
    'b8_result': '24c855b7f358a27cdfd1bd03ce79a83e12a5bb7d5ca9a253bde7b842a1c379c0',
    'b8_tie_geometry': 'd507028a34f2aab329c6430b981c2125f9c7532494df39680c87b784cae9f6f4',
    'b9_contract': '636425bab815f0782397de2a61696a889aa7c983d983eed72696436c9594d393',
    'b9_result': '087e83f9502d8bf97818bce49b256b177a5f1a164e3fe0523648530385b239a6',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def main() -> None:
    for key, expected in EXPECTED.items():
        path = PATHS[key]
        require(path.is_file(), f'missing source: {path}')
        require(sha(path) == expected, f'{key} SHA drift')
    d = {key: load(path) for key, path in PATHS.items()}
    prior, b8c, b8, geom, b9c, b9 = d['prior_expansion'], d['b8_contract'], d['b8_result'], d['b8_tie_geometry'], d['b9_contract'], d['b9_result']

    require(prior.get('paper_id') == PAPER_ID, 'prior expansion paper identity drift')
    require(prior.get('status') == 'BASELINE_ALIGNED_EXPANSION_COMPLETE_WITH_CROSS_POLICY_SUPPORT_STOP', 'prior expansion state drift')
    pa = prior['execution_accounting']
    require(pa['new_provider_posts'] == 498 and pa['new_scientifically_usable_provider_completions'] == 464, 'prior expansion accounting drift')
    require(pa['new_scientifically_usable_terminal_rollouts'] == 432 and pa['updated_full_paper_observable_provider_posts_lower_bound'] == 1339, 'prior expansion terminal accounting drift')

    require(b8c.get('paper_id') == PAPER_ID and b8c.get('status') == 'FROZEN_BEFORE_PROVIDER_CALLS', 'B8 contract drift')
    require(b8.get('paper_id') == PAPER_ID and b8.get('status') == 'B8_EXECUTION_COMPLETE', 'B8 result drift')
    require(b8['summary']['provider_calls_attempted_total'] == 144 and b8['summary']['provider_calls_complete'] == 144 and b8['summary']['provider_failures'] == 0, 'B8 execution accounting drift')
    require(abs(b8['summary']['observed_mean_absolute_rewrite_vs_raw_effect'] - 0.045139) < 1e-12, 'B8 effect drift')
    require(abs(b8['summary']['three_arm_permutation_p_ge_observed'] - 0.00775) < 1e-12, 'B8 permutation drift')
    require(b8['summary']['practical_effect_floor'] == 0.15 and b8['summary']['primary_gate_pass'] is False, 'B8 gate drift')
    require(b8['decision'] == 'REWRITE_VS_RAW_EFFECT_NOT_ESTABLISHED', 'B8 decision drift')

    require(geom.get('status') == 'DERIVED_GEOMETRY_COMPLETE_ZERO_PROVIDER_CALLS' and geom.get('provider_calls') == 0, 'B8 geometry drift')
    require(geom['runner_secondary_field_disposition']['use_in_manuscript'] is False and geom['runner_secondary_field_disposition']['scientific_primary_result_affected'] is False, 'B8 tie audit disposition drift')
    require(geom['tie_aware_closest_arm_counts'] == {
        'failure_memory': 1,
        'failure_memory+no_memory': 1,
        'failure_memory+no_memory+success_memory': 34,
    }, 'B8 tie-aware geometry drift')
    require(geom['exact_rate_equalities']['all_four_equal_tasks'] == 31, 'B8 all-four equality drift')

    require(b9c.get('paper_id') == PAPER_ID and b9c.get('status') == 'FROZEN_BEFORE_DIAGNOSTIC_COMPUTATION', 'B9 contract drift')
    require(b9.get('paper_id') == PAPER_ID and b9.get('status') == 'B9_DIAGNOSTIC_COMPLETE' and b9.get('provider_calls') == 0, 'B9 result drift')
    require(b9['summary_all_36']['task_count'] == 36 and b9['summary_multi_reference_16']['task_count'] == 16, 'B9 support drift')
    require(abs(b9['summary_all_36']['mean_absolute_success_failure_partial_difference'] - 0.019511) < 1e-12, 'B9 all-task branch diagnostic drift')
    require(abs(b9['summary_multi_reference_16']['mean_absolute_success_failure_partial_difference'] - 0.028274) < 1e-12, 'B9 multi-reference branch diagnostic drift')
    require(b9['headroom']['binary_same_but_partial_success_failure_diff_cells'] == 3, 'B9 hidden-difference count drift')

    incremental_posts = 144
    incremental_usable = 144
    payload = {
        'schema_version': '1.0',
        'artifact_type': 'baseline-aligned-followup-evidence',
        'paper_id': PAPER_ID,
        'status': 'BASELINE_FOLLOWUP_COMPLETE_RAW_TRAJECTORY_AND_ENDPOINT_DIAGNOSTIC',
        'relationship_to_prior_expansion': 'append-only follow-up; prior expansion artifact and its SHA remain unchanged',
        'source_bindings': {key: sha(path) for key, path in PATHS.items()},
        'experiments': {
            'B8_raw_writer_input_trajectory_baseline': {
                'provider_calls': 144,
                'complete_calls': 144,
                'provider_failures': 0,
                'future_tasks': 36,
                'selected_sources': b8c['selected_source_count'],
                'rollouts_per_task': b8c['rollouts_per_task'],
                'mean_absolute_rewrite_vs_raw_effect': b8['summary']['observed_mean_absolute_rewrite_vs_raw_effect'],
                'permutation_p': b8['summary']['three_arm_permutation_p_ge_observed'],
                'practical_floor': b8['summary']['practical_effect_floor'],
                'gate_pass': b8['summary']['primary_gate_pass'],
                'mean_absolute_raw_vs_no_memory': b8['secondary']['mean_absolute_raw_vs_no_memory'],
                'all_four_equal_tasks': geom['exact_rate_equalities']['all_four_equal_tasks'],
                'tie_aware_closest_arm_counts': geom['tie_aware_closest_arm_counts'],
                'runner_tie_biased_secondary_excluded': True,
                'interpretation': 'Relative to the common compact trajectory projection supplied to the memory writer, reward-conditioned rewriting produces a statistically detectable but practically small terminal difference on the same native-retrieval support; the preregistered 0.15 effect floor is missed.',
                'external_baseline_replication_claim': False,
                'baseline_alignment': 'Trajectory Retrieval / long-context controls motivate the raw-experience comparator, but B8 is a C1-internal writer-input trajectory baseline rather than a byte-exact reproduction of an external method.',
            },
            'B9_partial_reference_endpoint_headroom': {
                'provider_calls': 0,
                'rollouts_reused': b9['rollout_count'],
                'future_tasks': b9['summary_all_36']['task_count'],
                'multi_reference_tasks': b9['summary_multi_reference_16']['task_count'],
                'mean_absolute_success_failure_partial_difference_all': b9['summary_all_36']['mean_absolute_success_failure_partial_difference'],
                'mean_absolute_success_failure_partial_difference_multi_reference': b9['summary_multi_reference_16']['mean_absolute_success_failure_partial_difference'],
                'mean_absolute_memory_presence_partial_difference_all': b9['summary_all_36']['mean_absolute_memory_presence_partial_difference'],
                'binary_joint_floor_cells': b9['headroom']['binary_joint_floor_cells'],
                'partial_joint_floor_cells': b9['headroom']['partial_joint_floor_cells'],
                'binary_same_but_partial_branch_diff_cells': b9['headroom']['binary_same_but_partial_success_failure_diff_cells'],
                'confirmatory_gate': None,
                'interpretation': 'The binary endpoint does compress some partial correctness, but a post-hoc fractional-reference diagnostic does not uncover a hidden large success/failure branch separation; it is diagnostic only and cannot replace the preregistered B4/B5 endpoint.',
            },
        },
        'scientific_synthesis_delta': {
            'raw_trajectory_baseline': 'The small native effect is not unique to literal no-memory omission: a stronger raw writer-input trajectory comparator also misses the 0.15 practical-effect floor.',
            'endpoint_headroom': 'Binary floor compression exists, but continuous partial-reference coverage leaves the reward-branch contrast small, strengthening the interpretation that B4 is not merely a scoring-resolution artifact.',
            'transport_boundary': 'The combined native controls now distinguish four representational states—success memory, failure memory, raw trajectory evidence, and omission—without establishing a practically large broad terminal effect.',
        },
        'execution_accounting': {
            'prior_expansion_provider_posts': pa['new_provider_posts'],
            'prior_expansion_scientifically_usable_completions': pa['new_scientifically_usable_provider_completions'],
            'followup_new_provider_posts': incremental_posts,
            'followup_new_scientifically_usable_provider_completions': incremental_usable,
            'followup_zero_provider_diagnostics': 2,
            'baseline_program_provider_posts_total': pa['new_provider_posts'] + incremental_posts,
            'baseline_program_scientifically_usable_completions_total': pa['new_scientifically_usable_provider_completions'] + incremental_usable,
            'baseline_program_scientifically_usable_writer_calls_total': pa['new_scientifically_usable_writer_calls'],
            'baseline_program_scientifically_usable_terminal_rollouts_total': pa['new_scientifically_usable_terminal_rollouts'] + incremental_usable,
            'prior_full_paper_observable_provider_posts_lower_bound_before_baseline_program': pa['prior_full_paper_observable_provider_posts_lower_bound'],
            'full_paper_observable_provider_posts_lower_bound_after_followup': pa['updated_full_paper_observable_provider_posts_lower_bound'] + incremental_posts,
            'training_runs': 0,
            'gpu_runs': 0,
        },
        'claim_boundary_delta': {
            'raw_trajectory_practically_large_rewrite_effect_supported': False,
            'partial_reference_metric_replaces_binary_gate': False,
            'endpoint_resolution_explains_away_native_branch_nonpass': False,
            'external_trajectory_retrieval_method_replication_claimed': False,
            'live_browser_transport_supported': False,
            'population_effect_supported': False,
            'cross_policy_terminal_transfer_status_unchanged': 'SUPPORT_STOP_ZERO_SCIENTIFIC_UNITS',
        },
        'scientific_authority': False,
        'experiment_authority': True,
        'claim_expansion_authority': False,
        'submission_authority': False,
    }
    out = HERE / 'baseline-aligned-followup-evidence.json'
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': payload['status'],
        'experiments': payload['experiments'],
        'execution_accounting': payload['execution_accounting'],
        'claim_boundary_delta': payload['claim_boundary_delta'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
