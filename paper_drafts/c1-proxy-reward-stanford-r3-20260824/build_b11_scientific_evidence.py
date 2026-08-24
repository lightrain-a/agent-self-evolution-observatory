#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RUN = Path('/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b11-outcome-blind-procedural-20260824')
B10 = Path('/home/wyt/code/agent-self-evolution-observatory-c1-proxy-20260824-0226/paper_drafts/c1-proxy-reward-stanford-r3-20260824/transport-localization-evidence.json')
PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
EXPECTED = {
    'contract': 'f95cb2d52bc59b3cfa8b3c0ac4eb4c89b2c48a76d999e6e37f0fa5c6f0f3761c',
    'writer': '2efc0a19c356043e6f3f0f991d47121c3bfbdcf5a1e425a7633ea949d67acdb0',
    'manifest': '7714bbb8d0950762632b3b350b81954800fd0d866cf8d184c73852fe9571f6fc',
    'terminal': 'c13afbb4ce983f9a643cc8e1aa908f6189bc59984f60cae81de89ad82e66ec4c',
    'b10': '89b17623214d429efdefd791cc119b74b5231784815990f6a70f6c725e6598bc',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def req(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def main() -> None:
    paths = {
        'contract': RUN / 'b11-program-contract.json',
        'writer': RUN / 'b11-writer-result.json',
        'manifest': RUN / 'b11-neutral-memory-manifest.json',
        'terminal': RUN / 'b11-terminal-result.json',
        'b10': B10,
    }
    for key, path in paths.items():
        req(path.is_file(), f'missing source: {path}')
        req(sha(path) == EXPECTED[key], f'{key} SHA drift')
    contract, writer, manifest, terminal, b10 = (load(paths[k]) for k in ['contract', 'writer', 'manifest', 'terminal', 'b10'])
    req(contract['paper_id'] == writer['paper_id'] == manifest['paper_id'] == terminal['paper_id'] == PAPER_ID, 'paper identity drift')
    req(writer['status'] == 'B11_WRITER_COMPLETE' and writer['summary']['provider_calls_complete'] == 20 and writer['summary']['provider_failures'] == 0, 'writer stage drift')
    req(manifest['status'] == 'B11_NEUTRAL_MEMORY_MANIFEST_READY' and manifest['required_native_source_count'] == 11, 'manifest drift')
    req(terminal['status'] == 'B11_TERMINAL_EXECUTION_COMPLETE' and terminal['summary']['provider_calls_complete'] == 144 and terminal['summary']['provider_failures'] == 0, 'terminal stage drift')
    req(abs(terminal['summary']['observed_mean_absolute_reward_conditioned_vs_neutral_effect'] - 0.045139) < 1e-12, 'primary effect drift')
    req(abs(terminal['summary']['permutation_p_ge_observed'] - 0.0048) < 1e-12, 'primary p drift')
    req(terminal['summary']['practical_effect_floor'] == 0.15 and terminal['summary']['primary_gate_pass'] is False, 'primary gate drift')
    req(terminal['decision'] == 'REWARD_CONDITIONED_EFFECT_BEYOND_NEUTRAL_REWRITE_NOT_ESTABLISHED', 'decision drift')
    req(b10['execution_accounting']['full_paper_observable_provider_posts_lower_bound_after_b10'] == 1915, 'B10 accounting drift')

    cells = terminal['cell_results']
    req(len(cells) == 36, 'cell count drift')
    nonzero = [x for x in cells if float(x['reward_conditioned_vs_neutral_effect']) > 0]
    sum_effect = sum(float(x['reward_conditioned_vs_neutral_effect']) for x in cells)
    squared = [float(x['reward_conditioned_vs_neutral_effect']) ** 2 for x in cells]
    total_sq = sum(squared)
    ordered = sorted(cells, key=lambda x: float(x['reward_conditioned_vs_neutral_effect']), reverse=True)
    top1_share = 0.0 if not sum_effect else float(ordered[0]['reward_conditioned_vs_neutral_effect']) / sum_effect
    top2_sq_share = 0.0 if total_sq == 0 else sum(float(x['reward_conditioned_vs_neutral_effect']) ** 2 for x in ordered[:2]) / total_sq

    payload = {
        'schema_version': '1.0',
        'artifact_type': 'b11-outcome-blind-structured-control-scientific-evidence',
        'paper_id': PAPER_ID,
        'experiment_id': contract['experiment_id'],
        'status': 'B11_OUTCOME_BLIND_STRUCTURED_CONTROL_COMPLETE',
        'source_bindings': {key: sha(path) for key, path in paths.items()},
        'changed_assumption': contract['changed_assumption'],
        'writer_stage': {
            'provider_calls': 20,
            'complete_calls': 20,
            'provider_failures': 0,
            'required_native_sources_complete': writer['summary']['required_native_sources_complete'],
            'memory_item_count_distribution': writer['summary']['memory_item_count_distribution'],
            'mean_neutral_to_success_token_jaccard_distance': manifest['writer_geometry']['mean_neutral_to_success_token_jaccard_distance'],
            'mean_neutral_to_failure_token_jaccard_distance': manifest['writer_geometry']['mean_neutral_to_failure_token_jaccard_distance'],
            'neutral_closer_to_success_sources': manifest['writer_geometry']['neutral_closer_to_success_sources'],
            'neutral_closer_to_failure_sources': manifest['writer_geometry']['neutral_closer_to_failure_sources'],
            'neutral_title_set_equals_success_sources': manifest['writer_geometry']['neutral_title_set_equals_success_sources'],
            'neutral_title_set_equals_failure_sources': manifest['writer_geometry']['neutral_title_set_equals_failure_sources'],
            'interpretation': 'The outcome-blind writer produces a third structured state rather than copying either reward-conditioned branch; text geometry is descriptive only.',
        },
        'terminal_stage': {
            'provider_calls': 144,
            'complete_calls': 144,
            'provider_failures': 0,
            'future_tasks': 36,
            'mean_absolute_reward_conditioned_vs_neutral_effect': terminal['summary']['observed_mean_absolute_reward_conditioned_vs_neutral_effect'],
            'permutation_p': terminal['summary']['permutation_p_ge_observed'],
            'practical_effect_floor': terminal['summary']['practical_effect_floor'],
            'primary_gate_pass': terminal['summary']['primary_gate_pass'],
            'decision': terminal['decision'],
            'zero_effect_tasks': 36 - len(nonzero),
            'nonzero_effect_tasks': len(nonzero),
            'all_five_arms_equal_tasks': terminal['secondary']['all_five_arms_equal_tasks'],
            'neutral_equals_success_tasks': terminal['secondary']['neutral_equals_success_tasks'],
            'neutral_equals_failure_tasks': terminal['secondary']['neutral_equals_failure_tasks'],
            'neutral_equals_raw_tasks': terminal['secondary']['neutral_equals_raw_tasks'],
            'neutral_equals_no_memory_tasks': terminal['secondary']['neutral_equals_no_memory_tasks'],
            'mean_absolute_neutral_vs_raw': terminal['secondary']['mean_absolute_neutral_vs_raw'],
            'mean_absolute_neutral_vs_no_memory': terminal['secondary']['mean_absolute_neutral_vs_no_memory'],
            'top_effect_task': int(ordered[0]['future_task']),
            'top_effect_value': float(ordered[0]['reward_conditioned_vs_neutral_effect']),
            'top_effect_share_of_absolute_effect_mass': round(top1_share, 6),
            'top_two_squared_effect_mass_share': round(top2_sq_share, 6),
            'nonzero_cells': [{
                'future_task': int(x['future_task']),
                'selected_source_task': int(x['selected_source_task']),
                'success_memory_rate': x['success_memory_rate'],
                'failure_memory_rate': x['failure_memory_rate'],
                'neutral_memory_rate': x['neutral_memory_rate'],
                'raw_trajectory_rate': x['raw_trajectory_rate'],
                'no_memory_rate': x['no_memory_rate'],
                'effect': x['reward_conditioned_vs_neutral_effect'],
            } for x in nonzero],
            'interpretation': 'A statistically detectable three-arm difference exists, but reward-conditioned branch semantics do not achieve the preregistered practically-large effect relative to a same-information outcome-blind structured rewrite. The effect is highly localized rather than broad.',
        },
        'scientific_synthesis_delta': {
            'strongest_simple_reduction': 'The native attenuation cannot be reduced to omission, raw-experience representation, or generic structured rewriting: all three controls miss the same 0.15 practical floor relative to reward-conditioned memories.',
            'stage_resolved_interpretation': 'Reward-conditioned writing robustly changes durable text, but broad native retrieval usually maps success/failure/neutral/raw/no-memory states to the same downstream outcome; B10 independently localizes much of this attenuation before terminal scoring at branch-specific first-action uptake.',
            'forced_vs_native': 'The forced 4x4 intervention remains evidence of latent conditional leverage; B11 strengthens the boundary that latent leverage is not equivalent to broad source-faithful branch-specific uptake.',
        },
        'execution_accounting': {
            'prior_full_paper_observable_provider_posts_lower_bound_after_b10': 1915,
            'b11_writer_provider_posts': 20,
            'b11_terminal_provider_posts': 144,
            'b11_total_provider_posts': 164,
            'b11_scientifically_usable_provider_completions': 164,
            'full_paper_observable_provider_posts_lower_bound_after_b11': 2079,
            'gpu_runs': 0,
            'training_runs': 0,
        },
        'claim_boundary_delta': {
            'practically_large_reward_conditioned_effect_beyond_outcome_blind_structured_rewrite_supported': False,
            'neutral_writer_superiority_supported': False,
            'generic_structured_memory_presence_confirmed': False,
            'forced_intervention_equals_native_transport': False,
            'live_browser_transport_supported': False,
            'population_effect_supported': False,
            'claim_expansion_authority': False,
        },
        'scientific_authority': False,
        'experiment_authority': True,
        'claim_expansion_authority': False,
        'submission_authority': False,
    }
    out = HERE / 'b11-scientific-evidence.json'
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': payload['status'],
        'writer_stage': payload['writer_stage'],
        'terminal_stage': {k: v for k, v in payload['terminal_stage'].items() if k != 'nonzero_cells'},
        'execution_accounting': payload['execution_accounting'],
        'claim_boundary_delta': payload['claim_boundary_delta'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
