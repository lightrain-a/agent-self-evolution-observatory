from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .paper_acceptance_ledger import validate_paper_ledger
from .paper_preparation_protocol import validate_paper_preparation_receipt
from .presubmission_freeze import validate_freeze, verify_current_frozen_artifacts
from .submission_handoff import validate_handoff_ledger, validate_handoff_receipt
from .human_submission_signoff import validate_signoff_ledger, verify_current_signoff
from .venue_submission_receipt import validate_submission_receipt
from .revision_impact_audit import audit_freeze_receipt
from .rebuttal_protocol import validate_rebuttal_receipt, validate_review_set
from .post_decision_learning import validate_learning_receipt, validate_rebuttal_skipped_by_venue_receipt, validate_venue_decision_receipt
from .submission_attempt_history import build_attempt_history
from .submission_attempt_lineage import public_attempt_summary, validate_attempt_ledger
from .submission_attempt_workflow import current_attempt_workflow_summary, validate_attempt_workflow_ledger
from .scientific_reopen_protocol import public_scientific_reopen_summary, validate_scientific_reopen_ledger
from .reopened_scientific_contract import find_contract_by_handoff, public_reopened_contract_summary
from .reopened_scientific_problem_gate import load_latest_reopen_problem_gate, public_reopen_problem_gate_summary
from .reopened_scientific_method_design import public_reopen_method_summary
from .reopened_scientific_experiment_blueprint import public_reopen_blueprint_summary
from .reopened_local_validation_authorization import public_local_validation_authorization
from .reopened_pre_experiment_adapter import public_reopened_pre_experiment
from .reopened_experiment_lease_request import public_experiment_lease_request
from .reopened_experiment_lease import public_reopened_experiment_lease

DEFAULT_ROOT = Path('/data/wyt/agent-self-evolution-observatory')


def digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def latest(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(row.get('events') or []):
        if isinstance(event, dict) and event.get('event_type') == event_type:
            return event
    return {}


def blocker_group(value: str) -> str:
    text = str(value)
    if any(token in text for token in ('claim-evidence', 'method-experiment', 'evidence_sufficiency', 'unresolved-critical')):
        return 'DECISIVE_EVIDENCE'
    if 'statistics-uncertainty' in text:
        return 'STATISTICS_UNCERTAINTY'
    if 'plan_execution_parity' in text:
        return 'PLAN_EXECUTION_PARITY'
    if 'visual' in text:
        return 'VISUAL_CONTRACT'
    if 'reproducibility' in text:
        return 'REPRODUCIBILITY'
    if 'agent-native' in text or 'claim-raw' in text:
        return 'CLAIM_RAW_GROUNDING'
    if 'reader-' in text:
        return 'READER_SIMULATION'
    if 'submission-package' in text or 'venue-compliance' in text:
        return 'VENUE_HANDOFF'
    return 'OTHER'


def next_actions(groups: list[str]) -> list[str]:
    table = {
        'DECISIVE_EVIDENCE': 'close decision-critical claim-evidence gaps; support unavailability is support debt, not scientific counterevidence',
        'STATISTICS_UNCERTAINTY': 'complete the uncertainty/sensitivity analysis required by the retained claims',
        'PLAN_EXECUTION_PARITY': 'close the gap between the frozen paper plan and the evidence actually executed',
        'VISUAL_CONTRACT': 'bind each core claim/boundary to a main-text visual contract',
        'REPRODUCIBILITY': 'build a self-contained source/reproduction bundle and pass clean-room compile/recompute',
        'CLAIM_RAW_GROUNDING': 'close claim-to-raw-evidence roundtrip in the agent-native artifact',
        'READER_SIMULATION': 'complete figure-first and reproducibility readers and close critical objections',
        'VENUE_HANDOFF': 'complete venue policy, AI-use/authorship checklist, supplement consistency, and fresh-source compile',
        'OTHER': 'inspect remaining preparation blockers before human handoff',
    }
    return [table[group] for group in groups]


def current_policy_sha(root: Path) -> str:
    index = root / 'paper-submission-freezes/current-freeze-index.json'
    if not index.exists():
        return ''
    try:
        payload = json.loads(index.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return ''
    return str(payload.get('venue_policy_snapshot_sha256') or '')


def freeze_state(root: Path, paper_id: str, preparation_receipt_sha: str) -> dict[str, Any]:
    path = root / 'paper-submission-freezes' / f'{paper_id}.json'
    if not path.exists():
        return {'status': 'MACHINE_FREEZE_PENDING', 'integrity_pass': False, 'errors': ['freeze-receipt-missing'], 'freeze_sha256': ''}
    try:
        row = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'MACHINE_FREEZE_STALE', 'integrity_pass': False, 'errors': ['freeze-ledger-unreadable'], 'freeze_sha256': ''}
    structural = validate_freeze(row)
    event = latest(row, 'pre-submission-freeze')
    receipt = event.get('receipt') if isinstance(event.get('receipt'), dict) else {}
    errors = list(structural)
    errors.extend(verify_current_frozen_artifacts(row))
    if preparation_receipt_sha and receipt.get('paper_preparation_receipt_sha256') != preparation_receipt_sha:
        errors.append('freeze-preparation-receipt-stale')
    policy_sha = current_policy_sha(root)
    if policy_sha and receipt.get('venue_policy_snapshot_sha256') != policy_sha:
        errors.append('freeze-venue-policy-stale')
    errors = list(dict.fromkeys(errors))
    return {
        'status': 'MACHINE_FROZEN_CURRENT' if not errors else 'MACHINE_FREEZE_STALE',
        'integrity_pass': not errors,
        'errors': errors,
        'freeze_sha256': str(receipt.get('freeze_sha256') or ''),
    }


def handoff_state(root: Path, paper_id: str, freeze_sha256: str) -> dict[str, Any]:
    path = root / 'paper-submission-handoffs' / f'{paper_id}.json'
    if not path.exists():
        return {'status': 'MACHINE_HANDOFF_PENDING', 'integrity_pass': False, 'errors': ['handoff-receipt-missing'], 'handoff_sha256': ''}
    try:
        row = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'MACHINE_HANDOFF_STALE', 'integrity_pass': False, 'errors': ['handoff-ledger-unreadable'], 'handoff_sha256': ''}
    errors = list(validate_handoff_ledger(row))
    event = latest(row, 'machine-submission-handoff')
    receipt = event.get('receipt') if isinstance(event.get('receipt'), dict) else {}
    if not receipt or not validate_handoff_receipt(receipt):
        errors.append('handoff-receipt-invalid')
    if freeze_sha256 and receipt.get('freeze_sha256') != freeze_sha256:
        errors.append('handoff-freeze-stale')
    errors = list(dict.fromkeys(errors))
    return {
        'status': 'MACHINE_HANDOFF_CURRENT' if not errors else 'MACHINE_HANDOFF_STALE',
        'integrity_pass': not errors,
        'errors': errors,
        'handoff_sha256': str(receipt.get('handoff_sha256') or ''),
    }


def revision_impact_state(root: Path, paper_id: str, freeze_status: str) -> dict[str, Any]:
    path = root / 'paper-submission-freezes' / f'{paper_id}.json'
    if not path.exists():
        return {'status': 'NOT_AVAILABLE', 'impact_classes': [], 'minimum_rerun_paper_preparation_gates': [], 'minimum_rerun_paper_acceptance_checks': []}
    try:
        row = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'UNREADABLE', 'impact_classes': ['UNKNOWN'], 'minimum_rerun_paper_preparation_gates': [], 'minimum_rerun_paper_acceptance_checks': []}
    event = latest(row, 'pre-submission-freeze')
    receipt = event.get('receipt') if isinstance(event.get('receipt'), dict) else {}
    if not receipt:
        return {'status': 'NOT_AVAILABLE', 'impact_classes': [], 'minimum_rerun_paper_preparation_gates': [], 'minimum_rerun_paper_acceptance_checks': []}
    result = audit_freeze_receipt(receipt)
    if freeze_status == 'MACHINE_FROZEN_CURRENT' and result.get('status') != 'NO_CHANGE':
        result = dict(result)
        result['status'] = 'INCONSISTENT_FREEZE_AUDIT'
    return result


