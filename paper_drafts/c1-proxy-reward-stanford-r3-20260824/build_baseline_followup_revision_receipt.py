#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PAPER_ID = 'D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE'
QA_REVISION = 'ICLR-BASELINE-ALIGNED-FOLLOWUP-RAW-TRAJECTORY-ENDPOINT-20260824'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise RuntimeError(f'JSON root must be object: {path}')
    return obj


def main() -> None:
    qa = load(HERE / 'manuscript-qa.json')
    prior = load(HERE / 'baseline-aligned-expansion-evidence.json')
    followup = load(HERE / 'baseline-aligned-followup-evidence.json')
    if qa.get('status') != 'PASS' or qa.get('revision') != QA_REVISION:
        raise RuntimeError('current follow-up QA is not PASS')
    if sum(qa['checks'].values()) != len(qa['checks']):
        raise RuntimeError('not all QA checks pass')
    if prior.get('status') != 'BASELINE_ALIGNED_EXPANSION_COMPLETE_WITH_CROSS_POLICY_SUPPORT_STOP':
        raise RuntimeError('prior expansion layer drift')
    if followup.get('status') != 'BASELINE_FOLLOWUP_COMPLETE_RAW_TRAJECTORY_AND_ENDPOINT_DIAGNOSTIC':
        raise RuntimeError('follow-up evidence layer drift')

    fe = followup['experiments']
    acct = followup['execution_accounting']
    if fe['B8_raw_writer_input_trajectory_baseline']['gate_pass'] is not False:
        raise RuntimeError('B8 boundary drift')
    if fe['B9_partial_reference_endpoint_headroom']['confirmatory_gate'] is not None:
        raise RuntimeError('B9 authority drift')
    if acct['followup_new_provider_posts'] != 144 or acct['full_paper_observable_provider_posts_lower_bound_after_followup'] != 1483:
        raise RuntimeError('follow-up accounting drift')

    receipt = {
        'schema_version': '1.0',
        'artifact_type': 'baseline-followup-revision-receipt',
        'paper_id': PAPER_ID,
        'status': 'BASELINE_FOLLOWUP_INTEGRATED_QA_PASS',
        'revision': qa['revision'],
        'title': 'Reward Errors Become Persistent State: Write-Time Causality and Transport Boundaries in Agent Memory',
        'paper_pdf_sha256': sha(HERE / 'paper.pdf'),
        'manuscript_qa_sha256': sha(HERE / 'manuscript-qa.json'),
        'prior_expansion_evidence_sha256': sha(HERE / 'baseline-aligned-expansion-evidence.json'),
        'followup_evidence_sha256': sha(HERE / 'baseline-aligned-followup-evidence.json'),
        'paper_story_sha256': sha(REPO / 'paper-story-reward-memory.js'),
        'paper_reader_data_sha256': sha(REPO / 'paper-reader-data.js'),
        'manuscript_qa_checks_passed': sum(qa['checks'].values()),
        'manuscript_qa_checks_total': len(qa['checks']),
        'abstract_words_approx': qa['abstract_words_approx'],
        'main_text_pages': qa['main_text_pages'],
        'references_begin_page': qa['references_begin_page'],
        'pdf_pages_total': qa['pdf_pages_total'],
        'followup_experiments': followup['experiments'],
        'scientific_synthesis_delta': followup['scientific_synthesis_delta'],
        'claim_boundary_delta': followup['claim_boundary_delta'],
        'execution_accounting': acct,
        'scientific_values_changed': True,
        'scientific_claims_expanded': False,
        'followup_new_provider_calls_exact': qa['new_provider_calls_exact'],
        'followup_new_scientifically_usable_provider_calls': qa['new_scientifically_usable_provider_calls'],
        'followup_new_terminal_rollouts': qa['new_terminal_rollouts'],
        'baseline_program_provider_posts_total': qa['baseline_program_provider_posts_total'],
        'baseline_program_scientifically_usable_completions_total': qa['baseline_program_scientifically_usable_completions_total'],
        'baseline_program_terminal_rollouts_total': qa['baseline_program_terminal_rollouts_total'],
        'full_paper_observable_provider_posts_lower_bound': qa['updated_full_paper_observable_provider_posts_lower_bound'],
        'external_review_calls_current_followup': 0,
        'external_review_deferred_to_evening': True,
        'canonical_stable_registry_overwritten': False,
        'canonical_note': 'This daytime follow-up does not overwrite the stable PaperRegistry/acceptance ledger; the next scheduled external review may adjudicate the candidate later.',
        'build_note': {
            'latex_recompiled': True,
            'references_recompiled': True,
            'figure_sources_changed': False,
            'existing_figures_reused': True,
            'isolated_worktree_build_figures_portability_issue': 'build_figures.py resolves one generated-data path relative to the worktree and cannot locate the shared generated artifact there; no figure data or figure source changed in this follow-up.',
            'paper_has_overfull_boxes': False,
        },
        'scientific_authority': False,
        'experiment_authority': False,
        'claim_expansion_authority': False,
        'submission_authority': False,
    }
    out = HERE / 'baseline-followup-revision-receipt.json'
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': receipt['status'],
        'qa': f"{receipt['manuscript_qa_checks_passed']}/{receipt['manuscript_qa_checks_total']}",
        'pdf_sha256': receipt['paper_pdf_sha256'],
        'followup_new_calls': receipt['followup_new_provider_calls_exact'],
        'baseline_program_calls_total': receipt['baseline_program_provider_posts_total'],
        'full_lower_bound': receipt['full_paper_observable_provider_posts_lower_bound'],
        'external_review_calls_current_followup': 0,
    }, indent=2))


if __name__ == '__main__':
    main()
