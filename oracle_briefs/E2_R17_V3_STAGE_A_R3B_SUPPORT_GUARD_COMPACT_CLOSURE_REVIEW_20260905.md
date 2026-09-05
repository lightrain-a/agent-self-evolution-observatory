# E2-R17 V3 Stage-A R3B — compact exact-code blocker-closure review

Date: 2026-09-05
Role: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology/control-plane reviewer
Scope: ZERO-PROVIDER exact-code closure review of ONLY the two blockers from the prior R1 review.

## 0. Review rule

The previous exact-code reviewer already PASSed minter structural-only behavior, terminal binding, support-authority narrowness, and preservation of the R3 adjudicator/scientific object, but returned `REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE` for exactly two blockers:

1. the support adjudicator remained directly invocable without an enforceable one-shot support-read gate;
2. the gate did not end-to-end validate the exact reviewed minter + control-review receipt provenance, and negative tests did not cover those bypasses.

R3B changes only this control plane. Do NOT reopen matched-censor geometry, no-replay/replacement, 158 provider tasks + 1 matched censor + 1 terminal technical missing, K=8, 7/7/8 opportunity geometry, >=4 mixed-pool support threshold, or Stage-B design unless the exact code below changed those frozen objects. Do NOT infer Stage-A support or Stage-B effect. Do NOT request more scientific workload for appearance.

Hard time gate remains: `NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`. Even a PASS here authorizes no provider call before that time and does not itself authorize recovery execution, support read, or Stage B.

This compact packet is intentionally smaller than the 2393-line omnibus packet. It contains the complete verdict-changing code paths for the two prior blockers, the exact negative tests, frozen hashes/equality, and zero-provider preflight. No scientific code was edited to create this packet.

Final provider-recovery verdict must be exactly one of:
- `PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION`
- `REVISE_R3B_BEFORE_PROVIDER_RECOVERY`
- `STOP_R3_RECOVERY`

Also return `support_control_verdict` exactly one of:
- `PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`
- `FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`

## 1. Frozen object hashes and prior blockers

```json
{
  "parent_r3_contract_sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "r3b_contract_sha256": "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9",
  "frozen_r3b_support_guard_preflight_sha256": "94043973e6b89edf0e0132e8c503854063ab3ea32801ccc2766359554264084f",
  "prior_r1_review_sha256": "48bb7a5d51c99d2ed60fb844423eaa87c455d7f56ce49a1adecaeb9f6373c3e4",
  "prior_r1_verdict": "REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE",
  "prior_r1_remaining_blockers": [
    "Make the support adjudicator enforceably reachable only through the support-read-authorized one-shot gate; direct invocation must not remain an authority bypass.",
    "Make the gate verify provenance/binding to the exact reviewed minter and control-review receipt, and add zero-provider regression tests for direct-invocation and forged-permit bypasses."
  ],
  "control_plane_revision": "R3B_POST_TERMINAL_SUPPORT_GUARD",
  "relevant_bound_code": {
    "equal_dose_adjudicator": {
      "path": "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "sha256": "d8ad232562b5f88f7394555c158d83b7e00dd235f2ef8631c89a3cabe6b896eb"
    },
    "post_terminal_support_minter": {
      "path": "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py",
      "sha256": "0e7bf96b3e6274de8c6e5738b46924990de8b8897c04bb3871fce0e5fdd06d43"
    },
    "post_terminal_support_gate": {
      "path": "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py",
      "sha256": "333c3ef89746c4d7e44b20769e068b0520140dffb4fa79f32da1f9e981cefb10"
    },
    "post_terminal_support_tests": {
      "path": "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py",
      "sha256": "7a9c51fc7a24df34469efa71a6e2301e6aeab182d110e23cd460a646ecc002db"
    },
    "r3b_support_guard_preflight": {
      "path": "scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py",
      "sha256": "f7b8c18e5f7ee02155252b9739d6f17ab2258227ba9fcb1bbde1e532cd26f606"
    },
    "stage_a_runner": {
      "path": "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "sha256": "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
    },
    "authorization_minter": {
      "path": "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "sha256": "9866bcffb09b4d6a6f31c5c8e947c6107a8bf35e09b8ddc81a6ef6350d6278df"
    }
  },
  "science_key_equality_parent_r3": {
    "failed_r2_parent": true,
    "suite": true,
    "mindmemos": true,
    "provider_route": true,
    "model_identity_policy": true,
    "recovery_exceptions": true,
    "recovery_opportunity_manifest": true,
    "exact_once_acquisition": true,
    "equal_dose_support": true,
    "actor": true,
    "budget": true,
    "analysis_boundary": true,
    "stage_b_plan_no_authority": true,
    "runtime": true,
    "env_file_path": true,
    "run_root": true,
    "global_lease_path": true
  },
  "authority": {
    "analyzer": false,
    "heldout_evaluation": false,
    "paper_promotion": false,
    "public_benchmark": false,
    "second_backbone": false,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false,
    "submission": false,
    "updater": false
  },
  "analysis_boundary": {
    "heldout_access": false,
    "partial_learning_effect_read": false,
    "scientific_learning_effect_read": false,
    "stage_a_support_only": true,
    "stage_b_effect_inference": false,
    "support_read_before_terminal_recovery": false
  },
  "provider_reset_control": null
}
```