def human_signoff_state(root: Path, paper_id: str, machine_handoff_status: str) -> dict[str, Any]:
    if machine_handoff_status != 'MACHINE_HANDOFF_CURRENT':
        return {'status': 'NOT_ELIGIBLE', 'integrity_pass': False, 'errors': [], 'signoff_sha256': ''}
    signoff_path = root / 'paper-human-signoffs' / f'{paper_id}.json'
    if not signoff_path.exists():
        return {'status': 'PENDING_HUMAN_CONFIRMATION', 'integrity_pass': False, 'errors': [], 'signoff_sha256': ''}
    handoff_path = root / 'paper-submission-handoffs' / f'{paper_id}.json'
    freeze_path = root / 'paper-submission-freezes' / f'{paper_id}.json'
    try:
        signoff = json.loads(signoff_path.read_text(encoding='utf-8'))
        handoff = json.loads(handoff_path.read_text(encoding='utf-8'))
        freeze = json.loads(freeze_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'HUMAN_SIGNOFF_STALE', 'integrity_pass': False, 'errors': ['human-signoff-ledger-unreadable'], 'signoff_sha256': ''}
    errors = list(validate_signoff_ledger(signoff))
    errors.extend(verify_current_signoff(signoff, handoff, freeze))
    errors = list(dict.fromkeys(errors))
    event = latest(signoff, 'human-submission-signoff')
    receipt = event.get('receipt') if isinstance(event.get('receipt'), dict) else {}
    return {
        'status': 'HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING' if not errors else 'HUMAN_SIGNOFF_STALE',
        'integrity_pass': not errors,
        'errors': errors,
        'signoff_sha256': str(receipt.get('signoff_sha256') or ''),
    }


def review_intake_state(root: Path, paper_id: str, submission_receipt_sha256: str, state: str) -> dict[str, Any]:
    if state not in {'SUBMITTED', 'REBUTTAL', 'LEARN'}:
        return {'status': 'NOT_ELIGIBLE', 'review_set_sha256': '', 'review_count': 0, 'errors': []}
    path = root / 'paper-review-intake' / f'{paper_id}.json'
    if not path.exists():
        return {'status': 'AWAITING_VENUE_REVIEWS', 'review_set_sha256': '', 'review_count': 0, 'errors': []}
    try:
        row = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'status': 'REVIEW_INTAKE_STALE', 'review_set_sha256': '', 'review_count': 0, 'errors': ['review-intake-ledger-unreadable']}
    event = latest(row, 'review-set')
    review_set = event.get('review_set') if isinstance(event.get('review_set'), dict) else {}
    errors=[]
    if not review_set or not validate_review_set(review_set): errors.append('review-set-invalid')
    if submission_receipt_sha256 and review_set.get('submission_receipt_sha256') != submission_receipt_sha256: errors.append('review-set-submission-stale')
    return {
        'status': 'REVIEW_SET_CURRENT' if not errors else 'REVIEW_INTAKE_STALE',
        'review_set_sha256': str(review_set.get('review_set_sha256') or ''),
        'review_count': int(review_set.get('review_count') or 0),
        'errors': errors,
    }


def rebuttal_state(row: Mapping[str, Any], review_set_sha256: str) -> dict[str, Any]:
    state=str(row.get('current_state') or '')
    event=latest(row,'rebuttal-preparation')
    receipt=event.get('receipt') if isinstance(event.get('receipt'),dict) else {}
    skip_event=latest(row,'rebuttal-skipped-by-venue'); skip=skip_event.get('receipt') if isinstance(skip_event.get('receipt'),dict) else {}
    decision_event=latest(row,'venue-decision'); decision=decision_event.get('receipt') if isinstance(decision_event.get('receipt'),dict) else {}
    valid=bool(receipt) and str(receipt.get('contract_sha256') or '')==str(row.get('contract_sha256') or '') and validate_rebuttal_receipt(receipt)
    skip_valid=bool(skip) and str(skip.get('contract_sha256') or '')==str(row.get('contract_sha256') or '') and validate_rebuttal_skipped_by_venue_receipt(skip)
    decision_valid=bool(decision) and str(decision.get('contract_sha256') or '')==str(row.get('contract_sha256') or '') and validate_venue_decision_receipt(decision)
    skip_lineage_ok=skip_valid and decision_valid and decision.get('decision_phase')=='PRE_REBUTTAL_TERMINAL' and decision.get('rebuttal_available') is False and skip.get('venue_decision_sha256')==decision.get('venue_decision_sha256')
    errors=[]
    if receipt and not valid: errors.append('rebuttal-receipt-invalid')
    if skip and not skip_valid: errors.append('rebuttal-skip-receipt-invalid')
    if valid and review_set_sha256 and receipt.get('review_set_sha256')!=review_set_sha256: errors.append('rebuttal-review-set-stale')
    summary=receipt.get('summary') if isinstance(receipt.get('summary'),dict) else {}
    if state=='REBUTTAL': status='REBUTTAL_ACTIVE' if valid and not errors and receipt.get('pass') is True else ('REBUTTAL_SKIPPED_BY_VENUE' if skip_lineage_ok and not errors else 'REBUTTAL_RECEIPT_INVALID')
    elif state=='SUBMITTED': status='REBUTTAL_PREPARED_TRANSITION_PENDING' if valid and not errors and receipt.get('pass') is True else ('REBUTTAL_SKIPPED_TRANSITION_PENDING' if skip_lineage_ok and not errors else 'REBUTTAL_PREPARATION_PENDING')
    elif state=='LEARN' and skip_lineage_ok: status='REBUTTAL_SKIPPED_BY_VENUE'
    else: status='NOT_ELIGIBLE'
    return {
        'status':status,'valid':(valid and not errors and receipt.get('pass') is True) or (skip_lineage_ok and not errors),'errors':errors,
        'rebuttal_receipt_sha256':str(receipt.get('rebuttal_receipt_sha256') or ''),
        'rebuttal_skip_sha256':str(skip.get('rebuttal_skip_sha256') or ''),
        'review_set_sha256':str(receipt.get('review_set_sha256') or ''),
        'reviews':int(summary.get('reviews') or 0),'objections':int(summary.get('objections') or 0),
        'decision_critical':int(summary.get('decision_critical') or 0),
        'missing_decisive_evidence':int(summary.get('missing_decisive_evidence') or 0),
        'new_claim_requests':int(summary.get('new_claim_requests') or 0),
    }


def learning_state(row: Mapping[str, Any]) -> dict[str, Any]:
    state=str(row.get('current_state') or '')
    d_event=latest(row,'venue-decision'); decision=d_event.get('receipt') if isinstance(d_event.get('receipt'),dict) else {}
    l_event=latest(row,'post-decision-learning'); learning=l_event.get('receipt') if isinstance(l_event.get('receipt'),dict) else {}
    decision_valid=bool(decision) and str(decision.get('contract_sha256') or '')==str(row.get('contract_sha256') or '') and validate_venue_decision_receipt(decision)
    learning_valid=bool(learning) and str(learning.get('contract_sha256') or '')==str(row.get('contract_sha256') or '') and validate_learning_receipt(learning)
    lineage_ok=decision_valid and learning_valid and learning.get('venue_decision_sha256')==decision.get('venue_decision_sha256')
    if state=='LEARN': status='LEARN_COMPLETE' if lineage_ok and learning.get('pass') is True else 'LEARN_RECEIPT_INVALID'
    elif state=='REBUTTAL': status='AWAITING_FINAL_VENUE_DECISION' if not decision_valid else ('LEARNING_PREPARED_TRANSITION_PENDING' if lineage_ok and learning.get('pass') is True else 'POST_DECISION_LEARNING_PENDING')
    else: status='NOT_ELIGIBLE'
    summary=learning.get('summary') if isinstance(learning.get('summary'),dict) else {}
    return {
        'status':status,'decision':str(decision.get('decision') or ''),'decision_valid':decision_valid,
        'venue_decision_sha256':str(decision.get('venue_decision_sha256') or ''),
        'learning_valid':lineage_ok,'learning_receipt_sha256':str(learning.get('learning_receipt_sha256') or ''),
        'lessons':int(summary.get('lessons') or 0),'scientific_diagnostic_only':int(summary.get('scientific_diagnostic_only') or 0),
        'paper_process_lessons':int(summary.get('paper_process_lessons') or 0),
    }


