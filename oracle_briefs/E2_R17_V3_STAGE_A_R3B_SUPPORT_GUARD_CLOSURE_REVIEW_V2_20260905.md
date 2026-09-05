# E2-R17 V3 Stage-A R3B — exact blocker-closure review v2

Date: 2026-09-05
Scope: fresh independent ZERO-PROVIDER exact-code review of exactly the two prior R1 blockers.

Prior R1 PASSed structural-only minter, terminal binding, narrow support authority, preserved adjudicator/science, and required NO R3 scientific redesign. It failed only:
1. direct support-adjudicator invocation remained an authority bypass;
2. gate/review/minter provenance was not end-to-end bound and bypass tests were missing.

Do not reopen matched-censor geometry, no-replay/replacement, 158 provider tasks + one matched no-provider censor + one terminal technical missing, K=8, 7/7/8 opportunity geometry, >=4 mixed-pool threshold, or Stage-B design unless exact R3B code below changed those objects. Do not infer support/outcomes.

Hard time gate: `NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`. PASS here cannot relax it and cannot itself authorize provider recovery, support read, or Stage B.

Final provider-recovery verdict: exactly one of `PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION`, `REVISE_R3B_BEFORE_PROVIDER_RECOVERY`, `STOP_R3_RECOVERY`. Also return `support_control_verdict` exactly `PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE` or `FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`.

## Frozen hashes / equality
```json
{
  "parent_r3_contract_sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "r3b_contract_sha256": "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9",
  "frozen_support_guard_preflight_sha256": "94043973e6b89edf0e0132e8c503854063ab3ea32801ccc2766359554264084f",
  "prior_r1_review_sha256": "48bb7a5d51c99d2ed60fb844423eaa87c455d7f56ce49a1adecaeb9f6373c3e4",
  "prior_r1_verdict": "REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE",
  "prior_blockers": [
    "Make the support adjudicator enforceably reachable only through the support-read-authorized one-shot gate; direct invocation must not remain an authority bypass.",
    "Make the gate verify provenance/binding to the exact reviewed minter and control-review receipt, and add zero-provider regression tests for direct-invocation and forged-permit bypasses."
  ],
  "control_plane_revision": "R3B_POST_TERMINAL_SUPPORT_GUARD",
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
  "bound_code": {
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
  }
}
```

## A. Guarded adjudicator — direct bypass closure
### `scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py` exact lines 57-126
Whole-file SHA256: `d8ad232562b5f88f7394555c158d83b7e00dd235f2ef8631c89a3cabe6b896eb`
```python
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

```

## B. Minter review-binding + narrow permit
### `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py` exact lines 57-69
Whole-file SHA256: `0e7bf96b3e6274de8c6e5738b46924990de8b8897c04bb3871fce0e5fdd06d43`
```python
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
### `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py` exact lines 196-292
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
```

## C. One-shot gate provenance validation
### `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py` exact lines 35-125
Whole-file SHA256: `333c3ef89746c4d7e44b20769e068b0520140dffb4fa79f32da1f9e981cefb10`
```python


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
```

## D. One-shot consumption-before-invoke + fail-closed behavior
### `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py` exact lines 132-205
Whole-file SHA256: `333c3ef89746c4d7e44b20769e068b0520140dffb4fa79f32da1f9e981cefb10`
```python
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
```

## E. Exact blocker-focused regression tests
### `research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py` exact lines 241-367
Whole-file SHA256: `7a9c51fc7a24df34469efa71a6e2301e6aeab182d110e23cd460a646ecc002db`
```python
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
```

## F. Frozen zero-provider preflight
Frozen preflight whole-file SHA256: `94043973e6b89edf0e0132e8c503854063ab3ea32801ccc2766359554264084f`
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
Fresh rerun on 2026-09-05: the same unit-test suite passed 9/9; preflight checks remained all true, with only regenerated timestamp differing in the temporary rerun.

## G. Required audit
A. Is direct adjudicator bypass now closed because CLI requires `--support-authorization` and `--consumption-marker`, and `validate_support_read_gate` validates both plus exact bound hashes/review receipt?
B. Is exact review/minter/gate/adjudicator provenance end-to-end bound strongly enough to reject forged/stale permits?
C. Is single-use consumption created with `O_CREAT|O_EXCL` before invocation and left consumed on unexpected adjudicator failure, forbidding automatic retry?
D. Do tests directly cover direct invocation, forged review provenance, invalid permit, one-shot consumption, and no Stage-B authority? Any verdict-changing bypass remains?
E. Do parent-equality + unchanged bound recovery runner/authorizer show no R3 scientific-geometry change?
F. Does any path grant provider/updater/heldout/Stage-B/analyzer/paper authority?
G. Confirm hard Sep-7 time gate remains.
H. If PASS, is the only next consequence: after reset and fresh identity, allow a separate recovery-authorization minting step; support-read remains impossible until terminal 158-pool state and Stage B remains false?

## H. Required synthesis
Return exactly:
- `contract_sha256_acknowledged`
- `support_guard_preflight_sha256_acknowledged`
- `control_plane_revision`
- `minter_sha256_acknowledged`
- `gate_sha256_acknowledged`
- `support_adjudicator_sha256_acknowledged`
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
- `support_control_verdict`
- `execution_recommendation`: `ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION` or `DO_NOT_AUTHORIZE_R3B_RECOVERY`
- `remaining_blockers`: [] or exact blockers
Then exactly one final provider-recovery verdict token.
