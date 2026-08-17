from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

CANDIDATE_ID = "COMFYCLAW-BENCHMARK-CONDITIONED-EVOLVED-SKILL-UPTAKE"
SOURCE_REF = "arXiv:2607.01709"
PHENOMENON_ID = "265a7f1100492358e7de5ce6d2c7de05738cc79c1db2f4bb296d8969cc2c166c"
OFFICIAL_REPO = "https://github.com/Moms-Organic-Agent-Lab/comfyclaw"
OFFICIAL_COMMIT = "543265d0011dcd098c43039190284ffdd5507ff1"
TRACKED_MANIFEST_SHA256 = "d4dec45b83f60d230ad341d6b25acf3f0e755a2a37019560823bdd9a68f47a5e"
TRACKED_FILE_COUNT = 134
RESULTS_DOC_SHA256 = "bcc43a3df96e8e7da3a6bebf2089d0931f1ee1fd3fe9233d182dda17db2e0edc"
REPRODUCING_DOC_SHA256 = "65c75c19e8fcb866c50efcc1a8634837432a52ccc23f9fa64aa44d84e26f4ace"
DEFAULT_AUDIT_JSON = PROJECT_ROOT / "generated" / "comfyclaw-skill-uptake-support-audit-20260818.json"
DEFAULT_HOLD_JSON = PROJECT_ROOT / "generated" / "comfyclaw-skill-uptake-fresh-phenomenon-support-hold-20260818.json"

REQUIRED_UNIT = (
    "Per evaluated prompt/episode, a joinable paper-run record containing benchmark and prompt/example identity, frozen agent and "
    "image-model configuration, every read_skill event with skill identity and base-vs-evolved origin, final benchmark/verifier "
    "outcome, and workflow-edit categories; preferably paired under a matched base-only/evolved-skill availability intervention so "
    "evolved-skill uptake can be separated from benchmark task demand and predefined-library coverage."
)
REOPEN_CONDITION = (
    "The official authors release provenance-audited paper-run unit-level logs (or an equivalent first-party export) that satisfy "
    "the required join keys and outcomes, enabling a same-information test of benchmark-conditioned evolved-skill utility beyond "
    "task compositionality, predefined-skill coverage, retrieval/utilization, and task-skill compatibility. A new aggregate read-rate "
    "table or code capable of producing future logs is not sufficient."
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL).strip()


def _unit_level_candidates(files: list[str]) -> list[str]:
    out=[]
    for value in files:
        path=str(value or "").strip()
        lower=path.lower()
        data_ext=lower.endswith((".jsonl", ".csv", ".parquet", ".arrow"))
        run_dir=bool(re.search(r"(^|/)(benchmarks?|results?|runs?|traces?|trajector(?:y|ies)|paper[-_]?data)(/|$)", path, re.I))
        if data_ext or run_dir:
            out.append(path)
    return sorted(set(out))


def audit_release(release_root: Path, *, github_release_count: int = 0, github_release_asset_count: int = 0) -> dict[str, Any]:
    root=Path(release_root)
    commit=_git(root,"rev-parse","HEAD")
    files=_git(root,"ls-files").splitlines()
    manifest_sha=hashlib.sha256("\n".join(files).encode()).hexdigest()
    results=root/"docs"/"RESULTS.md";reproducing=root/"docs"/"REPRODUCING.md"
    unit_candidates=_unit_level_candidates(files)
    runtime_log_capable=bool(reproducing.is_file() and "_evolution_log" in reproducing.read_text(encoding="utf-8",errors="ignore"))
    summary_docs_present=results.is_file() and reproducing.is_file()
    exact_release=bool(
        commit==OFFICIAL_COMMIT
        and len(files)==TRACKED_FILE_COUNT
        and manifest_sha==TRACKED_MANIFEST_SHA256
        and results.is_file() and _sha(results)==RESULTS_DOC_SHA256
        and reproducing.is_file() and _sha(reproducing)==REPRODUCING_DOC_SHA256
    )
    no_released_units=bool(exact_release and not unit_candidates and int(github_release_asset_count)==0)
    status="HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT" if no_released_units else "HOLD_SUPPORT_RELEASE_SURFACE_CHANGED_REVIEW_REQUIRED"
    return {
        "schema_version":"1.0",
        "status":status,
        "candidate_id":CANDIDATE_ID,
        "source_ref":SOURCE_REF,
        "phenomenon_id":PHENOMENON_ID,
        "official_repo":OFFICIAL_REPO,
        "official_commit":commit,
        "tracked_file_count":len(files),
        "tracked_manifest_sha256":manifest_sha,
        "github_release_count":int(github_release_count),
        "github_release_asset_count":int(github_release_asset_count),
        "paper_run_unit_candidates":unit_candidates,
        "summary_docs_present":summary_docs_present,
        "runtime_log_capability_present":runtime_log_capable,
        "required_unit":REQUIRED_UNIT,
        "reopen_only_if":REOPEN_CONDITION,
        "why_hold":(
            "The primary paper reports benchmark-level evolved-skill read fractions (70.0%, 56.2%, 16.3%, 7.5%) but explicitly "
            "states that usage counts are not direct measures of skill quality. The current official release provides code, summary "
            "results, and a mechanism for future evolution logs, but no paper-run unit-level benchmark/read_skill/outcome artifacts "
            "and no GitHub Release assets. Without joinable prompt-level reads and outcomes, the strongest reductions—benchmark task "
            "demand, predefined-skill coverage, conditional artifact utility, and retrieval/utilization—cannot be exactly tested."
        ),
        "policy":{
            "support_availability_is_not_scientific_failure":True,
            "aggregate_read_rate_cannot_certify_skill_utility":True,
            "future_log_capability_is_not_released_paper_run_data":True,
            "release_change_requires_reaudit_before_clearing_hold":True,
            "automatic_problem_gate_authority":False,
            "automatic_method_authority":False,
            "automatic_experiment_authority":False,
            "automatic_p0_authority":False,
            "automatic_gpu_authority":False,
        },
        "scientific_authority":False,
    }


