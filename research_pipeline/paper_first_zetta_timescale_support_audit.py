from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

CANDIDATE_ID = "PORT-003"
SOURCE_REFS = ("arXiv:2608.09096", "arXiv:2608.16590")
OFFICIAL_REPO = "https://github.com/air-embodied-brain/Zetta-Embodiment"
OFFICIAL_BRANCH = "main"
OFFICIAL_COMMIT = "6129934d53ea00ac306c14723874321dc3667246"
TRACKED_FILE_COUNT = 250
TRACKED_MANIFEST_SHA256 = "63b642811e9068d5cc6fd16df0956b138bdb0a988fd0fe02862da152aa95cd0a"
EVIDENCE_FILE_SHA256 = {
    "rpent/evolution/models.py": "4aaac5fcb0a242d21739e1020c9fa217b1e1730eb0896a5d37a40f9571e48a75",
    "rpent/evolution/stages.py": "4abf26114ebe81c760b9b1e0c6994c00348a7860442b6af0520304fe9e6126fb",
    "robots/libero/run_evolution_rollout.py": "56ee2b1836a8c3e6ba5b0452b13c8e510d71a97c239abc80a9f20b36b39a4cd5",
}
DEFAULT_AUDIT_JSON = PROJECT_ROOT / "generated" / "zetta-timescale-support-audit-20260819.json"

REQUIRED_UNIT = (
    "A frozen Zetta policy/skill state supporting independent A/B/C/D timescale interventions "
    "(post-hoc only; episode/retrieval only; skill-level closed loop only; full Zetta) plus a "
    "matched-frequency hierarchical baseline, all on the same tasks/seeds with fixed base policy, "
    "skill state, and compute."
)
REOPEN_CONDITION = (
    "Reopen only if a first-party revision changes the released CandidateBundle/atomic-inheritance "
    "contract or runtime so that the required intermediate one-factor timescale arms are native and "
    "contract-valid on the same frozen bundle. Validator weakening, wrapper-based masking, synthetic "
    "mechanism injection, retraining, hidden-outcome tuning, or changing the base policy/skill state "
    "does not clear this hold."
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL
    ).strip()


def _normalize_repo_url(value: str) -> str:
    normalized = str(value or "").strip().rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized.lower()


def _origin_main_head(repo: Path) -> str:
    output = _git(repo, "ls-remote", "origin", f"refs/heads/{OFFICIAL_BRANCH}")
    head = output.split()[0] if output else ""
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("could not resolve official origin main HEAD")
    return head


def _tracked_manifest(repo: Path) -> tuple[int, str]:
    files = _git(repo, "ls-files").splitlines()
    return len(files), hashlib.sha256("\n".join(files).encode()).hexdigest()


def _contract_markers(repo: Path) -> dict[str, bool]:
    models = (repo / "rpent/evolution/models.py").read_text(encoding="utf-8")
    stages = (repo / "rpent/evolution/stages.py").read_text(encoding="utf-8")
    runtime = (repo / "robots/libero/run_evolution_rollout.py").read_text(encoding="utf-8")
    return {
        "recovery_only_rejected_unknown_critic": (
            "recovery rules reference unknown critic rules" in models
        ),
        "critic_only_rejected_uncovered_rule": (
            "every critic rejection must have a frozen executable recovery" in models
        ),
        "atomic_delta_requires_one_critic_and_one_recovery": (
            "one candidate must append exactly one critic and one linked recovery" in stages
        ),
        "runtime_modes_only_strict_or_active": (
            'choices=("strict_pure_vla", "active_bundle")' in runtime
        ),
        "active_bundle_loaded_and_sha_checked": (
            "bundle = CandidateBundle.from_dict(read_json(args.bundle))" in runtime
            and "candidate bundle SHA does not match --bundle-sha256" in runtime
        ),
    }