def submission_attempt_state(root: Path, paper_id: str, paper_state: str) -> dict[str, Any]:
    empty = {
        'status': 'ATTEMPT_NOT_PLANNED' if paper_state == 'LEARN' else 'NOT_ELIGIBLE',
        'attempts': 0,
        'latest_attempt_id': '',
        'latest_attempt_sha256': '',
        'latest_attempt_type': '',
        'target_venue': '',
        'machine_preparation_eligible': False,
        'requires_explicit_scientific_reopen': False,
        'parent_submission_bytes_immutable': True,
        'validation_errors': [],
    }
    path = root / 'paper-submission-attempts' / f'{paper_id}.json'
    if not path.exists():
        return empty
    try:
        row = json.loads(path.read_text(encoding='utf-8'))
        errors = validate_attempt_ledger(row)
        summary = public_attempt_summary(row)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {**empty, 'status': 'ATTEMPT_LEDGER_INVALID', 'validation_errors': ['attempt-ledger-unreadable']}
    if errors:
        return {**empty, **summary, 'status': 'ATTEMPT_LEDGER_INVALID', 'validation_errors': errors}
    return {**empty, **summary, 'status': str(summary.get('latest_status') or empty['status'])}


def submission_attempt_workflow_state(root: Path, attempt: Mapping[str, Any]) -> dict[str, Any]:
    empty = {
        'status': 'ATTEMPT_WORKFLOW_NOT_STARTED' if int(attempt.get('attempts') or 0) > 0 and attempt.get('machine_preparation_eligible') is True else 'NOT_ELIGIBLE',
        'attempt_id': str(attempt.get('latest_attempt_id') or ''),
        'attempt_sha256': str(attempt.get('latest_attempt_sha256') or ''),
        'preparation_sha256': '',
        'freeze_sha256': '',
        'handoff_sha256': '',
        'signoff_sha256': '',
        'submission_conflict_guard_sha256': '',
        'submission_conflict_guard_status': '',
        'submission_conflict_count': 0,
        'submission_receipt_sha256': '',
        'venue_submission_id': '',
        'submitted_at': '',
        'actual_submission_status': 'NOT_SUBMITTED',
        'review_set_sha256': '',
        'review_count': 0,
        'rebuttal_receipt_sha256': '',
        'rebuttal_missing_decisive_evidence': 0,
        'rebuttal_new_claim_requests': 0,
        'venue_decision_sha256': '',
        'venue_decision': '',
        'decision_phase': '',
        'rebuttal_skip_sha256': '',
        'learning_receipt_sha256': '',
        'learning_lessons': 0,
        'learning_scientific_diagnostic_only': 0,
        'frozen_artifacts': 0,
        'freeze_drift_errors': [],
        'validation_errors': [],
        'human_confirmation_status': '',
        'parent_submission_bytes_immutable': True,
    }
    attempt_id = str(attempt.get('latest_attempt_id') or '')
    if not attempt_id:
        return empty
    path = root / 'paper-submission-attempt-workflows' / f'{attempt_id}.json'
    if not path.exists():
        return empty
    try:
        row = json.loads(path.read_text(encoding='utf-8'))
        errors = validate_attempt_workflow_ledger(row)
        summary = current_attempt_workflow_summary(row)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {**empty, 'status': 'ATTEMPT_WORKFLOW_INVALID', 'validation_errors': ['attempt-workflow-ledger-unreadable']}
    if errors:
        return {**empty, **summary, 'status': 'ATTEMPT_WORKFLOW_INVALID', 'validation_errors': errors}
    if str(summary.get('attempt_sha256') or '') != str(attempt.get('latest_attempt_sha256') or ''):
        return {**empty, **summary, 'status': 'ATTEMPT_WORKFLOW_INVALID', 'validation_errors': ['attempt-workflow-plan-lineage-mismatch']}
    return {**empty, **summary}


def scientific_reopen_state(root: Path, paper_id: str, attempt: Mapping[str, Any]) -> dict[str, Any]:
    empty = {
        'status': 'SCIENTIFIC_REOPEN_PROPOSAL_REQUIRED' if attempt.get('requires_explicit_scientific_reopen') is True else 'NOT_ELIGIBLE',
        'attempt_sha256': str(attempt.get('latest_attempt_sha256') or ''),
        'proposal_sha256': '',
        'authorization_sha256': '',
        'authorization_scope': '',
        'external_scientific_authority_confirmed': False,
        'research_os_handoff_sha256': '',
        'new_contract_seed_id': '',
        'destination_gate': '',
        'new_contract_creation_eligible': False,
        'new_scientific_contract_required': attempt.get('requires_explicit_scientific_reopen') is True,
        'existing_scientific_contract_immutable': True,
        'automatic_contract_creation_authorized': False,
        'claim_expansion_authorized': False,
        'new_experiment_authorized': False,
        'gpu_execution_authorized': False,
        'validation_errors': [],
        'new_contract': {**public_reopened_contract_summary({}), 'problem_gate': public_reopen_problem_gate_summary({}), 'method_design': public_reopen_method_summary(Path('/nonexistent'), ''), 'experiment_blueprint': public_reopen_blueprint_summary(Path('/nonexistent'), ''), 'local_validation_authorization': public_local_validation_authorization(Path('/nonexistent'), ''), 'pre_experiment': public_reopened_pre_experiment(Path('/nonexistent'), ''), 'experiment_lease_request': public_experiment_lease_request(Path('/nonexistent'), ''), 'experiment_lease': public_reopened_experiment_lease(Path('/nonexistent'), '')},
    }
    if attempt.get('requires_explicit_scientific_reopen') is not True:
        return empty
    path = root / 'paper-scientific-reopen' / f'{paper_id}.json'
    if not path.exists():
        return empty
    try:
        row = json.loads(path.read_text(encoding='utf-8'))
        errors = validate_scientific_reopen_ledger(row)
        summary = public_scientific_reopen_summary(row, str(attempt.get('latest_attempt_sha256') or ''))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {**empty, 'status': 'SCIENTIFIC_REOPEN_LEDGER_INVALID', 'validation_errors': ['scientific-reopen-ledger-unreadable']}
    if errors:
        return {**empty, **summary, 'status': 'SCIENTIFIC_REOPEN_LEDGER_INVALID', 'validation_errors': errors}
    projected = {**empty, **summary}
    handoff_sha = str(projected.get('research_os_handoff_sha256') or '')
    if handoff_sha:
        try:
            contract = find_contract_by_handoff(root / 'scientific-contracts', handoff_sha)
            contract_summary = public_reopened_contract_summary(contract)
        except Exception:
            contract_summary = {**public_reopened_contract_summary({}), 'status': 'NEW_SCIENTIFIC_CONTRACT_INVALID'}
        if contract_summary.get('status') == 'NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED':
            gate_receipt = load_latest_reopen_problem_gate(root / 'scientific-contract-problem-gates', str(contract_summary.get('contract_id') or ''))
            gate_summary = public_reopen_problem_gate_summary(gate_receipt)
            method_summary = public_reopen_method_summary(root / 'scientific-contract-method-design', str(contract_summary.get('contract_id') or '')) if gate_summary.get('status') == 'REOPEN_PROBLEM_GATE_PASS_METHOD_DESIGN_REVIEW_ELIGIBLE' else public_reopen_method_summary(Path('/nonexistent'), '')
            blueprint_summary = public_reopen_blueprint_summary(root / 'scientific-contract-experiment-blueprints', str(contract_summary.get('contract_id') or '')) if method_summary.get('status') == 'REOPEN_METHOD_REVIEW_PASS_BLUEPRINT_DESIGN_ELIGIBLE' else public_reopen_blueprint_summary(Path('/nonexistent'), '')
            local_auth_summary = public_local_validation_authorization(root / 'scientific-contract-local-validation-authority', str(contract_summary.get('contract_id') or '')) if blueprint_summary.get('status') == 'REOPEN_BLUEPRINT_REVIEW_PASS_LOCAL_VALIDATION_AUTHORIZATION_ELIGIBLE' else public_local_validation_authorization(Path('/nonexistent'), '')
            pre_experiment_summary = public_reopened_pre_experiment(root / 'scientific-contract-pre-experiment', str(contract_summary.get('contract_id') or '')) if local_auth_summary.get('status') == 'LOCAL_VALIDATION_AUTHORIZED_PRE_EXPERIMENT_COMPILER_REQUIRED' else public_reopened_pre_experiment(Path('/nonexistent'), '')
            lease_request_summary = public_experiment_lease_request(root / 'scientific-contract-experiment-lease-requests', str(contract_summary.get('contract_id') or '')) if pre_experiment_summary.get('status') == 'PRE_EXPERIMENT_COMPILER_PASS_EXPERIMENT_LEASE_REQUIRED' else public_experiment_lease_request(Path('/nonexistent'), '')
            lease_summary = public_reopened_experiment_lease(root / 'scientific-contract-experiment-leases', str(contract_summary.get('contract_id') or ''), authority_root=root) if lease_request_summary.get('status') == 'EXPERIMENT_LEASE_REQUEST_READY_EXPLICIT_ACQUIRE_REQUIRED' else public_reopened_experiment_lease(Path('/nonexistent'), '')
            contract_summary = {**contract_summary, 'problem_gate': gate_summary, 'method_design': method_summary, 'experiment_blueprint': blueprint_summary, 'local_validation_authorization': local_auth_summary, 'pre_experiment': pre_experiment_summary, 'experiment_lease_request': lease_request_summary, 'experiment_lease': lease_summary}
            if gate_summary['status'] == 'REOPEN_PROBLEM_GATE_REQUIRED':
                projected['status'] = 'NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED'
            elif gate_summary['status'] == 'REOPEN_PROBLEM_GATE_PASS_METHOD_DESIGN_REVIEW_ELIGIBLE':
                if method_summary.get('status') == 'REOPEN_METHOD_REVIEW_PASS_BLUEPRINT_DESIGN_ELIGIBLE':
                    if pre_experiment_summary.get('status') == 'PRE_EXPERIMENT_COMPILER_PASS_EXPERIMENT_LEASE_REQUIRED':
                        projected['status'] = lease_summary.get('status') if lease_summary.get('status') != 'EXPERIMENT_LEASE_ACQUIRE_REQUIRED' else lease_request_summary.get('status')
                    else:
                        projected['status'] = pre_experiment_summary.get('status') if local_auth_summary.get('status') == 'LOCAL_VALIDATION_AUTHORIZED_PRE_EXPERIMENT_COMPILER_REQUIRED' else (local_auth_summary.get('status') if blueprint_summary.get('status') == 'REOPEN_BLUEPRINT_REVIEW_PASS_LOCAL_VALIDATION_AUTHORIZATION_ELIGIBLE' else blueprint_summary.get('status'))
                else:
                    projected['status'] = method_summary.get('status') or 'REOPEN_METHOD_DESIGN_REQUIRED'
            else:
                projected['status'] = gate_summary['status']
        projected['new_contract'] = contract_summary
    return projected


