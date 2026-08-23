from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_preparation_protocol import evaluate_paper_preparation
_canon_root = os.environ.get('D2_CANON_ROOT', '').strip()
if not _canon_root:
    raise RuntimeError('D2_CANON_ROOT must point to the canonical Research OS root')
CANON = Path(_canon_root)
PID = 'D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK'
PAPER = ROOT / 'paper_drafts/d2-temporal-skill-bottleneck-iclr2027'
PDF = PAPER / 'main.pdf'
CLAIMS = ROOT / 'generated/d2-temporal-skill-bottleneck-claim-ledger.json'
PROBES = ROOT / 'generated/d2-temporal-skill-independent-probes-20260822.json'
SEMANTIC = ROOT / 'generated/d2-temporal-skill-f11-semantic-audit-20260823.json'
SATURATION = ROOT / 'generated/d2-temporal-skill-source-saturation-20260823.json'
QA = ROOT / 'generated/d2-temporal-skill-bottleneck-paper-qa-final-stop.json'
BLIND = ROOT / 'generated/d2-temporal-skill-post-f11-semantic-mock-pc-20260823/BLIND_MANUSCRIPT.json'
AWARE = ROOT / 'generated/d2-temporal-skill-post-f11-semantic-mock-pc-20260823/ARTIFACT_AWARE.json'
MANIFEST = PAPER / 'ARTIFACTS.sha256'
OUT_PACKET = ROOT / 'generated/d2-temporal-skill-postready-final-stop-preparation-packet-20260823.json'
OUT_EVAL = ROOT / 'generated/d2-temporal-skill-postready-final-stop-preparation-evaluation-20260823.json'
OUT_ADJ = ROOT / 'generated/d2-temporal-skill-postready-quality-loop-terminal-adjudication-20260823.json'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aref(path: Path) -> str:
    return 'artifact:sha256:' + sha(path)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def packet() -> dict[str, Any]:
    refs = {
        'pdf': aref(PDF),
        'claims': aref(CLAIMS),
        'probes': aref(PROBES),
        'semantic': aref(SEMANTIC),
        'saturation': aref(SATURATION),
        'qa': aref(QA),
        'manifest': aref(MANIFEST),
        'blind': aref(BLIND),
        'aware': aref(AWARE),
    }
    dimensions = {
        'claim-evidence': {'pass': False, 'evidence_refs': [refs['claims'], refs['probes'], refs['semantic'], refs['aware']]},
        'novelty-positioning': {'pass': True, 'evidence_refs': [refs['pdf'], refs['aware']]},
        'method-experiment': {'pass': True, 'evidence_refs': [refs['pdf'], refs['probes']]},
        'statistics-uncertainty': {'pass': True, 'evidence_refs': [refs['pdf'], refs['probes'], refs['semantic']]},
        'visual-evidence': {'pass': True, 'evidence_refs': [refs['pdf'], refs['qa']]},
        'limitations-scope': {'pass': True, 'evidence_refs': [refs['pdf'], refs['claims'], refs['saturation']]},
        'reproducibility': {'pass': True, 'evidence_refs': [refs['qa'], refs['manifest']]},
        'citation-integrity': {'pass': True, 'evidence_refs': [refs['qa']]},
        'venue-compliance': {'pass': True, 'evidence_refs': [refs['qa'], refs['pdf']]},
    }
    issues = [
        {'issue_id': 'c3-f8-semantic-measurement-robustness-open', 'decision_critical': True},
        {'issue_id': 'c3-broad-family-matched-gates-open', 'decision_critical': True},
        {'issue_id': 'c4-longitudinal-persistence-unexecuted', 'decision_critical': True},
        {'issue_id': 'neutral-generic-control-too-weak', 'decision_critical': True},
        {'issue_id': 'single-model-generality', 'decision_critical': True},
        {'issue_id': 'source-pdf-drift', 'decision_critical': True},
        {'issue_id': 'title-scope-overreach', 'decision_critical': True},
        {'issue_id': 'same-substrate-experiment-loop-risk', 'decision_critical': True},
    ]
    resolved = [
        'neutral-generic-control-too-weak',
        'single-model-generality',
        'source-pdf-drift',
        'title-scope-overreach',
        'same-substrate-experiment-loop-risk',
    ]
    delta = {
        'neutral-generic-control-too-weak': refs['probes'],
        'single-model-generality': refs['probes'],
        'source-pdf-drift': refs['qa'],
        'title-scope-overreach': refs['pdf'],
        'same-substrate-experiment-loop-risk': refs['saturation'],
    }
    return {
        'protocol_version': '1.0',
        'paper_id': PID,
        'packet_role': 'post-ready controlled-intervention quality-loop terminal dry-run; does not supersede canonical R6 publication artifact',
        'claim_expansion_authorized': False,
        'new_experiment_authorized': False,
        'gates': {
            'hierarchical-rubric': {
                'hierarchical_decomposition': True,
                'single_overall_score_is_non_authoritative': True,
                'plan_execution_parity_pass': True,
                'fabricated_result_scan_pass': True,
                'evidence_sufficiency_review_pass': False,
                'dimensions': dimensions,
            },
            'verification-refinement': {
                'verifier_separate_from_refiner': True,
                'verification_against_frozen_contract': True,
                'issues': issues,
                'resolved_issue_ids': resolved,
                'revision_deltas': [{'issue_id': x, 'artifact_ref': delta[x]} for x in resolved],
                'non_improving_revision_reverted': True,
            },
            'citation-integrity': {
                'citations_total': 7,
                'citations_verified': 7,
                'claim_citations_total': 7,
                'claim_citations_primary_source_verified': 7,
                'duplicate_citations_absent': True,
                'orphan_bib_entries_absent': True,
                'citation_placement_review_pass': True,
                'citation_claim_entailment_review_pass': True,
                'hallucinated_citations': 0,
            },
            'visual-story': {
                'main_visuals': 3,
                'each_core_claim_has_main_visual': True,
                'figure_caption_reference_review_pass': True,
                'figure_text_callout_consistency_pass': True,
                'quantitative_visual_source_binding_pass': True,
                'negative_or_boundary_evidence_visible': True,
                'labels_legible_at_final_pdf_scale': True,
                'persistent_visual_contract_present': True,
                'registered_visuals_match_sections': True,
            },
            'reproducibility-bundle': {
                'self_contained_source_bundle': True,
                'clean_environment_compile_pass': True,
                'reproduction_entrypoint_present': True,
                'dependency_environment_manifest_present': True,
                'data_model_provenance_present': True,
                'random_seed_and_nondeterminism_documented': True,
                'evaluation_code_and_protocol_bound': True,
                'artifact_hash_manifest_present': True,
                'numeric_claim_recompute_pass': True,
                'independent_reproduction_check_pass': True,
                'secret_scan_pass': True,
                'source_manifest_ref': refs['manifest'],
            },
            'agent-native-artifact': {
                'layers': {
                    'scientific-logic': {'complete': True, 'artifact_refs': [refs['claims'], refs['probes']]},
                    'executable-specification': {'complete': True, 'artifact_refs': [refs['probes'], refs['manifest']]},
                    'exploration-graph': {'complete': True, 'artifact_refs': [refs['blind'], refs['aware'], refs['saturation']]},
                    'claim-evidence-grounding': {'complete': True, 'artifact_refs': [refs['claims'], refs['probes'], refs['semantic'], refs['qa']]},
                },
                'failed_and_rejected_branches_preserved': True,
                'claim_to_raw_output_roundtrip_pass': True,
            },
            'reader-simulation': {
                'modes': {
                    'blind-manuscript': {'completed': True, 'unresolved_decision_critical': 3},
                    'artifact-aware': {'completed': True, 'unresolved_decision_critical': 3},
                    'figure-first-skimmer': {'completed': True, 'unresolved_decision_critical': 0},
                    'reproducibility-reviewer': {'completed': True, 'unresolved_decision_critical': 0},
                },
                'paper_side_findings_resolved_or_explicitly_accepted': True,
                'review_score_is_not_a_hard_gate': True,
            },
            'submission-package': {
                'venue': 'ICLR 2027',
                'venue_template_and_page_rules_pass': True,
                'anonymous_source_and_pdf_pass': True,
                'metadata_matches_manuscript': True,
                'supplement_and_main_artifact_consistency_pass': True,
                'fresh_directory_source_compile_pass': True,
                'file_size_and_upload_constraints_pass': True,
                'ai_use_disclosure_decision_recorded': True,
                'authorship_and_conflict_checklist_recorded': True,
                'venue_policy_snapshot_current': True,
                'human_only_requirements_recorded': True,
                'external_human_submit_required': True,
                'human_submission_status': 'NOT_REQUESTED',
            },
        },
    }


