from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .paper_acceptance_ledger import validate_paper_ledger
from .paper_preparation_protocol import validate_paper_preparation_receipt
from .presubmission_freeze import validate_freeze, verify_current_frozen_artifacts

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
    if 'visual' in text:
        return 'VISUAL_CONTRACT'
    if 'reproducibility' in text:
        return 'REPRODUCIBILITY'
    if 'agent-native' in text or 'claim-raw' in text:
        return 'CLAIM_RAW_GROUNDING'
    if 'reader-' in text:
        return 'READER_SIMULATION'
    if 'submission-package' in text:
        return 'VENUE_HANDOFF'
    return 'OTHER'


def next_actions(groups: list[str]) -> list[str]:
    table = {
        'DECISIVE_EVIDENCE': 'close decision-critical claim-evidence gaps; support unavailability is support debt, not scientific counterevidence',
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

    base_ready = row.get('current_state') == 'SUBMISSION_READY' and preparation == 'PASS' and contract_ok and not ledger_errors
    freeze = freeze_state(root, paper_id, str(prep_receipt.get('receipt_sha256') or '')) if base_ready else {
        'status': 'PREPARATION_BLOCKED' if preparation == 'BLOCKED' else 'NOT_ELIGIBLE',
        'integrity_pass': False,
        'errors': [],
        'freeze_sha256': '',
    }
    handoff = base_ready and freeze['status'] == 'MACHINE_FROZEN_CURRENT'
    actions = next_actions(groups)
    if base_ready and freeze['status'] == 'MACHINE_FREEZE_PENDING':
        actions = ['create a pre-submission freeze checkpoint before human handoff']
    elif base_ready and freeze['status'] == 'MACHINE_FREEZE_STALE':
        actions = ['re-freeze the exact PDF/source/supplement bytes before human handoff']
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
        'blocker_groups': groups,
        'blocker_count': len(blockers),
        'next_actions': actions,
        'human_handoff_ready': handoff,
        'submission_freeze_eligible': base_ready,
        'authority': {'scientific': False, 'experiment': False, 'gpu': False, 'submission': False},
    }


def build(root: Path = DEFAULT_ROOT) -> dict[str, Any]:
    papers = [project(path, root) for path in sorted((root / 'paper-acceptance').glob('*.json'))]
    return {
        'schema_version': '1.1',
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'papers': papers,
        'summary': {
            'papers': len(papers),
            'paper_acceptance_submission_ready': sum(p['paper_state'] == 'SUBMISSION_READY' for p in papers),
            'preparation_pass': sum(p['paper_preparation_status'] == 'PASS' for p in papers),
            'preparation_blocked': sum(p['paper_preparation_status'] == 'BLOCKED' for p in papers),
            'legacy_pending': sum(p['paper_preparation_status'] == 'LEGACY_PENDING' for p in papers),
            'machine_frozen_current': sum(p['freeze_status'] == 'MACHINE_FROZEN_CURRENT' for p in papers),
            'machine_freeze_stale': sum(p['freeze_status'] == 'MACHINE_FREEZE_STALE' for p in papers),
            'human_handoff_ready': sum(p['human_handoff_ready'] for p in papers),
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
