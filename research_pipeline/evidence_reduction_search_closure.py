from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

STATUS = "EVIDENCE_REDUCTION_SEARCH_CLOSURE_READY"


def _load(path: Path) -> dict[str, Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"expected JSON object: {path}")
    return value


def _sha_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_evidence_reduction_search_closure(*,evidence_plan: dict[str,Any],candidate_id: str,evidence_manifest: dict[str,Any],evidence_manifest_uri: str) -> dict[str,Any]:
    rows=[row for row in evidence_plan.get("entries") or [] if isinstance(row,dict) and str(row.get("candidate_id") or "")==candidate_id]
    if len(rows)!=1: raise ValueError(f"expected exactly one evidence row for {candidate_id}")
    row=rows[0];receipt=row.get("evidence_receipt") or {}
    if row.get("status")!="STOP_EXACT_REDUCTION_SUPPORTED" or row.get("execution_authorized") is not False:
        raise ValueError("search closure requires canonical STOP_EXACT_REDUCTION_SUPPORTED state")
    if receipt.get("outcome")!="REDUCTION_SUPPORTED" or receipt.get("protocol_valid") is not True:
        raise ValueError("search closure requires protocol-valid REDUCTION_SUPPORTED receipt")
    contract=str(row.get("contract_sha256") or "").lower();manifest_sha=str(receipt.get("evidence_manifest_sha256") or "").lower()
    if len(contract)!=64 or len(manifest_sha)!=64: raise ValueError("closure requires contract/evidence manifest digests")
    if str(evidence_manifest.get("candidate_id") or "")!=candidate_id or str(evidence_manifest.get("contract_sha256") or "").lower()!=contract:
        raise ValueError("evidence manifest candidate/contract mismatch")
    if str(evidence_manifest.get("evidence_manifest_sha256") or "").lower()!=manifest_sha:
        raise ValueError("evidence manifest digest mismatch")
    design=row.get("design") or {};prediction=str(row.get("frozen_exact_prediction") or design.get("frozen_exact_prediction") or "").strip();baseline=str(row.get("frozen_same_information_baseline") or design.get("frozen_same_information_baseline") or "").strip();metric=str(receipt.get("metric_summary") or "").strip()
    if not prediction or not baseline or not metric: raise ValueError("closure requires frozen prediction/baseline and metric summary")
    source_refs=sorted({str(ref) for ref in row.get("source_refs") or [] if str(ref)})
    reopen=("Reopen this exact search basin only if a new preregistered, protocol-valid same-information study changes only the presentation/retrieval order of the same fixed skill set and demonstrates a directionally consistent success or independently audited uptake residual on held-out tasks that the frozen static compatibility/negative-transfer baseline cannot express. Changing skill composition, skill content, task set, executor, budget, or merely renaming context interference does not reopen this closure.")
    return {
        "schema_version":"1.0","status":STATUS,"source_candidate_id":candidate_id,"title":str(row.get("title") or candidate_id),
        "contract_sha256":contract,"evidence_manifest_sha256":manifest_sha,"evidence_manifest_uri":evidence_manifest_uri,
        "evidence_outcome":"REDUCTION_SUPPORTED","qualified_units":int(receipt.get("qualified_units") or 0),"metric_summary":metric,
        "problem_text":prediction,"strongest_reduction":baseline,"source_refs":source_refs,"reopen_condition":reopen,
        "scientific_authority":False,"belief_authority":False,
    }


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument("--evidence-plan",type=Path,required=True);p.add_argument("--candidate-id",required=True);p.add_argument("--evidence-manifest",type=Path,required=True);p.add_argument("--evidence-manifest-uri",required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    manifest=_load(a.evidence_manifest);actual=_sha_bytes(a.evidence_manifest)
    # The content-addressed evidence digest is embedded in the manifest object; the file itself is pretty-printed, so file SHA need not equal it.
    out=build_evidence_reduction_search_closure(evidence_plan=_load(a.evidence_plan),candidate_id=a.candidate_id,evidence_manifest=manifest,evidence_manifest_uri=a.evidence_manifest_uri)
    out["source_evidence_manifest_file_sha256"]=actual
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8");print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