def project(path: Path, root: Path) -> dict[str, Any]:
    row = json.loads(path.read_text(encoding='utf-8'))
    paper_id = str(row.get('paper_id') or path.stem)
    contract = row.get('contract') or {}
    recorded = str(row.get('contract_sha256') or '')
    contract_ok = bool(recorded) and digest(contract) == recorded
    ledger_errors = validate_paper_ledger(row)

    prep_event = latest(row, 'paper-preparation')
    prep_receipt = prep_event.get('receipt') if isinstance(prep_event.get('receipt'), dict) else {}
    prep_ok = bool(prep_receipt) and validate_paper_preparation_receipt(prep_receipt) and prep_receipt.get('contract_sha256') == recorded
    if prep_ok:
        preparation = 'PASS' if prep_receipt.get('pass') is True else 'BLOCKED'
    elif row.get('current_state') == 'SUBMISSION_READY':
        preparation = 'LEGACY_PENDING'
    else:
        preparation = 'NOT_ELIGIBLE'

    blockers = list(prep_receipt.get('blockers') or []) if prep_ok else ([] if preparation != 'LEGACY_PENDING' else ['paper-preparation-receipt-missing'])
    groups: list[str] = []
    for blocker in blockers:
        group = blocker_group(blocker)
        if group not in groups:
            groups.append(group)

    state = str(row.get('current_state') or '')
    lineage_ready = state in {'SUBMISSION_READY', 'SUBMITTED', 'REBUTTAL', 'LEARN'} and preparation == 'PASS' and contract_ok and not ledger_errors
    base_ready = state == 'SUBMISSION_READY' and lineage_ready
    freeze = freeze_state(root, paper_id, str(prep_receipt.get('receipt_sha256') or '')) if lineage_ready else {
        'status': 'PREPARATION_BLOCKED' if preparation == 'BLOCKED' else 'NOT_ELIGIBLE',
        'integrity_pass': False,
        'errors': [],
        'freeze_sha256': '',
    }
    if lineage_ready and freeze['status'] == 'MACHINE_FROZEN_CURRENT':
        machine_handoff = handoff_state(root, paper_id, freeze['freeze_sha256'])
    else:
        machine_handoff = {
            'status': 'PREPARATION_BLOCKED' if preparation == 'BLOCKED' else 'NOT_ELIGIBLE',
            'integrity_pass': False,
            'errors': [],
            'handoff_sha256': '',
        }
    handoff = machine_handoff['status'] == 'MACHINE_HANDOFF_CURRENT'
    impact = revision_impact_state(root, paper_id, freeze['status']) if lineage_ready else {'status': 'NOT_AVAILABLE', 'impact_classes': [], 'minimum_rerun_paper_preparation_gates': [], 'minimum_rerun_paper_acceptance_checks': []}
    human_signoff = human_signoff_state(root, paper_id, machine_handoff['status'])
    actual_event = latest(row, 'actual-submission')
    actual_receipt = actual_event.get('receipt') if isinstance(actual_event.get('receipt'), dict) else {}
    actual_valid = bool(actual_receipt) and str(actual_receipt.get('contract_sha256') or '') == recorded and validate_submission_receipt(actual_receipt)
    actual_submission_status = 'VENUE_SUBMISSION_CONFIRMED' if state in {'SUBMITTED','REBUTTAL','LEARN'} and actual_valid else ('SUBMITTED_RECEIPT_INVALID' if state in {'SUBMITTED','REBUTTAL','LEARN'} else ('VENUE_SUBMISSION_RECEIPT_RECORDED_TRANSITION_PENDING' if actual_valid else 'NOT_SUBMITTED'))
    review_intake=review_intake_state(root,paper_id,str(actual_receipt.get('submission_receipt_sha256') or ''),state)
    rebuttal=rebuttal_state(row,review_intake['review_set_sha256'])
    if rebuttal['status'] in {'REBUTTAL_SKIPPED_TRANSITION_PENDING','REBUTTAL_SKIPPED_BY_VENUE'}:
        review_intake={**review_intake,'status':'REVIEW_NOT_REQUIRED_VENUE_TERMINAL','review_count':0,'errors':[]}
    learning=learning_state(row)
    attempt=submission_attempt_state(root,paper_id,state)
    attempt_workflow=submission_attempt_workflow_state(root,attempt)
    attempt_history=build_attempt_history(paper_id,root/'paper-submission-attempts',root/'paper-submission-attempt-workflows')
    scientific_reopen=scientific_reopen_state(root,paper_id,attempt)
    actions = next_actions(groups)
    if state == 'LEARN':
        if learning['status']!='LEARN_COMPLETE':
            actions=['LEARN state has invalid decision/learning lineage; stop reuse until repaired']
        elif attempt['status']=='ATTEMPT_NOT_PLANNED':
            actions=['post-decision learning is complete; plan any resubmission or camera-ready as a new immutable child attempt, never by editing the parent submission lineage']
        elif attempt['status']=='ATTEMPT_LEDGER_INVALID':
            actions=['submission-attempt lineage is invalid; stop child preparation until the append-only attempt ledger is repaired']
        elif attempt['requires_explicit_scientific_reopen']:
            if scientific_reopen['status']=='SCIENTIFIC_REOPEN_PROPOSAL_REQUIRED':
                actions=['the child attempt requests a scientific change; record a scientific-reopen proposal bound to the old contract and child lineage, without authorizing experiments or GPU work']
            elif scientific_reopen['status']=='SCIENTIFIC_REOPEN_PROPOSED_EXTERNAL_AUTHORITY_REQUIRED':
                actions=['scientific reopen is proposed; await explicit external PI/human scientific authority. The old contract remains immutable and no experiment/GPU authority exists']
            elif scientific_reopen['status']=='EXTERNAL_SCIENTIFIC_REOPEN_CONFIRMED_NEW_CONTRACT_REQUIRED':
                actions=['external scientific reopen authority is recorded only for creating a new scientific contract. Compile the content-addressed Research OS handoff before contract creation; the old attempt remains blocked']
            elif scientific_reopen['status']=='RESEARCH_OS_NEW_CONTRACT_HANDOFF_READY':
                actions=['the approved reopen is compiled into a Research OS new-contract seed. Supply an explicit new-contract spec and create the immutable child scientific contract; method, P0, experiment, and GPU authority remain false']
            elif scientific_reopen['status']=='NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED':
                actions=['the reopened child scientific contract now exists at scientific stage problem. Run an independent reopen Problem Gate next; it has zero paper-design, method, experiment, P0, or GPU authority until that gate is separately adjudicated']
            elif scientific_reopen['status']=='REOPEN_METHOD_DESIGN_REQUIRED':
                actions=['the reopen Problem Gate passed. Freeze a bounded method design with matched same-information baselines, identifiability boundary, cheapest local falsifier, resource budget, and stop rules; no execution authority exists']
            elif scientific_reopen['status']=='REOPEN_METHOD_DESIGN_FROZEN_AWAITING_INDEPENDENT_REVIEW':
                actions=['the reopened method design is frozen. Run independent method review against generic same-information reductions before any experiment blueprint is designed']
            elif scientific_reopen['status']=='REOPEN_EXPERIMENT_BLUEPRINT_REQUIRED':
                actions=['independent method review passed. Freeze a bounded local-F0 experiment blueprint with units, qualification, arms, truth, metrics, same-information baselines, statistics, budget, GO/STOP, recovery, and escalation rules; execution remains unauthorized']
            elif scientific_reopen['status']=='REOPEN_EXPERIMENT_BLUEPRINT_FROZEN_AWAITING_INDEPENDENT_REVIEW':
                actions=['the local-F0 blueprint is frozen. Run independent blueprint review before any local-validation authorization or Pre-Experiment Compiler handoff']
            elif scientific_reopen['status']=='LOCAL_VALIDATION_AUTHORIZATION_REQUIRED':
                actions=['independent blueprint review passed. Obtain explicit external human/PI authorization for the bounded local F0; this authorization may not exceed the frozen blueprint budget and does not authorize execution']
            elif scientific_reopen['status']=='PRE_EXPERIMENT_COMPILER_REQUIRED':
                actions=['bounded local validation is human-authorized. Supply only real runtime/preflight evidence to the existing Pre-Experiment Compiler; missing competence, throughput, recovery, or protocol evidence must block rather than be default-filled']
            elif scientific_reopen['status']=='PRE_EXPERIMENT_COMPILER_BLOCKED':
                actions=['the native Pre-Experiment Compiler is blocked. Repair only its prerequisites/gates using real runtime evidence; no experiment lease or execution is allowed']
            elif scientific_reopen['status']=='EXPERIMENT_LEASE_REQUEST_REQUIRED':
                actions=['the native Pre-Experiment Compiler passed all prerequisites and 8 gates. Prepare a content-addressed experiment lease request bound to the exact research-execution plan hash; do not acquire the lease automatically']
            elif scientific_reopen['status']=='EXPERIMENT_LEASE_REQUEST_READY_EXPLICIT_ACQUIRE_REQUIRED':
                actions=['the single-writer experiment lease request is ready. A separate explicit executor action must assign run_id/actor, recheck governance stage, and acquire the exact-plan lease before execution']
            elif scientific_reopen['status']=='EXPERIMENT_LEASE_ACTIVE_RUN_NOT_STARTED':
                actions=['the single-writer experiment lease is active, but the run has not started and no GPU is allocated. Perform an explicit resource/GPU lease and run-start step next; do not treat experiment authority as evidence or P0 authority']
            elif scientific_reopen['status']=='EXPERIMENT_LEASE_STALE_OR_RELEASED':
                actions=['the recorded experiment lease is stale or released. Reacquire a current exact-plan single-writer lease only after rechecking the same frozen runtime/governance lineage; do not start from the stale receipt']
            elif scientific_reopen['status']=='EXPERIMENT_LEASE_LEDGER_INVALID':
                actions=['the experiment-lease receipt ledger is invalid. Stop run preparation and repair the lease/audit lineage; do not infer authority from the raw experiment-authority file alone']
            elif scientific_reopen['status']=='EXPERIMENT_LEASE_REQUEST_LEDGER_INVALID':
                actions=['the experiment lease-request ledger is invalid. Stop launch preparation and repair the request lineage; no execution is allowed']
            elif scientific_reopen['status']=='PRE_EXPERIMENT_ADAPTER_LEDGER_INVALID':
                actions=['the Pre-Experiment adapter ledger is invalid. Stop launch preparation and repair the content-addressed compiler lineage']
            elif scientific_reopen['status']=='LOCAL_VALIDATION_AUTHORITY_LEDGER_INVALID':
                actions=['local-validation authority ledger is invalid. Stop execution preparation and repair the content-addressed human authority lineage']
            elif scientific_reopen['status']=='REOPEN_BLUEPRINT_REVIEW_BLOCKED':
                actions=['independent blueprint review blocked the plan. Repair only the blueprint or stop; do not execute local validation']
            elif scientific_reopen['status']=='REOPEN_BLUEPRINT_LEDGER_INVALID':
                actions=['the reopen experiment-blueprint ledger is invalid. Stop local-validation authorization and repair the append-only blueprint lineage']
            elif scientific_reopen['status']=='REOPEN_METHOD_REVIEW_BLOCKED':
                actions=['independent method review blocked this realization. Revise or stop the method design without launching experiments']
            elif scientific_reopen['status']=='REOPEN_METHOD_LEDGER_INVALID':
                actions=['the reopen method-design ledger is invalid. Stop blueprint design and repair the append-only method lineage']
            elif scientific_reopen['status']=='REOPEN_PROBLEM_GATE_BLOCKED':
                actions=['the reopen Problem Gate is blocked; repair only the failed problem checks or stop this child scientific object. Do not proceed to method or experiment design']
            elif scientific_reopen['status']=='REOPEN_PROBLEM_GATE_LEDGER_INVALID':
                actions=['the reopen Problem Gate ledger is invalid; stop downstream scientific work until the append-only audit lineage is repaired']
            else:
                actions=['scientific-reopen ledger is invalid; stop scientific changes until the proposal/authorization lineage is repaired']
        elif attempt_workflow['status']=='ATTEMPT_POST_DECISION_LEARN_COMPLETE':
            actions=['the child attempt outcome is closed; any further submission must create a new child attempt bound to this child submission/decision/learning lineage']
        elif attempt_workflow['status']=='ATTEMPT_FINAL_DECISION_LEARNING_PENDING':
            actions=['record scoped child post-decision lessons; acceptance/rejection does not change scientific truth or authorize automatic reopen']
        elif attempt_workflow['status']=='ATTEMPT_TERMINAL_DECISION_SKIP_PENDING':
            actions=['record the explicit child venue-skip receipt before learning; never fabricate reviews or rebuttal for a no-window terminal decision']
        elif attempt_workflow['status']=='ATTEMPT_REBUTTAL_PREPARED_DECISION_PENDING':
            actions=['child rebuttal is prepared; await the real venue final decision without granting experiment or claim-expansion authority']
        elif attempt_workflow['status']=='ATTEMPT_VENUE_REVIEWS_RECORDED':
            actions=['classify child venue objections and prepare a scope-preserving rebuttal; missing decisive evidence cannot be papered over']
        elif attempt_workflow['status']=='ATTEMPT_VENUE_SUBMISSION_CONFIRMED':
            actions=['await real child venue reviews or an explicit terminal no-rebuttal decision; keep parent and child submission lineages distinct']
        elif attempt_workflow['status']=='ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING':
            actions=['child human signoff is complete, but a sibling attempt has an active real venue submission; do not dual-submit and re-run the conflict guard only after that sibling reaches a terminal venue outcome']
        elif attempt_workflow['status']=='ATTEMPT_HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING':
            actions=['child human signoff is complete; actual child venue upload remains a separate explicit human action and must pass the paper-level sibling-submission conflict guard']
        elif attempt_workflow['status']=='ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED':
            actions=['the child attempt has its own preparation/freeze/handoff lineage; await explicit human confirmation and never reuse the parent submission signoff']
        elif attempt_workflow['status'] in {'ATTEMPT_HANDOFF_STALE','ATTEMPT_FREEZE_STALE','ATTEMPT_HUMAN_SIGNOFF_STALE','ATTEMPT_WORKFLOW_INVALID'}:
            actions=['the child attempt workflow is stale or invalid; repair/refreeze only within this attempt namespace and never mutate the parent submission']
        elif attempt['machine_preparation_eligible']:
            actions=['the child attempt is paper-side only and may enter its fresh attempt-scoped Preparation/Freeze/Handoff pipeline while parent submitted bytes remain immutable']
        else:
            actions=['post-decision learning is complete; preserve parent submission immutability and inspect the latest child-attempt plan']
    elif state == 'REBUTTAL':
        if rebuttal['status']=='REBUTTAL_SKIPPED_BY_VENUE':
            actions=['venue provided no rebuttal window; do not fabricate reviews or a rebuttal, and proceed only with scoped post-decision learning'] if learning['status']=='POST_DECISION_LEARNING_PENDING' else ['venue-skipped rebuttal lineage is closed; advance to LEARN only after the scoped learning receipt passes']
        elif rebuttal['status']!='REBUTTAL_ACTIVE': actions=['REBUTTAL state has an invalid or stale preparation/venue-skip receipt; stop downstream workflow until repaired']
        elif learning['status']=='AWAITING_FINAL_VENUE_DECISION': actions=['rebuttal is active; await the real final venue decision']
        elif learning['status']=='POST_DECISION_LEARNING_PENDING': actions=['record scoped post-decision lessons; acceptance/rejection does not change scientific claim truth']
        elif learning['status']=='LEARNING_PREPARED_TRANSITION_PENDING': actions=['post-decision learning passed; advance REBUTTAL → LEARN without granting scientific or experiment authority']
    elif state == 'SUBMITTED':
        if not actual_valid: actions=['SUBMITTED state has an invalid or missing venue submission receipt; treat the ledger as invalid until repaired']
        elif rebuttal['status']=='REBUTTAL_SKIPPED_TRANSITION_PENDING': actions=['venue issued a terminal decision with no rebuttal window; advance through the logical REBUTTAL node using the bound venue-skip receipt, without fabricating reviews']
        elif review_intake['status']=='AWAITING_VENUE_REVIEWS': actions=['await real venue reviews or an explicit terminal venue decision; do not synthesize mock reviews into the rebuttal ledger']
        elif review_intake['status']=='REVIEW_INTAKE_STALE': actions=['repair review intake lineage against the current venue submission receipt']
        elif rebuttal['status']=='REBUTTAL_PREPARATION_PENDING': actions=['classify venue objections and prepare a scope-preserving rebuttal; reviewer requests do not authorize experiments']
        elif rebuttal['status']=='REBUTTAL_PREPARED_TRANSITION_PENDING': actions=['rebuttal preparation passed; advance the paper to REBUTTAL without changing scientific authority']
    elif base_ready and freeze['status'] == 'MACHINE_FREEZE_PENDING':
        actions = ['create a pre-submission freeze checkpoint before machine handoff']
    elif base_ready and freeze['status'] == 'MACHINE_FREEZE_STALE':
        rerun = list(impact.get('minimum_rerun_paper_preparation_gates') or []) + list(impact.get('minimum_rerun_paper_acceptance_checks') or [])
        actions = ['revision impact requires rerun: ' + ', '.join(rerun)] if rerun else ['re-freeze the exact PDF/source/supplement bytes before machine handoff']
    elif base_ready and machine_handoff['status'] == 'MACHINE_HANDOFF_PENDING':
        actions = ['build the machine submission handoff packet from the current freeze before author confirmation']
    elif base_ready and machine_handoff['status'] == 'MACHINE_HANDOFF_STALE':
        actions = ['rebuild the machine submission handoff packet from the current freeze before author confirmation']
    elif human_signoff['status'] == 'PENDING_HUMAN_CONFIRMATION':
        actions = ['collect explicit human confirmations bound to the current handoff SHA; actual submission remains a separate action']
    elif human_signoff['status'] == 'HUMAN_SIGNOFF_STALE':
        actions = ['repeat human signoff against the current freeze and handoff before any upload']
    elif human_signoff['status'] == 'HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING':
        actions = ['human signoff is complete; actual venue upload still requires a separate explicit human submission action and receipt']
    elif not groups and not handoff:
        actions = ['complete Paper Preparation migration before human handoff']

    return {
        'paper_id': paper_id,
        'title': str(contract.get('title') or paper_id),
        'paper_state': str(row.get('current_state') or ''),
        'contract_integrity_pass': contract_ok,
        'ledger_replay_pass': not ledger_errors,
        'ledger_errors': ledger_errors,
        'paper_preparation_status': preparation,
        'paper_preparation_passed_gates': int((prep_receipt.get('summary') or {}).get('passed_gates') or 0) if prep_ok else 0,
        'paper_preparation_required_gates': int((prep_receipt.get('summary') or {}).get('required_gates') or 8),
        'paper_preparation_receipt_sha256': str(prep_receipt.get('receipt_sha256') or '') if prep_ok else '',
        'freeze_status': freeze['status'],
        'freeze_integrity_pass': freeze['integrity_pass'],
        'freeze_sha256': freeze['freeze_sha256'],
        'freeze_errors': freeze['errors'],
        'revision_impact_status': str(impact.get('status') or ''),
        'revision_impact_classes': list(impact.get('impact_classes') or []),
        'revision_impact_preparation_reruns': list(impact.get('minimum_rerun_paper_preparation_gates') or []),
        'revision_impact_acceptance_reruns': list(impact.get('minimum_rerun_paper_acceptance_checks') or []),
        'revision_impact_requires_full_reaudit': impact.get('requires_full_preparation_reaudit') is True,
        'machine_handoff_status': machine_handoff['status'],
        'machine_handoff_integrity_pass': machine_handoff['integrity_pass'],
        'machine_handoff_sha256': machine_handoff['handoff_sha256'],
        'machine_handoff_errors': machine_handoff['errors'],
        'human_signoff_status': human_signoff['status'],
        'human_signoff_integrity_pass': human_signoff['integrity_pass'],
        'human_signoff_sha256': human_signoff['signoff_sha256'],
        'human_signoff_errors': human_signoff['errors'],
        'actual_submission_status': actual_submission_status,
        'actual_submission_receipt_valid': actual_valid,
        'actual_submission_receipt_sha256': str(actual_receipt.get('submission_receipt_sha256') or ''),
        'venue_submission_id': str(actual_receipt.get('venue_submission_id') or ''),
        'venue_forum_ref': str(actual_receipt.get('venue_forum_ref') or ''),
        'submitted_at': str(actual_receipt.get('submitted_at') or ''),
        'review_intake_status': review_intake['status'],
        'review_set_sha256': review_intake['review_set_sha256'],
        'venue_review_count': review_intake['review_count'],
        'review_intake_errors': review_intake['errors'],
        'rebuttal_status': rebuttal['status'],
        'rebuttal_receipt_sha256': rebuttal['rebuttal_receipt_sha256'],
        'rebuttal_skip_sha256': rebuttal['rebuttal_skip_sha256'],
        'rebuttal_errors': rebuttal['errors'],
        'rebuttal_objections': rebuttal['objections'],
        'rebuttal_decision_critical': rebuttal['decision_critical'],
        'rebuttal_missing_decisive_evidence': rebuttal['missing_decisive_evidence'],
        'rebuttal_new_claim_requests': rebuttal['new_claim_requests'],
        'learning_status': learning['status'],
        'venue_final_decision': learning['decision'],
        'venue_decision_sha256': learning['venue_decision_sha256'],
        'post_decision_learning_sha256': learning['learning_receipt_sha256'],
        'post_decision_lessons': learning['lessons'],
        'post_decision_scientific_diagnostic_lessons': learning['scientific_diagnostic_only'],
        'submission_attempt_status': attempt['status'],
        'submission_attempt_count': attempt['attempts'],
        'latest_submission_attempt_id': attempt['latest_attempt_id'],
        'latest_submission_attempt_sha256': attempt['latest_attempt_sha256'],
        'latest_submission_attempt_type': attempt['latest_attempt_type'],
        'latest_submission_attempt_target_venue': attempt['target_venue'],
        'submission_attempt_machine_preparation_eligible': attempt['machine_preparation_eligible'],
        'submission_attempt_requires_scientific_reopen': attempt['requires_explicit_scientific_reopen'],
        'parent_submission_bytes_immutable': attempt['parent_submission_bytes_immutable'],
        'submission_attempt_errors': attempt['validation_errors'],
        'submission_attempt_workflow_status': attempt_workflow['status'],
        'submission_attempt_preparation_sha256': attempt_workflow['preparation_sha256'],
        'submission_attempt_freeze_sha256': attempt_workflow['freeze_sha256'],
        'submission_attempt_handoff_sha256': attempt_workflow['handoff_sha256'],
        'submission_attempt_signoff_sha256': attempt_workflow['signoff_sha256'],
        'submission_attempt_conflict_guard_sha256': attempt_workflow['submission_conflict_guard_sha256'],
        'submission_attempt_conflict_guard_status': attempt_workflow['submission_conflict_guard_status'],
        'submission_attempt_conflict_count': attempt_workflow['submission_conflict_count'],
        'submission_attempt_actual_receipt_sha256': attempt_workflow['submission_receipt_sha256'],
        'submission_attempt_venue_submission_id': attempt_workflow['venue_submission_id'],
        'submission_attempt_submitted_at': attempt_workflow['submitted_at'],
        'submission_attempt_actual_submission_status': attempt_workflow['actual_submission_status'],
        'submission_attempt_review_set_sha256': attempt_workflow['review_set_sha256'],
        'submission_attempt_review_count': attempt_workflow['review_count'],
        'submission_attempt_rebuttal_sha256': attempt_workflow['rebuttal_receipt_sha256'],
        'submission_attempt_missing_decisive_evidence': attempt_workflow['rebuttal_missing_decisive_evidence'],
        'submission_attempt_new_claim_requests': attempt_workflow['rebuttal_new_claim_requests'],
        'submission_attempt_venue_decision_sha256': attempt_workflow['venue_decision_sha256'],
        'submission_attempt_venue_decision': attempt_workflow['venue_decision'],
        'submission_attempt_decision_phase': attempt_workflow['decision_phase'],
        'submission_attempt_rebuttal_skip_sha256': attempt_workflow['rebuttal_skip_sha256'],
        'submission_attempt_learning_sha256': attempt_workflow['learning_receipt_sha256'],
        'submission_attempt_learning_lessons': attempt_workflow['learning_lessons'],
        'submission_attempt_learning_scientific_diagnostic_only': attempt_workflow['learning_scientific_diagnostic_only'],
        'submission_attempt_frozen_artifacts': attempt_workflow['frozen_artifacts'],
        'submission_attempt_freeze_drift_errors': attempt_workflow['freeze_drift_errors'],
        'submission_attempt_workflow_errors': attempt_workflow['validation_errors'],
        'submission_attempt_human_confirmation_status': attempt_workflow['human_confirmation_status'],
        'submission_attempt_history': attempt_history,
        'scientific_reopen_status': scientific_reopen['status'],
        'scientific_reopen_proposal_sha256': scientific_reopen['proposal_sha256'],
        'scientific_reopen_authorization_sha256': scientific_reopen['authorization_sha256'],
        'scientific_reopen_authorization_scope': scientific_reopen['authorization_scope'],
        'scientific_reopen_external_authority_confirmed': scientific_reopen['external_scientific_authority_confirmed'],
        'scientific_reopen_research_os_handoff_sha256': scientific_reopen['research_os_handoff_sha256'],
        'scientific_reopen_new_contract_seed_id': scientific_reopen['new_contract_seed_id'],
        'scientific_reopen_destination_gate': scientific_reopen['destination_gate'],
        'scientific_reopen_new_contract_creation_eligible': scientific_reopen['new_contract_creation_eligible'],
        'scientific_reopen_new_contract_required': scientific_reopen['new_scientific_contract_required'],
        'reopened_scientific_contract': scientific_reopen['new_contract'],
        'scientific_reopen_errors': scientific_reopen['validation_errors'],
        'blocker_groups': groups,
        'blocker_count': len(blockers),
        'next_actions': actions,
        'human_handoff_ready': handoff,
        'submission_freeze_eligible': base_ready,
        'authority': {'scientific': False, 'experiment': False, 'gpu': False, 'submission': False},
    }


