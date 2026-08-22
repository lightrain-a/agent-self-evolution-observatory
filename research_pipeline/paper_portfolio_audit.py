from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from .paper_acceptance_ledger import validate_paper_ledger
from .paper_preparation_protocol import validate_paper_preparation_receipt

DEFAULT_ROOT=Path('/data/wyt/agent-self-evolution-observatory')

def digest(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def latest(row:Mapping[str,Any],kind:str)->dict[str,Any]:
 for e in reversed(row.get('events') or []):
  if isinstance(e,dict) and e.get('event_type')==kind:return e
 return {}

def blocker_group(value:str)->str:
 s=str(value)
 if any(x in s for x in ('claim-evidence','method-experiment','evidence_sufficiency','unresolved-critical')):return 'DECISIVE_EVIDENCE'
 if 'visual' in s:return 'VISUAL_CONTRACT'
 if 'reproducibility' in s:return 'REPRODUCIBILITY'
 if 'agent-native' in s or 'claim-raw' in s:return 'CLAIM_RAW_GROUNDING'
 if 'reader-' in s:return 'READER_SIMULATION'
 if 'submission-package' in s:return 'VENUE_HANDOFF'
 return 'OTHER'

def next_actions(groups:list[str])->list[str]:
 table={
  'DECISIVE_EVIDENCE':'close decision-critical claim-evidence gaps; support unavailability is support debt, not scientific counterevidence',
  'VISUAL_CONTRACT':'bind each core claim/boundary to a main-text visual contract',
  'REPRODUCIBILITY':'build a self-contained source/reproduction bundle and pass clean-room compile/recompute',
  'CLAIM_RAW_GROUNDING':'close claim-to-raw-evidence roundtrip in the agent-native artifact',
  'READER_SIMULATION':'complete figure-first and reproducibility readers and close critical objections',
  'VENUE_HANDOFF':'complete venue policy, AI-use/authorship checklist, supplement consistency, and fresh-source compile',
  'OTHER':'inspect remaining preparation blockers before human handoff',
 }
 return [table[g] for g in groups]

def project(path:Path)->dict[str,Any]:
 row=json.loads(path.read_text());pid=str(row.get('paper_id') or path.stem);contract=row.get('contract') or {};recorded=str(row.get('contract_sha256') or '')
 contract_ok=bool(recorded) and digest(contract)==recorded;ledger_errors=validate_paper_ledger(row);pe=latest(row,'paper-preparation');receipt=pe.get('receipt') if isinstance(pe.get('receipt'),dict) else {}
 receipt_ok=bool(receipt) and validate_paper_preparation_receipt(receipt) and receipt.get('contract_sha256')==recorded
 if receipt_ok:prep='PASS' if receipt.get('pass') is True else 'BLOCKED'
 elif row.get('current_state')=='SUBMISSION_READY':prep='LEGACY_PENDING'
 else:prep='NOT_ELIGIBLE'
 blockers=list(receipt.get('blockers') or []) if receipt_ok else ([] if prep!='LEGACY_PENDING' else ['paper-preparation-receipt-missing'])
 groups=[]
 for b in blockers:
  g=blocker_group(b)
  if g not in groups:groups.append(g)
 handoff=row.get('current_state')=='SUBMISSION_READY' and prep=='PASS' and contract_ok and not ledger_errors
 return {'paper_id':pid,'title':str(contract.get('title') or pid),'paper_state':str(row.get('current_state') or ''),'contract_integrity_pass':contract_ok,'ledger_replay_pass':not ledger_errors,'ledger_errors':ledger_errors,'paper_preparation_status':prep,'paper_preparation_passed_gates':int((receipt.get('summary') or {}).get('passed_gates') or 0) if receipt_ok else 0,'paper_preparation_required_gates':int((receipt.get('summary') or {}).get('required_gates') or 8),'paper_preparation_receipt_sha256':str(receipt.get('receipt_sha256') or '') if receipt_ok else '','blocker_groups':groups,'blocker_count':len(blockers),'next_actions':next_actions(groups) if groups else ([] if handoff else ['complete Paper Preparation migration before human handoff']),'human_handoff_ready':handoff,'submission_freeze_eligible':handoff,'authority':{'scientific':False,'experiment':False,'gpu':False,'submission':False}}

def build(root:Path=DEFAULT_ROOT)->dict[str,Any]:
 papers=[project(p) for p in sorted((root/'paper-acceptance').glob('*.json'))];return {'schema_version':'1.0','generated_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),'papers':papers,'summary':{'papers':len(papers),'paper_acceptance_submission_ready':sum(p['paper_state']=='SUBMISSION_READY' for p in papers),'preparation_pass':sum(p['paper_preparation_status']=='PASS' for p in papers),'preparation_blocked':sum(p['paper_preparation_status']=='BLOCKED' for p in papers),'legacy_pending':sum(p['paper_preparation_status']=='LEGACY_PENDING' for p in papers),'human_handoff_ready':sum(p['human_handoff_ready'] for p in papers),'submission_freeze_eligible':sum(p['submission_freeze_eligible'] for p in papers),'ledger_replay_failures':sum(not p['ledger_replay_pass'] for p in papers),'contract_integrity_failures':sum(not p['contract_integrity_pass'] for p in papers)},'authority':{'scientific':False,'experiment':False,'gpu':False,'submission':False}}

def main():
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,default=DEFAULT_ROOT);a.add_argument('--json-output',type=Path,default=Path('generated/paper-portfolio-audit.json'));a.add_argument('--js-output',type=Path,default=Path('generated/paper-portfolio-audit.js'));x=a.parse_args();v=build(x.root);v['audit_sha256']=digest(v);x.json_output.parent.mkdir(parents=True,exist_ok=True);x.json_output.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');x.js_output.write_text('window.PAPER_PORTFOLIO_AUDIT = '+json.dumps(v,ensure_ascii=False,separators=(',',':'))+';\n');print(json.dumps({'status':'PASS','summary':v['summary'],'audit_sha256':v['audit_sha256']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