def main() -> None:
    ledger = load(CANON / 'paper-acceptance' / f'{PID}.json')
    p = packet()
    evaluation = evaluate_paper_preparation(p)
    OUT_PACKET.write_text(json.dumps(p, ensure_ascii=False, indent=2) + '\n')
    OUT_EVAL.write_text(json.dumps(evaluation, ensure_ascii=False, indent=2) + '\n')
    r6 = next(e for e in reversed(ledger['events']) if e.get('event_type') == 'submission-readiness-context-r6')
    current_pdf_sha = sha(PDF)
    r6_pdf_sha = str(r6.get('paper_pdf_sha256') or '')
    if current_pdf_sha == r6_pdf_sha:
        raise RuntimeError('post-ready controlled manuscript unexpectedly byte-identical to R6 publication artifact')
    adjudication = {
        'schema_version': '1.0',
        'paper_id': PID,
        'adjudication_id': 'C06-POSTREADY-CONTROLLED-INTERVENTION-TERMINAL-20260823',
        'current_controlled_manuscript_title': load(CLAIMS).get('title'),
        'current_controlled_manuscript_pdf_sha256': current_pdf_sha,
        'current_controlled_manuscript_qa_pass': load(QA).get('status') == 'PASS',
        'current_controlled_manuscript_qa_checks': load(QA).get('summary', {}).get('checks'),
        'latest_controlled_mock_pc': {
            'blind': {'recommendation': load(BLIND)['review']['recommendation'], 'score': load(BLIND)['review']['score_1_to_10']},
            'artifact_aware': {'recommendation': load(AWARE)['review']['recommendation'], 'score': load(AWARE)['review']['score_1_to_10']},
        },
        'paper_preparation_pass': evaluation['pass'],
        'paper_preparation_passed_gates': evaluation['summary']['passed_gates'],
        'paper_preparation_required_gates': evaluation['summary']['required_gates'],
        'paper_preparation_blockers': evaluation['blockers'],
        'controlled_manuscript_submission_freeze_eligible': False,
        'same_substrate_experiment_expansion_authorized': False,
        'source_saturation': load(SATURATION)['decision'],
        'semantic_robustness_established': load(SEMANTIC)['adjudication']['semantic_robustness_established'],
        'remaining_scientific_debt': {
            'C3': [
                'fresh adequately powered prospective matched evidence is unavailable on the current TimeSage-MT source under the frozen >=16 pair GO rule',
                'F8 deterministic gate is not reproduced by the only valid blinded semantic reviewer',
            ],
            'C4': [
                'first-party TimeSage-EV period-sequential evaluated assets or an equivalent independent skill-write-then-reuse substrate',
            ],
        },
        'canonical_ledger_current_state': ledger['current_state'],
        'canonical_r6_publication_artifact': {
            'paper_pdf_sha256': r6_pdf_sha,
            'artifact_submission_ready': r6.get('artifact_submission_ready'),
            'recommended_immediate_action': r6.get('recommended_immediate_action'),
            'post_repair_mock_pc_scores': r6.get('post_repair_mock_pc_scores'),
            'post_repair_mock_pc_recommendations': r6.get('post_repair_mock_pc_recommendations'),
        },
        'publication_artifact_decision': 'KEEP_R6_AS_CANONICAL_SUBMISSION_ARTIFACT',
        'controlled_quality_loop_decision': 'TERMINAL_HOLD_CURRENT_SUPPORT_DO_NOT_SUPERSEDE_R6',
        'reason': 'The post-ready controlled-intervention manuscript improves causal auditing and exposes new measurement boundaries, but its latest reader simulations remain weak-reject and Paper Preparation fails on unresolved scientific evidence. The canonical R6 source-native artifact has a distinct byte identity and an existing 8/8 preparation pass with 8/8/7 Mock-PC scores. Preserve R6 as the submission artifact and retain this controlled manuscript as append-only research memory until an explicit reopen condition is met.',
        'reopen_conditions': load(SATURATION)['reopen_conditions'],
        'canonical_ledger_modified_by_this_adjudication': False,
        'scientific_authority': False,
        'experiment_authority': False,
        'submission_authority': False,
    }
    OUT_ADJ.write_text(json.dumps(adjudication, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'evaluation': evaluation, 'adjudication': adjudication}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