## 2. Guarded adjudicator: direct invocation must fail without permit + consumption marker

### `scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py` lines 1-130
Whole-file SHA256: `d8ad232562b5f88f7394555c158d83b7e00dd235f2ef8631c89a3cabe6b896eb`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
CONSUMPTION_NAME = "post_terminal_support_read_authorization.consumed.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def req(c: bool, m: str) -> None:
    if not c: raise RuntimeError(m)

def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    os.replace(tmp,path)

def bound(raw: str) -> Path:
    p=Path(raw); return p if p.is_absolute() else ROOT/p

def choose_four(stream_id: str, mixed: list[str]) -> list[str]:
    req(len(mixed)>=4,f"insufficient mixed pools: {stream_id}")
    return sorted(mixed,key=lambda t:hashlib.sha256(f"semantic-transfer-mrw4-v3|{stream_id}|{t}".encode()).hexdigest())[:4]

def choose_ten(scores: dict[str,float], *, descending: bool, salt: str) -> list[str]:
    req(len(scores)==20,"router stream universe drift")
    def key(s: str):
        primary=-scores[s] if descending else scores[s]
        return primary,hashlib.sha256(f"{salt}|{s}".encode()).hexdigest()
    return sorted(scores,key=key)[:10]

def failed_witness(rows: list[dict[str,Any]], winner: int) -> dict[str,Any]:
    xs=[r for r in rows if float(r["score"])==0.0 and int(r["rollout_index"])!=winner]
    req(bool(xs),"mixed pool lacks failed nonwinner")
    r=min(xs,key=lambda x:int(x["rollout_index"]))
    return {"rollout_index":int(r["rollout_index"]),"trajectory_path":str(r["trajectory_path"]),"trajectory_sha256":str(r["trajectory_sha256"]),"score":0.0,"selector":"lowest original rollout index among verifier-failure nonwinner trajectories"}