def validate_support_audit(audit: dict[str, Any]) -> list[str]:
    errors=[]
    if audit.get("scientific_authority") is not False:errors.append("support audit cannot carry scientific authority")
    if audit.get("candidate_id")!=CANDIDATE_ID or audit.get("source_ref")!=SOURCE_REF or audit.get("phenomenon_id")!=PHENOMENON_ID:errors.append("support audit identity mismatch")
    if audit.get("status") not in {"HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT","HOLD_SUPPORT_RELEASE_SURFACE_CHANGED_REVIEW_REQUIRED"}:errors.append("support audit status invalid")
    if not str(audit.get("required_unit") or "").strip() or not str(audit.get("reopen_only_if") or "").strip():errors.append("support audit must state required unit and reopen condition")
    if audit.get("status")=="HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT":
        if audit.get("official_commit")!=OFFICIAL_COMMIT or audit.get("tracked_manifest_sha256")!=TRACKED_MANIFEST_SHA256 or int(audit.get("tracked_file_count") or 0)!=TRACKED_FILE_COUNT:errors.append("no-unit hold must bind exact official release inventory")
        if audit.get("paper_run_unit_candidates") not in ([],None) or int(audit.get("github_release_asset_count") or 0)!=0:errors.append("no-unit hold cannot coexist with released unit candidates/assets")
        if audit.get("runtime_log_capability_present") is not True or audit.get("summary_docs_present") is not True:errors.append("no-unit hold must distinguish code/docs capability from missing paper-run units")
    return errors


def build_support_hold(*,audit:dict[str,Any],audit_file_sha256:str)->dict[str,Any]:
    errors=validate_support_audit(audit)
    if errors:raise ValueError("invalid ComfyClaw support audit: "+";".join(errors))
    if audit.get("status")!="HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT":raise ValueError("cannot build stable support hold from changed release surface")
    return {
        "schema_version":"1.0",
        "status":"HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT",
        "candidate_id":CANDIDATE_ID,
        "title":"ComfyClaw benchmark-conditioned evolved-skill uptake support hold",
        "source_ref":SOURCE_REF,
        "phenomenon_id":PHENOMENON_ID,
        "required_unit":REQUIRED_UNIT,
        "reason":str(audit.get("why_hold") or ""),
        "reopen_only_if":REOPEN_CONDITION,
        "support_audit_artifact":"generated/comfyclaw-skill-uptake-support-audit-20260818.json",
        "support_audit_sha256":audit_file_sha256,
        "scientific_authority":False,
        "authority":{"problem_gate":False,"method":False,"experiment":False,"p0":False,"gpu":False},
    }


def validate_support_hold(hold:dict[str,Any],*,audit_path:Path=DEFAULT_AUDIT_JSON)->list[str]:
    errors=[]
    if hold.get("status")!="HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT" or hold.get("scientific_authority") is not False:errors.append("support hold status/authority invalid")
    if hold.get("candidate_id")!=CANDIDATE_ID or hold.get("source_ref")!=SOURCE_REF or hold.get("phenomenon_id")!=PHENOMENON_ID:errors.append("support hold identity mismatch")
    if hold.get("required_unit")!=REQUIRED_UNIT or hold.get("reopen_only_if")!=REOPEN_CONDITION:errors.append("support hold contract drift")
    if str(hold.get("support_audit_artifact") or "")!="generated/comfyclaw-skill-uptake-support-audit-20260818.json":errors.append("support hold audit path invalid")
    if not audit_path.is_file():errors.append("support audit artifact missing")
    else:
        sha=_sha(audit_path)
        if str(hold.get("support_audit_sha256") or "")!=sha:errors.append("support hold audit digest mismatch")
    return errors


def write_support_state(*,release_root:Path,github_release_count:int=0,github_release_asset_count:int=0,audit_path:Path=DEFAULT_AUDIT_JSON,hold_path:Path=DEFAULT_HOLD_JSON)->dict[str,Any]:
    audit=audit_release(release_root,github_release_count=github_release_count,github_release_asset_count=github_release_asset_count)
    errors=validate_support_audit(audit)
    if errors:raise ValueError("invalid ComfyClaw support audit: "+";".join(errors))
    audit_path.parent.mkdir(parents=True,exist_ok=True);audit_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    hold=build_support_hold(audit=audit,audit_file_sha256=_sha(audit_path));hold_path.write_text(json.dumps(hold,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    hold_errors=validate_support_hold(hold,audit_path=audit_path)
    if hold_errors:raise ValueError("invalid ComfyClaw support hold: "+";".join(hold_errors))
    return {"audit":audit,"support_hold":hold}


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("--release-root",type=Path,required=True);ap.add_argument("--github-release-count",type=int,default=0);ap.add_argument("--github-release-asset-count",type=int,default=0);a=ap.parse_args()
    print(json.dumps(write_support_state(release_root=a.release_root,github_release_count=a.github_release_count,github_release_asset_count=a.github_release_asset_count),ensure_ascii=False,indent=2))


if __name__=="__main__":main()
