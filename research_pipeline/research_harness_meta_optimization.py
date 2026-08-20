from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION="1.0"
POLICY={
 "schema_version":SCHEMA_VERSION,
 "meta_optimizer_is_read_only_proposal_producer":True,
 "meta_optimizer_cannot_edit_research_corpus_or_code":True,
 "meta_optimizer_has_zero_scientific_authority":True,
 "proposal_application_requires_separate_landing_gate":True,
 "landing_requires_explicit_human_approval":True,
 "landing_requires_independent_resolved_model_family":True,
 "landing_requires_regression_tests_and_diff_receipt":True,
 "meta_optimization_cannot_relax_assurance_thresholds":True,
}

def _sha(v:Any)->str:return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _recent_cycle_failures(automation_dir:Path|None,limit:int=12)->Counter[str]:
 counts:Counter[str]=Counter()
 if automation_dir is None or not automation_dir.exists():return counts
 for path in sorted(automation_dir.glob("cycle-*.json"),key=lambda p:p.stat().st_mtime,reverse=True)[:limit]:
  try:p=json.loads(path.read_text(encoding="utf-8"))
  except (OSError,json.JSONDecodeError):continue
  for step in p.get("steps") or []:
   if isinstance(step,dict) and step.get("status")=="fail":counts[str(step.get("name") or "unknown")]+=1
 return counts
def build_research_harness_meta_optimization(*,integration_lint:dict[str,Any],stall_state:dict[str,Any],search_telemetry:dict[str,Any],automation_dir:Path|None=None)->dict[str,Any]:
 proposals=[];lint_failed=int((integration_lint.get("summary") or {}).get("failed") or 0);stale=int((stall_state.get("summary") or {}).get("stale_count") or 0);failures=_recent_cycle_failures(automation_dir)
 if lint_failed:proposals.append({"failure_pattern":"required-integration-contract-unwired","target_component":"integration-contract","proposed_change":"Wire or remove the orphan producer/consumer contract and add a regression test proving the live consumer path.","evidence":{"failed_contracts":lint_failed},"risk":"low"})
 if stale>=2:proposals.append({"failure_pattern":"repeated-zero-new-finding-search","target_component":"problem-discovery-harness","proposed_change":"Change the scientific-object/search-primitive/source frame before another automatic discovery transaction; more fan-out alone is not a structural pivot.","evidence":{"stale_count":stale,"directive":(stall_state.get("directive") or {}).get("action")},"risk":"medium"})
 for name,count in failures.most_common(4):
  if count>=2:proposals.append({"failure_pattern":f"repeated-automation-step-failure:{name}","target_component":name,"proposed_change":"Diagnose the repeated execution failure and propose the smallest launch/preflight safeguard without altering scientific thresholds.","evidence":{"failed_cycles":count},"risk":"low"})
 for row in proposals:
  row["proposal_id"]="META-"+_sha({"failure_pattern":row["failure_pattern"],"target_component":row["target_component"],"proposed_change":row["proposed_change"]})[:16];row["status"]="PROPOSED_NOT_APPLIED";row["required_landing_checks"]=["explicit-human-approval","independent-resolved-model-family","regression-tests-pass","git-diff-sha256","assurance-thresholds-unchanged"];row["scientific_authority"]=False
 bottleneck=str((search_telemetry.get("bottleneck") or {}).get("key") or "")
 return {"schema_version":SCHEMA_VERSION,"status":"META_PROPOSALS_READY" if proposals else "NO_META_PATCH_PROPOSED","policy":dict(POLICY),"summary":{"proposals":len(proposals),"repeated_cycle_failure_types":sum(c>=2 for c in failures.values()),"stale_count":stale,"integration_failures":lint_failed,"current_search_bottleneck":bottleneck},"proposals":proposals,"scientific_authority":False,"authority":{"apply_patch":False,"provider_calls":False,"problem_gate":False,"method":False,"experiment":False,"p0":False,"gpu":False}}
def validate_meta_change_landing(proposal:dict[str,Any],landing_receipt:dict[str,Any])->dict[str,Any]:
 author=str(landing_receipt.get("author_model_family") or "").strip();reviewer=str(landing_receipt.get("reviewer_model_family") or "").strip();checks={"proposal_is_unapplied":proposal.get("status")=="PROPOSED_NOT_APPLIED","explicit_human_approval":landing_receipt.get("explicit_human_approval") is True,"independent_reviewer_model_family":bool(author and reviewer and author!=reviewer),"regression_tests_pass":landing_receipt.get("regression_tests_pass") is True,"git_diff_sha256":len(str(landing_receipt.get("git_diff_sha256") or ""))==64,"assurance_thresholds_unchanged":landing_receipt.get("assurance_thresholds_unchanged") is True};passed=all(checks.values())
 return {"schema_version":SCHEMA_VERSION,"status":"LANDING_GATE_PASS" if passed else "LANDING_GATE_BLOCK","proposal_id":proposal.get("proposal_id"),"checks":checks,"apply_authorized_by_this_function":False,"scientific_authority":False}