def source_watermark(root: Path) -> str:
    timestamps: list[str] = []
    for directory in (root / 'paper-acceptance', root / 'paper-submission-freezes', root / 'paper-submission-handoffs', root / 'paper-human-signoffs', root / 'paper-review-intake', root / 'paper-submission-attempts', root / 'paper-submission-attempt-workflows', root / 'paper-scientific-reopen', root / 'scientific-contracts', root / 'scientific-contract-problem-gates', root / 'scientific-contract-method-design', root / 'scientific-contract-experiment-blueprints', root / 'scientific-contract-local-validation-authority', root / 'scientific-contract-pre-experiment', root / 'scientific-contract-experiment-lease-requests', root / 'scientific-contract-experiment-leases', root / 'experiment-authority'):
        if not directory.exists():
            continue
        for path in sorted(directory.glob('*.json')):
            if path.name in {'current-freeze-index.json', 'venue-policy-iclr2027-20260822.json'}:
                continue
            try:
                payload = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                continue
            updated = str(payload.get('updated_at') or payload.get('released_at') or payload.get('acquired_at') or payload.get('created_at') or '')
            if updated:
                timestamps.append(updated)
    return max(timestamps) if timestamps else '1970-01-01T00:00:00+00:00'


def build(root: Path = DEFAULT_ROOT) -> dict[str, Any]:
    papers = [project(path, root) for path in sorted((root / 'paper-acceptance').glob('*.json'))]
    return {
        'schema_version': '1.1',
        'generated_at': source_watermark(root),
        'papers': papers,
        'summary': {
            'papers': len(papers),
            'paper_acceptance_submission_ready': sum(p['paper_state'] == 'SUBMISSION_READY' for p in papers),
            'preparation_pass': sum(p['paper_preparation_status'] == 'PASS' for p in papers),
            'preparation_blocked': sum(p['paper_preparation_status'] == 'BLOCKED' for p in papers),
            'legacy_pending': sum(p['paper_preparation_status'] == 'LEGACY_PENDING' for p in papers),
            'machine_frozen_current': sum(p['freeze_status'] == 'MACHINE_FROZEN_CURRENT' for p in papers),
            'machine_freeze_stale': sum(p['freeze_status'] == 'MACHINE_FREEZE_STALE' for p in papers),
            'machine_handoff_current': sum(p['machine_handoff_status'] == 'MACHINE_HANDOFF_CURRENT' for p in papers),
            'machine_handoff_stale': sum(p['machine_handoff_status'] == 'MACHINE_HANDOFF_STALE' for p in papers),
            'human_handoff_ready': sum(p['human_handoff_ready'] for p in papers),
            'human_signoff_pending': sum(p['human_signoff_status'] == 'PENDING_HUMAN_CONFIRMATION' for p in papers),
            'human_signoff_complete': sum(p['human_signoff_status'] == 'HUMAN_SIGNOFF_COMPLETE_ACTUAL_SUBMISSION_PENDING' for p in papers),
            'human_signoff_stale': sum(p['human_signoff_status'] == 'HUMAN_SIGNOFF_STALE' for p in papers),
            'submitted': sum(p['paper_state'] == 'SUBMITTED' for p in papers),
            'submitted_receipt_bound': sum(p['actual_submission_status'] == 'VENUE_SUBMISSION_CONFIRMED' for p in papers),
            'submitted_receipt_invalid': sum(p['actual_submission_status'] == 'SUBMITTED_RECEIPT_INVALID' for p in papers),
            'awaiting_venue_reviews': sum(p['review_intake_status'] == 'AWAITING_VENUE_REVIEWS' for p in papers),
            'review_sets_current': sum(p['review_intake_status'] == 'REVIEW_SET_CURRENT' for p in papers),
            'rebuttal_preparation_pending': sum(p['rebuttal_status'] == 'REBUTTAL_PREPARATION_PENDING' for p in papers),
            'rebuttal_active': sum(p['rebuttal_status'] == 'REBUTTAL_ACTIVE' for p in papers),
            'rebuttal_skipped_by_venue': sum(p['rebuttal_status'] in {'REBUTTAL_SKIPPED_TRANSITION_PENDING','REBUTTAL_SKIPPED_BY_VENUE'} for p in papers),
            'final_decisions_recorded': sum(bool(p['venue_decision_sha256']) for p in papers),
            'post_decision_learning_pending': sum(p['learning_status'] == 'POST_DECISION_LEARNING_PENDING' for p in papers),
            'learning_prepared': sum(p['learning_status'] == 'LEARNING_PREPARED_TRANSITION_PENDING' for p in papers),
            'learn_complete': sum(p['learning_status'] == 'LEARN_COMPLETE' for p in papers),
            'submission_attempt_plans': sum(int((p['submission_attempt_history'].get('summary') or {}).get('attempts') or 0) for p in papers),
            'attempt_machine_preparation_eligible': sum(int((p['submission_attempt_history'].get('summary') or {}).get('machine_preparation_eligible') or 0) for p in papers),
            'attempts_requiring_scientific_reopen': sum(int((p['submission_attempt_history'].get('summary') or {}).get('requires_explicit_scientific_reopen') or 0) for p in papers),
            'resubmission_plans': sum(int((p['submission_attempt_history'].get('summary') or {}).get('resubmissions') or 0) for p in papers),
            'camera_ready_plans': sum(int((p['submission_attempt_history'].get('summary') or {}).get('camera_ready') or 0) for p in papers),
            'attempt_ledger_invalid': sum(bool(p['submission_attempt_history'].get('validation_errors')) for p in papers),
            'attempt_preparation_pass': sum(p['submission_attempt_workflow_status'] == 'ATTEMPT_PREPARATION_PASS_FREEZE_PENDING' for p in papers),
            'attempt_machine_frozen': sum(p['submission_attempt_workflow_status'] == 'ATTEMPT_MACHINE_FROZEN_HANDOFF_PENDING' for p in papers),
            'attempt_machine_handoff_ready': sum(p['submission_attempt_workflow_status'] == 'ATTEMPT_MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED' for p in papers),
            'attempt_submission_blocked_active_sibling': sum(p['submission_attempt_workflow_status'] == 'ATTEMPT_SUBMISSION_BLOCKED_ACTIVE_SIBLING' for p in papers),
            'attempt_workflow_stale_or_invalid': sum(int((p['submission_attempt_history'].get('summary') or {}).get('invalid_attempts') or 0) for p in papers),
            'attempt_human_signoff_complete': sum(int((p['submission_attempt_history'].get('summary') or {}).get('human_signoffs') or 0) for p in papers),
            'attempt_venue_submitted': sum(int((p['submission_attempt_history'].get('summary') or {}).get('venue_submissions') or 0) for p in papers),
            'attempt_reviews_recorded': sum(int((p['submission_attempt_history'].get('summary') or {}).get('review_sets') or 0) for p in papers),
            'attempt_rebuttals_prepared': sum(int((p['submission_attempt_history'].get('summary') or {}).get('rebuttals_prepared') or 0) for p in papers),
            'attempt_final_decisions_recorded': sum(int((p['submission_attempt_history'].get('summary') or {}).get('final_decisions') or 0) for p in papers),
            'attempt_post_decision_learning_complete': sum(int((p['submission_attempt_history'].get('summary') or {}).get('post_decision_learn_complete') or 0) for p in papers),
            'attempt_rebuttal_skipped_by_venue': sum(int((p['submission_attempt_history'].get('summary') or {}).get('rebuttals_skipped_by_venue') or 0) for p in papers),
            'scientific_reopen_proposed': sum(p['scientific_reopen_status'] == 'SCIENTIFIC_REOPEN_PROPOSED_EXTERNAL_AUTHORITY_REQUIRED' for p in papers),
            'scientific_reopen_authorized_new_contract_required': sum(p['scientific_reopen_status'] == 'EXTERNAL_SCIENTIFIC_REOPEN_CONFIRMED_NEW_CONTRACT_REQUIRED' for p in papers),
            'scientific_reopen_research_os_handoff_ready': sum(p['scientific_reopen_status'] == 'RESEARCH_OS_NEW_CONTRACT_HANDOFF_READY' for p in papers),
            'reopened_scientific_contract_problem_gate_required': sum(p['scientific_reopen_status'] == 'NEW_SCIENTIFIC_CONTRACT_CREATED_PROBLEM_GATE_REQUIRED' for p in papers),
            'reopen_problem_gate_pass': sum(p['scientific_reopen_status'] == 'REOPEN_PROBLEM_GATE_PASS_METHOD_DESIGN_REVIEW_ELIGIBLE' for p in papers),
            'reopen_problem_gate_blocked': sum(p['scientific_reopen_status'] == 'REOPEN_PROBLEM_GATE_BLOCKED' for p in papers),
            'reopen_problem_gate_invalid': sum(p['scientific_reopen_status'] == 'REOPEN_PROBLEM_GATE_LEDGER_INVALID' for p in papers),
            'reopen_method_design_required': sum(p['scientific_reopen_status'] == 'REOPEN_METHOD_DESIGN_REQUIRED' for p in papers),
            'reopen_method_design_awaiting_review': sum(p['scientific_reopen_status'] == 'REOPEN_METHOD_DESIGN_FROZEN_AWAITING_INDEPENDENT_REVIEW' for p in papers),
            'reopen_method_review_pass': sum(p['scientific_reopen_status'] == 'REOPEN_METHOD_REVIEW_PASS_BLUEPRINT_DESIGN_ELIGIBLE' for p in papers),
            'reopen_method_review_blocked': sum(p['scientific_reopen_status'] == 'REOPEN_METHOD_REVIEW_BLOCKED' for p in papers),
            'reopen_method_invalid': sum(p['scientific_reopen_status'] == 'REOPEN_METHOD_LEDGER_INVALID' for p in papers),
            'reopen_blueprint_required': sum(p['scientific_reopen_status'] == 'REOPEN_EXPERIMENT_BLUEPRINT_REQUIRED' for p in papers),
            'reopen_blueprint_awaiting_review': sum(p['scientific_reopen_status'] == 'REOPEN_EXPERIMENT_BLUEPRINT_FROZEN_AWAITING_INDEPENDENT_REVIEW' for p in papers),
            'reopen_blueprint_review_pass': sum(p['scientific_reopen_status'] == 'REOPEN_BLUEPRINT_REVIEW_PASS_LOCAL_VALIDATION_AUTHORIZATION_ELIGIBLE' for p in papers),
            'reopen_blueprint_review_blocked': sum(p['scientific_reopen_status'] == 'REOPEN_BLUEPRINT_REVIEW_BLOCKED' for p in papers),
            'reopen_blueprint_invalid': sum(p['scientific_reopen_status'] == 'REOPEN_BLUEPRINT_LEDGER_INVALID' for p in papers),
            'reopen_local_validation_authorized': sum(p['scientific_reopen_status'] == 'LOCAL_VALIDATION_AUTHORIZED_PRE_EXPERIMENT_COMPILER_REQUIRED' for p in papers),
            'reopen_local_validation_authority_invalid': sum(p['scientific_reopen_status'] == 'LOCAL_VALIDATION_AUTHORITY_LEDGER_INVALID' for p in papers),
            'reopen_pre_experiment_required': sum(p['scientific_reopen_status'] == 'PRE_EXPERIMENT_COMPILER_REQUIRED' for p in papers),
            'reopen_pre_experiment_blocked': sum(p['scientific_reopen_status'] == 'PRE_EXPERIMENT_COMPILER_BLOCKED' for p in papers),
            'reopen_pre_experiment_pass_lease_required': sum(p['scientific_reopen_status'] == 'PRE_EXPERIMENT_COMPILER_PASS_EXPERIMENT_LEASE_REQUIRED' for p in papers),
            'reopen_pre_experiment_invalid': sum(p['scientific_reopen_status'] == 'PRE_EXPERIMENT_ADAPTER_LEDGER_INVALID' for p in papers),
            'reopen_experiment_lease_request_required': sum(p['scientific_reopen_status'] == 'EXPERIMENT_LEASE_REQUEST_REQUIRED' for p in papers),
            'reopen_experiment_lease_request_ready': sum(p['scientific_reopen_status'] == 'EXPERIMENT_LEASE_REQUEST_READY_EXPLICIT_ACQUIRE_REQUIRED' for p in papers),
            'reopen_experiment_lease_request_invalid': sum(p['scientific_reopen_status'] == 'EXPERIMENT_LEASE_REQUEST_LEDGER_INVALID' for p in papers),
            'reopen_experiment_lease_active_run_not_started': sum(p['scientific_reopen_status'] == 'EXPERIMENT_LEASE_ACTIVE_RUN_NOT_STARTED' for p in papers),
            'reopen_experiment_lease_stale_or_released': sum(p['scientific_reopen_status'] == 'EXPERIMENT_LEASE_STALE_OR_RELEASED' for p in papers),
            'reopen_experiment_lease_invalid': sum(p['scientific_reopen_status'] == 'EXPERIMENT_LEASE_LEDGER_INVALID' for p in papers),
            'scientific_reopen_invalid': sum(p['scientific_reopen_status'] == 'SCIENTIFIC_REOPEN_LEDGER_INVALID' for p in papers),
            'submission_freeze_eligible': sum(p['submission_freeze_eligible'] for p in papers),
            'ledger_replay_failures': sum(not p['ledger_replay_pass'] for p in papers),
            'contract_integrity_failures': sum(not p['contract_integrity_pass'] for p in papers),
        },
        'authority': {'scientific': False, 'experiment': False, 'gpu': False, 'submission': False},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--json-output', type=Path, default=Path('generated/paper-portfolio-audit.json'))
    parser.add_argument('--js-output', type=Path, default=Path('generated/paper-portfolio-audit.js'))
    args = parser.parse_args()
    payload = build(args.root)
    payload['audit_sha256'] = digest(payload)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.js_output.write_text('window.PAPER_PORTFOLIO_AUDIT = ' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'summary': payload['summary'], 'audit_sha256': payload['audit_sha256']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
