#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PAPER = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
REV = 'ICLR-STAGE-RESOLVED-B11-20260824'
TITLE = 'Reward Errors Change Memory Before They Change Policy'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'not object: {path}')
    return obj


def main() -> None:
    qa = load(HERE / 'manuscript-qa.json')
    b11 = load(HERE / 'b11-scientific-evidence.json')
    conc = load(HERE / 'b11-concentration-evidence.json')
    story = load(HERE / 'story-v4-argument-search-20260824.json')
    loc = load(HERE / 'transport-localization-evidence.json')

    if qa.get('status') != 'PASS' or qa.get('revision') != REV or not all(qa['checks'].values()):
        raise RuntimeError('B11 QA not pass')
    if b11.get('status') != 'B11_OUTCOME_BLIND_STRUCTURED_CONTROL_COMPLETE':
        raise RuntimeError('B11 evidence drift')
    if conc.get('status') != 'B11_ZERO_CALL_CONCENTRATION_COMPLETE' or conc.get('provider_calls') != 0:
        raise RuntimeError('B11 concentration drift')
    if story.get('status') != 'STORY_SEARCH_COMPLETE_WINNER_FROZEN' or story['winner']['id'] != 'S1-WRITE-TO-UPTAKE-BOTTLENECK':
        raise RuntimeError('story winner drift')

    w = b11['writer_stage']
    t = b11['terminal_stage']
    a = b11['execution_accounting']
    c = conc['summary']
    if not (w['complete_calls'] == 20 and w['provider_failures'] == 0 and w['required_native_sources_complete'] == 11):
        raise RuntimeError('B11 writer execution drift')
    if not (t['complete_calls'] == 144 and t['provider_failures'] == 0 and abs(t['mean_absolute_reward_conditioned_vs_neutral_effect'] - .045139) < 1e-12 and abs(t['permutation_p'] - .0048) < 1e-12 and t['primary_gate_pass'] is False):
        raise RuntimeError('B11 terminal drift')
    if not (c['top1_effect_task'] == 229 and abs(c['top1_share_of_absolute_effect_mass'] - .615385) < 1e-12 and abs(c['minimum_leave_one_task_out_mean_effect'] - .017857) < 1e-12 and c['sources_with_nonzero_effect'] == 2):
        raise RuntimeError('B11 concentration geometry drift')
    if a['full_paper_observable_provider_posts_lower_bound_after_b11'] != 2079:
        raise RuntimeError('B11 accounting drift')

    receipt = {
        'schema_version': '1.0',
        'artifact_type': 'stage-resolved-b11-revision-receipt',
        'paper_id': PAPER,
        'status': 'STAGE_RESOLVED_B11_INTEGRATED_QA_PASS',
        'revision': REV,
        'title': TITLE,
        'story_winner': {
            'id': story['winner']['id'],
            'score': story['winner']['score'],
            'title': TITLE,
            'forbidden_story_mode': story['system_story_contract']['forbidden_story_mode'],
            'additional_experiment_verdict': story['additional_experiment_adjudication']['verdict'],
            'additional_experiment_provider_calls_avoided': story['additional_experiment_adjudication']['provider_calls_avoided'],
        },
        'paper_pdf_sha256': sha(HERE / 'paper.pdf'),
        'manuscript_qa_sha256': sha(HERE / 'manuscript-qa.json'),
        'b11_scientific_evidence_sha256': sha(HERE / 'b11-scientific-evidence.json'),
        'b11_concentration_evidence_sha256': sha(HERE / 'b11-concentration-evidence.json'),
        'story_v4_argument_search_sha256': sha(HERE / 'story-v4-argument-search-20260824.json'),
        'transport_localization_evidence_sha256': sha(HERE / 'transport-localization-evidence.json'),
        'paper_story_sha256': sha(REPO / 'paper-story-reward-memory.js'),
        'paper_reader_data_sha256': sha(REPO / 'paper-reader-data.js'),
        'qa_checks_passed': sum(qa['checks'].values()),
        'qa_checks_total': len(qa['checks']),
        'abstract_words_approx': qa['abstract_words_approx'],
        'main_text_pages': qa['main_text_pages'],
        'references_begin_page': qa['references_begin_page'],
        'pdf_pages_total': qa['pdf_pages_total'],
        'scientific_delta': {
            'outcome_blind_writer_complete_calls': w['complete_calls'],
            'outcome_blind_writer_required_native_sources': w['required_native_sources_complete'],
            'neutral_to_success_token_jaccard': w['mean_neutral_to_success_token_jaccard_distance'],
            'neutral_to_failure_token_jaccard': w['mean_neutral_to_failure_token_jaccard_distance'],
            'neutral_terminal_complete_calls': t['complete_calls'],
            'reward_conditioned_vs_neutral_effect': t['mean_absolute_reward_conditioned_vs_neutral_effect'],
            'reward_conditioned_vs_neutral_p': t['permutation_p'],
            'practical_floor': t['practical_effect_floor'],
            'gate_pass': t['primary_gate_pass'],
            'zero_effect_tasks': t['zero_effect_tasks'],
            'all_five_arms_equal_tasks': t['all_five_arms_equal_tasks'],
            'top_effect_task': c['top1_effect_task'],
            'top_effect_absolute_mass_share': c['top1_share_of_absolute_effect_mass'],
            'top_effect_squared_mass_share': c['top1_share_of_squared_effect_mass'],
            'leave_top_task_out_mean_effect': c['minimum_leave_one_task_out_mean_effect'],
            'sources_with_any_nonzero_future': c['sources_with_nonzero_effect'],
            'native_selected_sources': c['native_selected_source_count'],
        },
        'mechanism_synthesis': {
            'write': 'Label-only treatment robustly changes durable memory beyond a stronger same-mode wording perturbation.',
            'forced_leverage': 'Direct injection establishes conditional leverage but bypasses native retrieval.',
            'exposure': 'Exact released retrieval can expose the memory broadly after bank expansion.',
            'uptake': 'Native S/F first-action separation is weak, placing attenuation before or at branch-specific policy uptake.',
            'structured_control': 'Outcome-blind structured rewriting yields a distinct textual state but no broad practically-large reward-conditioned terminal effect; the detected small effect is strongly concentrated.',
            'bounded_lesson': 'Memory-text corruption is not equivalent to realized policy transport.',
        },
        'claim_boundary': b11['claim_boundary_delta'],
        'execution_accounting': a,
        'current_revision_new_provider_calls': a['b11_total_provider_posts'],
        'current_revision_new_scientifically_usable_calls': a['b11_scientifically_usable_provider_completions'],
        'current_revision_new_writer_calls': a['b11_writer_provider_posts'],
        'current_revision_new_terminal_rollouts': a['b11_terminal_provider_posts'],
        'full_paper_observable_provider_posts_lower_bound': a['full_paper_observable_provider_posts_lower_bound_after_b11'],
        'scientific_values_changed': True,
        'scientific_claims_expanded': False,
        'external_review_calls_current_revision': 0,
        'external_review_deferred_to_evening': True,
        'canonical_stable_registry_overwritten': False,
        'canonical_note': 'This is a daytime candidate update. Stable PaperRegistry/acceptance projection remains unchanged until the next scheduled external review.',
        'closest_work_delta': {
            'paper': 'Beyond Retrieval: Query-Conditioned Reuse of Long-Horizon Agent Trajectories',
            'arxiv': '2608.12847',
            'use': 'Supports separating retrieval from post-retrieval reuse; C1 remains distinct by intervening on reward-conditioned write-time construction and measuring branch-specific uptake.',
        },
        'scientific_authority': False,
        'experiment_authority': False,
        'claim_expansion_authority': False,
        'submission_authority': False,
    }
    out = HERE / 'stage-resolved-b11-revision-receipt.json'
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': receipt['status'],
        'qa': f"{receipt['qa_checks_passed']}/{receipt['qa_checks_total']}",
        'title': receipt['title'],
        'pdf_sha256': receipt['paper_pdf_sha256'],
        'b11_calls': receipt['current_revision_new_provider_calls'],
        'full_lower_bound': receipt['full_paper_observable_provider_posts_lower_bound'],
        'story_winner': receipt['story_winner'],
        'external_review_calls': 0,
    }, indent=2))


if __name__ == '__main__':
    main()