def validate_support_read_gate(*, contract: dict[str,Any], contract_path: Path, recovery_authorization_path: Path, summary_path: Path, support_authorization_path: Path, consumption_marker_path: Path, output_path: Path, csha: str, asha: str) -> dict[str,Any]:
    req(contract.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3B support-control revision absent")
    support_auth=load(support_authorization_path)
    req(support_auth.get("status")==SUPPORT_AUTH_STATUS and support_auth.get("single_use") is True,"R3B support-read authorization invalid")
    req(support_auth.get("contract_sha256")==csha,"R3B support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256")==asha,"R3B support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256")==sha(summary_path),"R3B support-read terminal-summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve()==contract_path.resolve(),"R3B support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve()==recovery_authorization_path.resolve(),"R3B support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve()==summary_path.resolve(),"R3B support-read terminal-summary path drift")
    authority=support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True,"R3B Stage-A support-read authority absent")
    for key in ("stage_a_provider_execution","stage_b_learning_execution","updater","heldout_evaluation","analyzer","second_backbone","public_benchmark","paper_promotion","submission"):
        req(authority.get(key) is False,f"R3B support-read authorization overbroad: {key}")

    control=support_auth.get("bound_control_plane") or {}
    minter_path=Path(str(control.get("minter_path") or "")); gate_path=Path(str(control.get("gate_path") or "")); adjudicator_path=Path(str(control.get("support_adjudicator_path") or ""))
    req(minter_path.is_file() and control.get("minter_sha256")==sha(minter_path),"R3B minter provenance drift")
    req(gate_path.is_file() and control.get("gate_sha256")==sha(gate_path),"R3B gate provenance drift")
    req(adjudicator_path.resolve()==Path(__file__).resolve() and control.get("support_adjudicator_sha256")==sha(Path(__file__)),"R3B guarded adjudicator provenance drift")
    for key,path in (("post_terminal_support_minter",minter_path),("post_terminal_support_gate",gate_path),("equal_dose_adjudicator",Path(__file__))):
        row=(contract.get("bound_code") or {}).get(key) or {}
        req(bound(str(row.get("path") or "")).resolve()==path.resolve() and row.get("sha256")==sha(path),f"R3B contract bound-code drift: {key}")

    review_row=support_auth.get("control_review") or {}; review_path=Path(str(review_row.get("path") or ""))
    req(review_path.is_file() and review_row.get("sha256")==sha(review_path),"R3B control-review receipt binding drift")
    review=load(review_path)
    req(review.get("status")=="COMPLETED" and review.get("surface")=="ChatGPT web" and review.get("model")=="GPT-5.6 Sol","R3B control-review provenance drift")
    req(review.get("verdict")==CONTROL_REVIEW_VERDICT and review_row.get("verdict")==CONTROL_REVIEW_VERDICT,"R3B control-review verdict drift")
    req(review.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3B control-review revision drift")
    req(review.get("minter_sha256_acknowledged")==control.get("minter_sha256"),"R3B review/minter SHA drift")
    req(review.get("gate_sha256_acknowledged")==control.get("gate_sha256"),"R3B review/gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged")==control.get("support_adjudicator_sha256"),"R3B review/adjudicator SHA drift")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False,"R3B control review grants forbidden authority")

    scope=support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve()==output_path.resolve(),"R3B support-adjudication output path drift")
    run_root=Path(str(scope.get("required_run_root") or "")); req(run_root.resolve()==Path(contract["run_root"]).resolve(),"R3B support-read run-root drift")
    expected_marker=run_root/"checkpoints/post_terminal_support_read"/CONSUMPTION_NAME
    req(consumption_marker_path.resolve()==expected_marker.resolve() and consumption_marker_path.is_file(),"R3B gate consumption marker absent/path drift")
    marker=load(consumption_marker_path)
    req(marker.get("artifact_type")=="e2-r17-v3-stage-a-r3-post-terminal-support-read-consumption" and marker.get("status")=="CONSUMED_IN_FLIGHT_DO_NOT_RETRY","R3B gate consumption marker status drift")
    req(marker.get("support_authorization_sha256")==sha(support_authorization_path),"R3B gate consumption support-auth SHA drift")
    req(marker.get("terminal_summary_sha256")==sha(summary_path),"R3B gate consumption summary SHA drift")
    req(Path(str(marker.get("required_output") or "")).resolve()==output_path.resolve(),"R3B gate consumption output drift")
    req(marker.get("gate_sha256")==sha(gate_path),"R3B gate consumption gate SHA drift")
    req(marker.get("control_review_sha256")==sha(review_path),"R3B gate consumption review SHA drift")
    req(marker.get("stage_b_authority") is False,"R3B gate consumption grants Stage-B authority")
    return {"support_authorization":support_auth,"support_authorization_sha256":sha(support_authorization_path),"consumption_marker_sha256":sha(consumption_marker_path),"control_review_sha256":sha(review_path)}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,required=True)
    ap.add_argument("--authorization",type=Path,required=True)
    ap.add_argument("--summary",type=Path,required=True)
    ap.add_argument("--support-authorization",type=Path,required=True)
    ap.add_argument("--consumption-marker",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args(); req(not a.output.exists(),"R3 support adjudication already exists")
    c,auth,s=load(a.contract),load(a.authorization),load(a.summary)
    csha,asha=sha(a.contract),sha(a.authorization)
    req(c["status"]==CONTRACT_STATUS and auth["status"]==AUTH_STATUS,"R3 contract/auth status invalid")
    req(auth["contract_sha256"]==csha,"R3 auth contract drift")
    req(s["status"]==SUMMARY_STATUS and s["contract_sha256"]==csha and s["authorization_sha256"]==asha,"R3 terminal summary binding drift")
    req(s["planned_tasks"]==160 and s["provider_executable_tasks"]==158 and s["sealed_k8_pools"]==158,"R3 terminal accounting drift")
    req(s["terminal_technical_missing"]==1 and s["matched_no_provider_censor"]==1,"R3 exception accounting drift")
    req(s["support_inspected"] is False and s["updater_calls"]==0 and s["heldout_evaluations"]==0,"R3 crossed support/learning boundary")
    guard=validate_support_read_gate(contract=c,contract_path=a.contract,recovery_authorization_path=a.authorization,summary_path=a.summary,support_authorization_path=a.support_authorization,consumption_marker_path=a.consumption_marker,output_path=a.output,csha=csha,asha=asha)

    om=c["recovery_opportunity_manifest"]; opath=bound(om["path"])
    req(opath.is_file() and sha(opath)==om["sha256"],"R3 opportunity manifest drift")
    o=load(opath); stream_ids=[str(x) for x in o["ordered_stream_ids"]]
    streams={str(k):[str(x) for x in v] for k,v in o["support_eligible_task_ids_by_stream"].items()}
```

## 3. Support-read minter: exact review/minter/gate/adjudicator binding and narrow authority

### `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py` lines 1-69
Whole-file SHA256: `0e7bf96b3e6274de8c6e5738b46924990de8b8897c04bb3871fce0e5fdd06d43`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
RECOVERY_AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
LEASE_STATUS = "COMPLETED_STAGE_A_V3_R3_RECOVERY_PENDING_EQUAL_DOSE_ADJUDICATION"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
EXPECTED_SUPPORT_ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
EXPECTED_GATE = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
EXPECTED_ADJUDICATION_OUTPUT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def bound(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def task_claim_paths(claim_root: Path, task_id: str) -> tuple[Path, Path]:
    stem = hashlib.sha256(task_id.encode("utf-8")).hexdigest()
    return claim_root / f"{stem}.attempt.json", claim_root / f"{stem}.sealed.json"


def validate_control_review(review_path: Path, *, minter_sha: str, gate_sha: str, support_adjudicator_sha: str) -> dict[str, Any]:
    review = load(review_path)
    req(review.get("status") == "COMPLETED", "post-terminal control review is not completed")
    req(review.get("surface") == "ChatGPT web", "post-terminal control review surface drift")
    req(review.get("model") == "GPT-5.6 Sol", "post-terminal control review model drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT, "post-terminal control review did not PASS")
    req(review.get("minter_sha256_acknowledged") == minter_sha, "post-terminal control review minter SHA drift")
    req(review.get("gate_sha256_acknowledged") == gate_sha, "post-terminal control review gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged") == support_adjudicator_sha, "post-terminal control review support-adjudicator SHA drift")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "post-terminal control review revision drift")
    req(review.get("stage_b_authority") is False, "post-terminal control review grants Stage-B authority")
    req(review.get("scientific_authority") is False, "post-terminal control review grants scientific authority")
    return review
```
### `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py` lines 196-325
Whole-file SHA256: `0e7bf96b3e6274de8c6e5738b46924990de8b8897c04bb3871fce0e5fdd06d43`

```python
def build_support_authorization(
    *,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    control_review_path: Path,
    output_path: Path,
    adjudication_output_path: Path = EXPECTED_ADJUDICATION_OUTPUT,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    req(not output_path.exists(), "post-terminal support-read authorization already exists")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file(), "R3B guarded support adjudicator absent")
    req(EXPECTED_GATE.is_file(), "post-terminal support gate absent")
    minter_sha = sha(Path(__file__))
    gate_sha = sha(EXPECTED_GATE)
    support_adjudicator_sha = sha(EXPECTED_SUPPORT_ADJUDICATOR)
    state = validate_terminal_structure(
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
    )
    contract = state["contract"]
    bound_code = contract.get("bound_code") or {}
    for key, path, expected_sha in (
        ("post_terminal_support_minter", Path(__file__), minter_sha),
        ("post_terminal_support_gate", EXPECTED_GATE, gate_sha),
        ("equal_dose_adjudicator", EXPECTED_SUPPORT_ADJUDICATOR, support_adjudicator_sha),
    ):
        row = bound_code.get(key) or {}
        req(bound(str(row.get("path") or "")).resolve() == path.resolve(), f"R3B contract {key} path drift")
        req(row.get("sha256") == expected_sha, f"R3B contract {key} SHA drift")
    review = validate_control_review(
        control_review_path,
        minter_sha=minter_sha,
        gate_sha=gate_sha,
        support_adjudicator_sha=support_adjudicator_sha,
    )
    req(not adjudication_output_path.exists(), "R3 support adjudication output already exists")

    timestamp = created_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-authorization",
        "created_at_utc": timestamp,
        "status": SUPPORT_AUTH_STATUS,
        "single_use": True,
        "provider_calls": 0,
        "scientific_execution": False,
        "contract_path": str(contract_path),
        "contract_sha256": state["contract_sha256"],
        "recovery_authorization_path": str(recovery_authorization_path),
        "recovery_authorization_sha256": state["recovery_authorization_sha256"],
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": state["summary_sha256"],
        "terminal_lease_path": str(state["lease_path"]),
        "terminal_lease_sha256": sha(state["lease_path"]),
        "control_review": {
            "path": str(control_review_path.resolve()),
            "sha256": sha(control_review_path),
            "verdict": review["verdict"],
            "model": review["model"],
            "surface": review["surface"],
        },
        "bound_control_plane": {
            "minter_path": str(Path(__file__).resolve()),
            "minter_sha256": minter_sha,
            "gate_path": str(EXPECTED_GATE),
            "gate_sha256": gate_sha,
            "support_adjudicator_path": str(EXPECTED_SUPPORT_ADJUDICATOR),
            "support_adjudicator_sha256": support_adjudicator_sha,
        },
        "execution_scope": {
            "required_adjudication_output": str(adjudication_output_path),
            "required_run_root": str(state["run_root"]),
            "provider_execution_tasks": 158,
            "sealed_k8_pools": 158,
            "terminal_technical_missing": BURNED,
            "matched_no_provider_censor": CENSOR,
            "support_required_mixed_pools_per_stream": 4,
            "opportunity_geometry": "7/7/8",
            "support_read_may_open_k8_pool_semantics": True,
            "support_read_before_terminal_recovery": False,
        },
        "authority": {
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
        "interpretation_boundary": "Single-use zero-provider authority to invoke the already exact-hash-reviewed R3 Stage-A support adjudicator after the exact terminal recovery state only. It grants no provider execution, updater, heldout, Stage-B execution, public benchmark, analyzer, or paper-claim authority.",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--control-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--adjudication-output", type=Path, default=EXPECTED_ADJUDICATION_OUTPUT)
    args = parser.parse_args()
    payload = build_support_authorization(
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        control_review_path=args.control_review,
        output_path=args.output,
        adjudication_output_path=args.adjudication_output,
    )
    atomic(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "terminal_summary_sha256": payload["terminal_summary_sha256"],
        "authority": payload["authority"],
        "provider_calls": 0,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 4. One-shot gate: provenance validation, O_EXCL consumption, fail-closed invocation

### `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py` lines 1-260
Whole-file SHA256: `333c3ef89746c4d7e44b20769e068b0520140dffb4fa79f32da1f9e981cefb10`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
EXPECTED_SUPPORT_ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
CONSUMPTION_NAME = "post_terminal_support_read_authorization.consumed.json"
COMPLETION_NAME = "post_terminal_support_read_adjudication.completed.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _exclusive_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def validate_support_authorization(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    support_auth = load(support_authorization_path)
    req(support_auth.get("status") == SUPPORT_AUTH_STATUS, "post-terminal support-read authorization status drift")
    req(support_auth.get("single_use") is True, "post-terminal support-read authorization is not single-use")
    req(support_auth.get("provider_calls") == 0, "post-terminal support-read authorization provider-call drift")
    req(support_auth.get("scientific_execution") is False, "post-terminal support-read authorization incorrectly records scientific execution")

    authority = support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True, "Stage-A support-read authority absent")
    for key in (
        "stage_a_provider_execution",
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
    ):
        req(authority.get(key) is False, f"post-terminal support-read authorization overbroad: {key}")

    req(support_auth.get("contract_sha256") == sha(contract_path), "post-terminal support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256") == sha(recovery_authorization_path), "post-terminal support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256") == sha(summary_path), "post-terminal support-read summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve() == contract_path.resolve(), "post-terminal support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve() == recovery_authorization_path.resolve(), "post-terminal support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve() == summary_path.resolve(), "post-terminal support-read summary path drift")

    summary = load(summary_path)
    req(summary.get("status") == SUMMARY_STATUS, "terminal summary no longer at pending-support boundary")
    req(summary.get("support_inspected") is False, "terminal summary indicates support already inspected")
    req(summary.get("stage_b_authority") is False, "terminal summary grants Stage-B authority")

    control = support_auth.get("bound_control_plane") or {}
    minter_path = Path(str(control.get("minter_path") or ""))
    gate_path = Path(str(control.get("gate_path") or ""))
    adjudicator_path = Path(str(control.get("support_adjudicator_path") or ""))
    req(minter_path.is_file() and control.get("minter_sha256") == sha(minter_path), "support-read minter provenance drift")
    req(gate_path.resolve() == Path(__file__).resolve() and control.get("gate_sha256") == sha(Path(__file__)), "support-read gate SHA drift")
    req(adjudicator_path.resolve() == EXPECTED_SUPPORT_ADJUDICATOR.resolve(), "support adjudicator path drift")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file() and control.get("support_adjudicator_sha256") == sha(EXPECTED_SUPPORT_ADJUDICATOR), "guarded support adjudicator SHA drift")

    review_row = support_auth.get("control_review") or {}
    review_path = Path(str(review_row.get("path") or ""))
    req(review_path.is_file() and review_row.get("sha256") == sha(review_path), "support-read control-review receipt binding drift")
    review = load(review_path)
    req(review.get("status") == "COMPLETED" and review.get("surface") == "ChatGPT web" and review.get("model") == "GPT-5.6 Sol", "support-read control-review provenance drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT and review_row.get("verdict") == CONTROL_REVIEW_VERDICT, "support-read control-review verdict drift")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "support-read control-review revision drift")
    req(review.get("minter_sha256_acknowledged") == control.get("minter_sha256"), "support-read review/minter SHA drift")
    req(review.get("gate_sha256_acknowledged") == control.get("gate_sha256"), "support-read review/gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged") == control.get("support_adjudicator_sha256"), "support-read review/adjudicator SHA drift")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False, "support-read control review grants forbidden authority")

    scope = support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve() == output_path.resolve(), "support adjudication output path drift")
    req(scope.get("provider_execution_tasks") == 158 and scope.get("sealed_k8_pools") == 158, "post-terminal support-read geometry drift")
    req(scope.get("opportunity_geometry") == "7/7/8", "post-terminal support-read opportunity geometry drift")
    req(scope.get("support_required_mixed_pools_per_stream") == 4, "post-terminal support threshold drift")

    run_root = Path(str(scope.get("required_run_root") or ""))
    req(run_root.is_dir(), "post-terminal support-read run root absent")
    lease_path = Path(str(support_auth.get("terminal_lease_path") or ""))
    req(lease_path.is_file() and support_auth.get("terminal_lease_sha256") == sha(lease_path), "post-terminal support-read lease binding drift")
    return {"support_authorization": support_auth, "summary": summary, "run_root": run_root, "lease_path": lease_path}


def default_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def run_gate(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    output_path: Path,
    invoke: Callable[[list[str]], subprocess.CompletedProcess[str]] = default_invoke,
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    req(not output_path.exists(), "R3 support adjudication output already exists")
    state = validate_support_authorization(
        support_authorization_path=support_authorization_path,
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
        output_path=output_path,
    )
    run_root: Path = state["run_root"]
    control_root = run_root / "checkpoints/post_terminal_support_read"
    consumption = control_root / CONSUMPTION_NAME
    completion = control_root / COMPLETION_NAME
    req(not consumption.exists(), "post-terminal support-read authorization already consumed; retry forbidden")
    req(not completion.exists(), "post-terminal support adjudication completion receipt already exists")

    auth_sha = sha(support_authorization_path)
    summary_sha = sha(summary_path)
    support_auth = state["support_authorization"]
    review_row = support_auth["control_review"]
    consumption_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-consumption",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
        "support_authorization_path": str(support_authorization_path),
        "support_authorization_sha256": auth_sha,
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": summary_sha,
        "required_output": str(output_path),
        "gate_sha256": sha(Path(__file__)),
        "control_review_sha256": review_row["sha256"],
        "automatic_retry": False,
        "stage_b_authority": False,
    }
    _exclusive_json(consumption, consumption_payload)

    command = [
        python_executable,
        str(EXPECTED_SUPPORT_ADJUDICATOR),
        "--contract",
        str(contract_path),
        "--authorization",
        str(recovery_authorization_path),
        "--summary",
        str(summary_path),
        "--support-authorization",
        str(support_authorization_path),
        "--consumption-marker",
        str(consumption),
        "--output",
        str(output_path),
    ]
    result = invoke(command)
    if result.returncode not in {0, 3}:
        raise RuntimeError(
            "R3 support adjudicator failed outside terminal PASS/HOLD states; support-read permit remains consumed and manual review is required. "
            f"returncode={result.returncode}; stdout_tail={result.stdout[-1200:]}; stderr_tail={result.stderr[-1200:]}"
        )
    req(output_path.is_file(), "R3 support adjudicator returned terminal code without output artifact")
    adjudication = load(output_path)
    expected_statuses = {
        0: "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
        3: "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
    }
    req(adjudication.get("status") == expected_statuses[result.returncode], "R3 support adjudicator terminal status/returncode mismatch")
    authority = adjudication.get("authority") or {}
    req(authority.get("execute_stage_b") is False, "R3 support adjudication improperly grants Stage-B execution")
    req(authority.get("heldout_evaluation") is False, "R3 support adjudication improperly grants heldout evaluation")
    req(authority.get("analyzer") is False, "R3 support adjudication improperly grants analyzer authority")
    req(authority.get("paper_promotion") is False, "R3 support adjudication improperly grants paper-promotion authority")

    completion_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-completion",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED_POST_TERMINAL_SUPPORT_READ",
        "support_authorization_sha256": auth_sha,
        "consumption_path": str(consumption),
        "consumption_sha256": sha(consumption),
        "terminal_summary_sha256": summary_sha,
        "adjudication_output": str(output_path),
        "adjudication_output_sha256": sha(output_path),
        "adjudication_status": adjudication["status"],
        "adjudicator_returncode": result.returncode,
        "stage_b_authority": False,
        "automatic_retry": False,
    }
    _exclusive_json(completion, completion_payload)
    return {
        "status": completion_payload["status"],
        "adjudication_status": adjudication["status"],
        "returncode": result.returncode,
        "consumption_path": str(consumption),
        "completion_path": str(completion),
        "stage_b_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--support-authorization", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_gate(
        support_authorization_path=args.support_authorization,
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        output_path=args.output,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 5. Exact blocker-focused regression tests

### `research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py` lines 150-371
Whole-file SHA256: `7a9c51fc7a24df34469efa71a6e2301e6aeab182d110e23cd460a646ecc002db`

```python
        }
        write_json(summary, summary_payload)
        ssha = sha(summary)
        write_json(
            lease,
            {
                "schema_version": "1.0",
                "status": minter.LEASE_STATUS,
                "contract_sha256": csha,
                "authorization_sha256": asha,
                "summary_path": str(summary),
                "summary_sha256": ssha,
            },
        )

        control_review = root / "control-review.json"
        write_json(
            control_review,
            {
                "schema_version": "1.0",
                "status": "COMPLETED",
                "surface": "ChatGPT web",
                "model": "GPT-5.6 Sol",
                "verdict": minter.CONTROL_REVIEW_VERDICT,
                "control_plane_revision": minter.CONTROL_PLANE_REVISION,
                "minter_sha256_acknowledged": sha(Path(minter.__file__)),
                "gate_sha256_acknowledged": sha(Path(gate.__file__)),
                "support_adjudicator_sha256_acknowledged": sha(minter.EXPECTED_SUPPORT_ADJUDICATOR),
                "stage_b_authority": False,
                "scientific_authority": False,
            },
        )
        return {
            "root": root,
            "run": run,
            "contract": contract,
            "recovery_auth": recovery_auth,
            "summary": summary,
            "lease": lease,
            "control_review": control_review,
            "support_auth": root / "support-auth.json",
            "adjudication_output": root / "support-adjudication.json",
        }

    def build_auth(self, fixture: dict[str, Path]) -> dict:
        payload = minter.build_support_authorization(
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            control_review_path=fixture["control_review"],
            output_path=fixture["support_auth"],
            adjudication_output_path=fixture["adjudication_output"],
            created_at_utc="2026-09-07T00:01:00+08:00",
        )
        write_json(fixture["support_auth"], payload)
        return payload

    def test_minter_rejects_absent_or_nonterminal_summary(self) -> None:
        fixture = self.make_fixture()
        missing = fixture["root"] / "missing-summary.json"
        with self.assertRaises(FileNotFoundError):
            minter.build_support_authorization(
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=missing,
                control_review_path=fixture["control_review"],
                output_path=fixture["support_auth"],
                adjudication_output_path=fixture["adjudication_output"],
            )
        summary = json.loads(fixture["summary"].read_text())
        summary["status"] = "RUNNING"
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "terminal summary status drift"):
            self.build_auth(fixture)

    def test_minter_rejects_support_already_inspected(self) -> None:
        fixture = self.make_fixture()
        summary = json.loads(fixture["summary"].read_text())
        summary["support_inspected"] = True
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "already inspected support"):
            self.build_auth(fixture)

    def test_minter_rejects_recovery_authorization_hash_drift(self) -> None:
        fixture = self.make_fixture()
        auth = json.loads(fixture["recovery_auth"].read_text())
        auth["tampered"] = True
        write_json(fixture["recovery_auth"], auth)
        with self.assertRaisesRegex(RuntimeError, "summary authorization SHA drift"):
            self.build_auth(fixture)

    def test_minter_grants_only_stage_a_support_read(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        self.assertTrue(payload["authority"]["stage_a_support_read"])
        self.assertFalse(payload["authority"]["stage_a_provider_execution"])
        self.assertFalse(payload["authority"]["stage_b_learning_execution"])
        self.assertFalse(payload["authority"]["heldout_evaluation"])
        self.assertEqual(payload["provider_calls"], 0)
        self.assertFalse(payload["scientific_execution"])

    def test_gate_refuses_invalid_support_authorization(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        payload["authority"]["stage_a_support_read"] = False
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "support-read authority absent"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
            )
        consumption = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.CONSUMPTION_NAME
        self.assertFalse(consumption.exists())

    def test_gate_rejects_forged_permit_without_review_provenance(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        forged_review = fixture["root"] / "forged-review.json"
        write_json(forged_review, {"status": "COMPLETED", "surface": "ChatGPT web", "model": "GPT-5.6 Sol", "verdict": minter.CONTROL_REVIEW_VERDICT})
        payload["control_review"]["path"] = str(forged_review)
        payload["control_review"]["sha256"] = sha(forged_review)
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "review/minter SHA drift|control-review revision drift|control-review receipt binding drift"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
            )

    def test_guarded_adjudicator_rejects_direct_invocation_without_support_permit(self) -> None:
        fixture = self.make_fixture()
        command = [
            sys.executable,
            str(minter.EXPECTED_SUPPORT_ADJUDICATOR),
            "--contract",
            str(fixture["contract"]),
            "--authorization",
            str(fixture["recovery_auth"]),
            "--summary",
            str(fixture["summary"]),
            "--output",
            str(fixture["adjudication_output"]),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--support-authorization", result.stderr)
        self.assertFalse(fixture["adjudication_output"].exists())

    def test_gate_consumes_once_and_fail_closes_on_unexpected_adjudicator_error(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)

        def failed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 2, stdout="", stderr="synthetic failure")

        with self.assertRaisesRegex(RuntimeError, "permit remains consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )
        control = fixture["run"] / "checkpoints/post_terminal_support_read"
        self.assertTrue((control / gate.CONSUMPTION_NAME).is_file())
        self.assertFalse((control / gate.COMPLETION_NAME).exists())
        with self.assertRaisesRegex(RuntimeError, "already consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )

    def test_gate_accepts_terminal_pass_without_stage_b_authority(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)

        def passed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            self.assertIn("--support-authorization", command)
            self.assertIn("--consumption-marker", command)
            output = Path(command[command.index("--output") + 1])
            write_json(
                output,
                {
                    "status": "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
                    "authority": {
                        "prepare_stage_b_contract": True,
                        "execute_stage_b": False,
                        "heldout_evaluation": False,
                        "analyzer": False,
                        "paper_promotion": False,
                    },
                },
            )
            return subprocess.CompletedProcess(command, 0, stdout="synthetic pass", stderr="")

        result = gate.run_gate(
            support_authorization_path=fixture["support_auth"],
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            output_path=fixture["adjudication_output"],
            invoke=passed_invoke,
        )
        self.assertEqual(result["status"], "COMPLETED_POST_TERMINAL_SUPPORT_READ")
        self.assertFalse(result["stage_b_authority"])
        completion = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.COMPLETION_NAME
        self.assertTrue(completion.is_file())
        self.assertFalse(json.loads(completion.read_text())["stage_b_authority"])


if __name__ == "__main__":
    unittest.main()
```

### Fresh zero-provider test rerun

```text
test_gate_accepts_terminal_pass_without_stage_b_authority (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_gate_accepts_terminal_pass_without_stage_b_authority) ... ok
test_gate_consumes_once_and_fail_closes_on_unexpected_adjudicator_error (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_gate_consumes_once_and_fail_closes_on_unexpected_adjudicator_error) ... ok
test_gate_refuses_invalid_support_authorization (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_gate_refuses_invalid_support_authorization) ... ok
test_gate_rejects_forged_permit_without_review_provenance (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_gate_rejects_forged_permit_without_review_provenance) ... ok
test_guarded_adjudicator_rejects_direct_invocation_without_support_permit (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_guarded_adjudicator_rejects_direct_invocation_without_support_permit) ... ok
test_minter_grants_only_stage_a_support_read (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_minter_grants_only_stage_a_support_read) ... ok
test_minter_rejects_absent_or_nonterminal_summary (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_minter_rejects_absent_or_nonterminal_summary) ... ok
test_minter_rejects_recovery_authorization_hash_drift (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_minter_rejects_recovery_authorization_hash_drift) ... ok
test_minter_rejects_support_already_inspected (research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control.R3PostTerminalSupportReadControlTests.test_minter_rejects_support_already_inspected) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.901s

OK
```

## 6. Frozen R3B support-guard preflight

Frozen preflight SHA256: `94043973e6b89edf0e0132e8c503854063ab3ea32801ccc2766359554264084f`

```json
{
  "actual_support_read_authorization_minted": false,
  "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-r3b-support-guard-zero-provider-preflight",
  "authority": {
    "heldout": false,
    "paper_claim": false,
    "provider_recovery": false,
    "stage_a_support_read": false,
    "stage_b_execution": false
  },
  "authority_review_path": "generated/e2-r17-v3-r3-post-terminal-support-authority-gpt56-review-20260905.json",
  "authority_review_sha256": "575ab2f4535d994bfd23e2dedcd9effbc26d8d358f5c3b1b3d26411c7f0d6846",
  "checks": {
    "all_bound_code_hashes_match": true,
    "fresh_r3b_lineage_absent": true,
    "post_terminal_support_control_bound": true,
    "provider_recovery_runner_unchanged": true,
    "support_control_compile_pass": true,
    "support_control_tests_9_of_9_pass": true,
    "support_read_artifacts_absent": true
  },
  "contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3b-support-guard-20260905.json",
  "contract_sha256": "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9",
  "created_at_utc": "2026-09-05T14:55:32+00:00",
  "fresh_identity_qualified": false,
  "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_R3B_EXACT_HASH_PREEXECUTION_REVIEW_THEN_PROVIDER_RESET_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
  "parent_r3_contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json",
  "parent_r3_contract_sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "provider_calls": 0,
  "r1_exact_code_review_path": "generated/e2-r17-v3-r3-support-control-exact-code-gpt56-review-r1-20260905.json",
  "r1_exact_code_review_sha256": "48bb7a5d51c99d2ed60fb844423eaa87c455d7f56ce49a1adecaeb9f6373c3e4",
  "r3b_recovery_authorization_minted": false,
  "schema_version": "1.0",
  "science_keys_equal_parent": [
    "failed_r2_parent",
    "suite",
    "mindmemos",
    "provider_route",
    "model_identity_policy",
    "recovery_exceptions",
    "recovery_opportunity_manifest",
    "exact_once_acquisition",
    "equal_dose_support",
    "actor",
    "budget",
    "analysis_boundary",
    "stage_b_plan_no_authority",
    "runtime",
    "env_file_path",
    "run_root",
    "global_lease_path"
  ],
  "scientific_execution": false,
  "stage_b_authority": false,
  "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3B_SUPPORT_GUARD_PREFLIGHT",
  "support_inspected": false,
  "unit_tests": {
    "passed": 9,
    "suite": "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control",
    "total": 9
  }
}
```

## 7. Audit questions

A. **Direct bypass closure.** Does the guarded adjudicator now fail closed when invoked without both the support authorization and the gate-created consumption marker? Does the gate command pass both required artifacts, so the former direct-invocation bypass is closed?

B. **Review/minter provenance closure.** Do the minter, permit payload, gate, and adjudicator bind the exact minter/gate/adjudicator hashes plus a completed GPT-5.6 Sol control-review receipt whose verdict/revision/acknowledged hashes match? Can a forged or stale permit/review bypass those checks?

C. **Single use / failure behavior.** Is `O_CREAT|O_EXCL` consumption written before adjudicator invocation, and does an unexpected adjudicator error leave the permit consumed with no automatic retry?

D. **Negative tests.** Do the 9/9 tests now directly exercise the two previous blockers, including direct invocation and forged review provenance? Is there any verdict-changing untested bypass visible in the exact code?

E. **Scientific equivalence.** Given all listed science-key equalities are true and the provider recovery runner/authorizer remain bound unchanged, did R3B alter the already-passed R3 scientific geometry?

F. **Authority boundary.** Does any minter/gate/adjudicator path grant provider recovery, updater, heldout, Stage-B execution, analyzer, paper-promotion, or submission authority?

G. **Time boundary.** Confirm this review does not relax `NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`.

H. **Next consequence.** If the two blockers are closed, may the system proceed only to the *separate recovery-authorization minting step* after the hard time reset and fresh identity, while support-read permission remains impossible until terminal 158-pool recovery and Stage B remains unauthorized?

## 8. Required synthesis

Return exactly these fields before the final token:

- `contract_sha256_acknowledged`: exact R3B contract SHA
- `support_guard_preflight_sha256_acknowledged`: exact frozen support-guard preflight SHA
- `control_plane_revision`: `R3B_POST_TERMINAL_SUPPORT_GUARD`
- `minter_sha256_acknowledged`: exact minter SHA
- `gate_sha256_acknowledged`: exact gate SHA
- `support_adjudicator_sha256_acknowledged`: exact guarded adjudicator SHA
- `scientific_equivalence_to_parent_r3`: PASS/FAIL
- `direct_bypass_closed`: PASS/FAIL
- `review_provenance_closed`: PASS/FAIL
- `single_use_gate`: PASS/FAIL
- `minter_structural_only`: PASS/FAIL
- `tests_preflight`: PASS/FAIL
- `provider_recovery_authority_affected`: true/false
- `r3_contract_redesign_required`: true/false
- `new_scientific_experiment_required`: true/false
- `stage_b_authority`: false
- `scientific_authority`: false
- `support_control_verdict`: exact PASS/FAIL token above
- `execution_recommendation`: `ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION` or `DO_NOT_AUTHORIZE_R3B_RECOVERY`
- `remaining_blockers`: [] or exact blockers

Then end with exactly one provider-recovery verdict token from Section 0.
