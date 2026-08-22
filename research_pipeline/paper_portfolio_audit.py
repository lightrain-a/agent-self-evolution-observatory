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
from .post_decision_learning import validate_learning_receipt, validate_venue_decision_receipt

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
    valid=bool(receipt) and str(receipt.get('contract_sha256') or '')==str(row.get('contract_sha256') or '') and validate_rebuttal_receipt(receipt)
    errors=[]
    if receipt and not valid: errors.append('rebuttal-receipt-invalid')
    if valid and review_set_sha256 and receipt.get('review_set_sha256')!=review_set_sha256: errors.append('rebuttal-review-set-stale')
    summary=receipt.get('summary') if isinstance(receipt.get('summary'),dict) else {}
    if state=='REBUTTAL': status='REBUTTAL_ACTIVE' if valid and not errors and receipt.get('pass') is True else 'REBUTTAL_RECEIPT_INVALID'
    elif state=='SUBMITTED': status='REBUTTAL_PREPARED_TRANSITION_PENDING' if valid and not errors and receipt.get('pass') is True else 'REBUTTAL_PREPARATION_PENDING'
    else: status='NOT_ELIGIBLE'
    return {
        'status':status,'valid':valid and not errors,'errors':errors,
        'rebuttal_receipt_sha256':str(receipt.get('rebuttal_receipt_sha256') or ''),
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
    learning=learning_state(row)
    actions = next_actions(groups)
    if state == 'LEARN':
        actions = ['post-decision learning is complete; reuse process lessons only within their declared scope, while scientific lessons remain diagnostic until independent evidence exists'] if learning['status']=='LEARN_COMPLETE' else ['LEARN state has invalid decision/learning lineage; stop reuse until repaired']
    elif state == 'REBUTTAL':
        if rebuttal['status']!='REBUTTAL_ACTIVE': actions=['REBUTTAL state has an invalid or stale preparation receipt; stop response workflow until repaired']
        elif learning['status']=='AWAITING_FINAL_VENUE_DECISION': actions=['rebuttal is active; await the real final venue decision']
        elif learning['status']=='POST_DECISION_LEARNING_PENDING': actions=['record scoped post-decision lessons; acceptance/rejection does not change scientific claim truth']
        elif learning['status']=='LEARNING_PREPARED_TRANSITION_PENDING': actions=['post-decision learning passed; advance REBUTTAL → LEARN without granting scientific or experiment authority']
    elif state == 'SUBMITTED':
        if not actual_valid: actions=['SUBMITTED state has an invalid or missing venue submission receipt; treat the ledger as invalid until repaired']
        elif review_intake['status']=='AWAITING_VENUE_REVIEWS': actions=['await real venue reviews; do not synthesize mock reviews into the rebuttal ledger']
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
        'blocker_groups': groups,
        'blocker_count': len(blockers),
        'next_actions': actions,
        'human_handoff_ready': handoff,
        'submission_freeze_eligible': base_ready,
        'authority': {'scientific': False, 'experiment': False, 'gpu': False, 'submission': False},
    }


def source_watermark(root: Path) -> str:
    timestamps: list[str] = []
    for directory in (root / 'paper-acceptance', root / 'paper-submission-freezes', root / 'paper-submission-handoffs', root / 'paper-human-signoffs', root / 'paper-review-intake'):
        if not directory.exists():
            continue
        for path in sorted(directory.glob('*.json')):
            if path.name in {'current-freeze-index.json', 'venue-policy-iclr2027-20260822.json'}:
                continue
            try:
                payload = json.loads(path.read_text(encoding='utf-8'))
            except (OSError, json.JSONDecodeError):
                continue
            updated = str(payload.get('updated_at') or '')
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
            'final_decisions_recorded': sum(bool(p['venue_decision_sha256']) for p in papers),
            'post_decision_learning_pending': sum(p['learning_status'] == 'POST_DECISION_LEARNING_PENDING' for p in papers),
            'learning_prepared': sum(p['learning_status'] == 'LEARNING_PREPARED_TRANSITION_PENDING' for p in papers),
            'learn_complete': sum(p['learning_status'] == 'LEARN_COMPLETE' for p in papers),
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