def audit_release(release_root: Path, *, origin_main_head: str | None = None) -> dict[str, Any]:
    root = Path(release_root)
    commit = _git(root, "rev-parse", "HEAD")
    origin_url = _git(root, "remote", "get-url", "origin")
    origin_matches_official = _normalize_repo_url(origin_url) == _normalize_repo_url(OFFICIAL_REPO)
    worktree_clean = not bool(_git(root, "status", "--porcelain"))
    remote_head = str(origin_main_head or _origin_main_head(root)).strip().lower()
    tracked_file_count, tracked_manifest_sha256 = _tracked_manifest(root)
    evidence_files = [
        {
            "path": path,
            "sha256": _sha(root / path),
            "expected_sha256": expected,
            "matches_expected": _sha(root / path) == expected,
        }
        for path, expected in EVIDENCE_FILE_SHA256.items()
    ]
    markers = _contract_markers(root)
    exact_revision = (
        commit == OFFICIAL_COMMIT
        and remote_head == OFFICIAL_COMMIT
        and origin_matches_official
        and worktree_clean
        and tracked_file_count == TRACKED_FILE_COUNT
        and tracked_manifest_sha256 == TRACKED_MANIFEST_SHA256
        and all(row["matches_expected"] for row in evidence_files)
    )
    blocker_verified = exact_revision and all(markers.values())
    status = (
        "HOLD_SUPPORT_RELEASED_SCHEMA_BLOCKS_REQUIRED_UNIT"
        if blocker_verified
        else "HOLD_SUPPORT_RELEASE_SURFACE_CHANGED_REVIEW_REQUIRED"
    )
    return {
        "schema_version": "1.0",
        "status": status,
        "candidate_id": CANDIDATE_ID,
        "source_refs": list(SOURCE_REFS),
        "official_repo": OFFICIAL_REPO,
        "official_branch": OFFICIAL_BRANCH,
        "official_commit": commit,
        "origin_url": origin_url,
        "origin_matches_official": origin_matches_official,
        "worktree_clean": worktree_clean,
        "origin_main_head": remote_head,
        "head_matches_canonical_inventory": remote_head == OFFICIAL_COMMIT,
        "tracked_file_count": tracked_file_count,
        "tracked_manifest_sha256": tracked_manifest_sha256,
        "evidence_files": evidence_files,
        "schema_level_blocker": {
            "kind": "RELEASED_SUBSTRATE_SCHEMA_CONTRACT",
            "markers": markers,
            "candidate_bundle_contract": (
                "Recovery rules must reference present Critic rules, every Critic rejection must have "
                "a frozen executable Recovery path, and each candidate delta must append exactly one "
                "Critic plus one linked Recovery."
            ),
            "runtime_contract": (
                "The released LIBERO rollout exposes strict_pure_vla or active_bundle and loads the "
                "active CandidateBundle intact with SHA verification."
            ),
            "required_intermediate_arms_contract_valid": False,
            "implication": (
                "The released substrate does not expose native independent intermediate one-factor "
                "arms needed to identify the frozen PORT-003 timescale contrast. The native outer "
                "comparison is pure VLA versus the intact active bundle; using a mask/wrapper or "
                "weakening validation would change the realization substrate."
            ),
        },
        "required_unit": REQUIRED_UNIT,
        "why_hold": (
            "PORT-003 needs independent intermediate timescale interventions on the same frozen state. "
            "At the canonical Zetta main revision, the schema and atomic-inheritance validators couple "
            "Critic and Recovery into an indivisible contract-valid candidate delta, while the runtime "
            "accepts only the intact active bundle or strict pure-VLA mode. Therefore the required "
            "one-factor intermediate arms cannot be materialized without changing the released substrate."
        ),
        "reopen_only_if": REOPEN_CONDITION,
        "policy": {
            "support_availability_is_not_scientific_failure": True,
            "schema_contract_blocker_is_realization_support_not_principle_dead_end": True,
            "wrapper_or_validator_modification_cannot_clear_same_substrate_hold": True,
            "release_change_requires_reaudit_before_clearing_hold": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
        },
        "authority": {
            "problem_gate": False,
            "paper_design": False,
            "method": False,
            "experiment": False,
            "p0": False,
            "gpu": False,
        },
        "scientific_authority": False,
    }


def validate_support_audit(audit: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if audit.get("candidate_id") != CANDIDATE_ID or tuple(audit.get("source_refs") or ()) != SOURCE_REFS:
        errors.append("support audit identity mismatch")
    if audit.get("scientific_authority") is not False:
        errors.append("support audit cannot carry scientific authority")
    if any(value is not False for value in (audit.get("authority") or {}).values()):
        errors.append("support audit downstream authority must remain false")
    if not str(audit.get("required_unit") or "").strip() or not str(audit.get("reopen_only_if") or "").strip():
        errors.append("support audit must state required unit and reopen condition")
    if audit.get("status") == "HOLD_SUPPORT_RELEASED_SCHEMA_BLOCKS_REQUIRED_UNIT":
        if audit.get("official_commit") != OFFICIAL_COMMIT or audit.get("origin_main_head") != OFFICIAL_COMMIT:
            errors.append("stable schema hold must bind exact official main revision")
        if audit.get("origin_matches_official") is not True:
            errors.append("stable schema hold must bind the official repository origin")
        if audit.get("worktree_clean") is not True:
            errors.append("stable schema hold requires a clean audited checkout")
        if audit.get("tracked_file_count") != TRACKED_FILE_COUNT or audit.get("tracked_manifest_sha256") != TRACKED_MANIFEST_SHA256:
            errors.append("stable schema hold must bind exact tracked release inventory")
        observed = {row.get("path"): row for row in audit.get("evidence_files") or [] if isinstance(row, dict)}
        for path, expected in EVIDENCE_FILE_SHA256.items():
            row = observed.get(path) or {}
            if row.get("sha256") != expected or row.get("matches_expected") is not True:
                errors.append(f"evidence file digest mismatch: {path}")
        blocker = audit.get("schema_level_blocker") or {}
        if blocker.get("kind") != "RELEASED_SUBSTRATE_SCHEMA_CONTRACT":
            errors.append("schema blocker kind mismatch")
        if blocker.get("required_intermediate_arms_contract_valid") is not False:
            errors.append("stable schema hold cannot claim required intermediate arms are valid")
        if not all((blocker.get("markers") or {}).values()):
            errors.append("stable schema hold requires all contract markers")
    elif audit.get("status") != "HOLD_SUPPORT_RELEASE_SURFACE_CHANGED_REVIEW_REQUIRED":
        errors.append("support audit status invalid")
    return errors


def write_support_audit(*, release_root: Path, output_path: Path = DEFAULT_AUDIT_JSON, origin_main_head: str | None = None) -> dict[str, Any]:
    audit = audit_release(release_root, origin_main_head=origin_main_head)
    errors = validate_support_audit(audit)
    if errors:
        raise ValueError("invalid Zetta support audit: " + "; ".join(errors))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_AUDIT_JSON)
    parser.add_argument("--origin-main-head")
    args = parser.parse_args()
    audit = write_support_audit(
        release_root=args.release_root,
        output_path=args.out,
        origin_main_head=args.origin_main_head,
    )
    print(json.dumps({"status": audit["status"], "candidate_id": audit["candidate_id"], "scientific_authority": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
