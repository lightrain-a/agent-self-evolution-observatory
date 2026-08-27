from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.config import PROJECT_ROOT

CANDIDATE_ID = "PORT-010"
SOURCE_REPO = "https://github.com/usail-hkust/VibeWorlding-Gym"
SOURCE_REMOTE = "git@github.com:usail-hkust/VibeWorlding-Gym.git"
PREANALYSIS = PROJECT_ROOT / "generated" / "port010-vwe-firstparty-preanalysis-proposal.json"
PLAN = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "generated" / "port010-vwe-source-release-audit-20260827.json"
ADMIN_PATH_NAMES = {"license", "licence", "license.md", "licence.md", "notice", "notice.md", "citation.cff", "code_of_conduct.md", "contributing.md"}
OUTCOME_MARKERS = ("trajectory", "final_map", "reward", "result", "outcome", "rollout", "verified", "prediction", "eval_log", "evaluation_log")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=120)
    if check and result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()[:500]}")
    return result.stdout


def admin_path(path: str) -> bool:
    return Path(path).name.lower() in ADMIN_PATH_NAMES


def outcome_like(path: str) -> bool:
    low = path.lower()
    return any(marker in low for marker in OUTCOME_MARKERS)


def readme_change_is_citation_admin_only(root: Path, baseline: str, head: str) -> bool:
    changed = run_git(root, "diff", "--name-only", baseline, head, "--", "README.md").strip()
    if not changed:
        return True
    current = run_git(root, "show", f"{head}:README.md")
    lines = current.splitlines()
    citation_line = next((i + 1 for i, line in enumerate(lines) if line.strip().lower().startswith("## 8. citation")), None)
    if citation_line is None:
        return False
    patch = run_git(root, "diff", "--unified=0", baseline, head, "--", "README.md")
    new_starts = []
    for line in patch.splitlines():
        match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if match:
            new_starts.append(int(match.group(1)))
    additions = "\n".join(line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++"))
    return bool(new_starts) and min(new_starts) >= citation_line and not any(marker in additions.lower() for marker in OUTCOME_MARKERS)


def fetch_objects(root: Path, baseline: str) -> str:
    run_git(root, "init", "-q")
    run_git(root, "remote", "add", "origin", SOURCE_REMOTE)
    run_git(root, "fetch", "-q", "--depth=16", "--no-tags", "origin", "main")
    head = run_git(root, "rev-parse", "refs/remotes/origin/main").strip().lower()
    if subprocess.run(["git", "-C", str(root), "cat-file", "-e", baseline + "^{commit}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        run_git(root, "fetch", "-q", "--no-tags", "origin", baseline)
    if subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", baseline, head]).returncode:
        raise RuntimeError("frozen VibeWorlding-Gym baseline is not an ancestor of observed main")
    return head


def build_audit() -> dict[str, Any]:
    preanalysis = json.loads(PREANALYSIS.read_text(encoding="utf-8"))
    baseline = str((preanalysis.get("first_party_provenance") or {}).get("source_revision") or "").lower()
    source_url = str((preanalysis.get("first_party_provenance") or {}).get("source_url") or "")
    if source_url.rstrip("/") != SOURCE_REPO or not re.fullmatch(r"[0-9a-f]{40}", baseline):
        raise RuntimeError("unexpected frozen VibeWorlding-Gym source provenance")
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    row = next(item for item in plan.get("entries") or [] if item.get("candidate_id") == CANDIDATE_ID)
    if row.get("status") != "HOLD_EVIDENCE_REVIEW_BLOCKED" or (row.get("evidence_review") or {}).get("verdict") != "BLOCK_BAKE_IN":
        raise RuntimeError("PORT-010 is not in the expected effective HOLD")
    required = list((row.get("release_change_adjudication") or {}).get("required_reopen_components") or [])
    remaining = list((row.get("release_change_adjudication") or {}).get("remaining_reopen_components") or [])
    if sorted(required) != ["per_case_outcomes", "query_units"] or remaining != ["per_case_outcomes"]:
        raise RuntimeError("PORT-010 frozen reopen-component contract drifted")

    with tempfile.TemporaryDirectory(prefix="port010-vwe-git-") as td:
        root = Path(td)
        head = fetch_objects(root, baseline)
        commit_shas = [line.strip() for line in run_git(root, "rev-list", "--reverse", f"{baseline}..{head}").splitlines() if line.strip()]
        commits = []
        for sha in commit_shas:
            fields = run_git(root, "show", "-s", "--format=%H%x1f%aI%x1f%s", sha).strip().split("\x1f")
            commits.append({"sha": fields[0].lower(), "authored_at": fields[1], "message": fields[2][:300]})
        status_rows = {}
        for line in run_git(root, "diff", "--name-status", baseline, head).splitlines():
            if not line.strip():
                continue
            status, path = line.split("\t", 1)
            status_rows[path] = status
        numstat = {}
        for line in run_git(root, "diff", "--numstat", baseline, head).splitlines():
            if not line.strip():
                continue
            additions, deletions, path = line.split("\t", 2)
            numstat[path] = (None if additions == "-" else int(additions), None if deletions == "-" else int(deletions))
        files = []
        for path in sorted(status_rows):
            additions, deletions = numstat.get(path, (None, None))
            blob = run_git(root, "rev-parse", f"{head}:{path}", check=False).strip().lower() if not status_rows[path].startswith("D") else ""
            files.append({"path": path, "status": status_rows[path], "additions": additions, "deletions": deletions, "blob_sha": blob})
        outcome_paths = sorted(item["path"] for item in files if outcome_like(item["path"]))
        citation_admin = readme_change_is_citation_admin_only(root, baseline, head)
        admin_only = bool(files) and all(admin_path(item["path"]) or item["path"] == "README.md" for item in files) and citation_admin and not outcome_paths

    if head == baseline:
        disposition = "NO_RELEASE_CHANGE"
    elif admin_only:
        disposition = "RECHECKED_RELEASE_IRRELEVANT"
    else:
        disposition = "RECHECK_REQUIRED_CONTENT_AUDIT"
    material = {
        "candidate_id": CANDIDATE_ID,
        "source_repo": SOURCE_REPO,
        "baseline_revision": baseline,
        "observed_revision": head,
        "ahead_by": len(commits),
        "commits": commits,
        "changed_files": files,
        "outcome_artifact_candidate_paths": outcome_paths,
        "readme_change_citation_admin_only": citation_admin,
        "admin_only_change": admin_only,
        "disposition": disposition,
        "required_reopen_components": required,
        "materialized_reopen_components_from_this_change": [],
        "remaining_reopen_components": remaining,
        "qualifying_author_outcome_artifact": False,
        "support_qualified": False,
        "generator_reopen_authorized": False,
        "problem_gate_authorized": False,
        "method_authorized": False,
        "experiment_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "scientific_authority": False,
    }
    return {"schema_version": "port010-source-release-audit-v1", "generated_at": now(), **material, "audit_sha256": sha256_json(material)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = build_audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: audit[key] for key in ("baseline_revision", "observed_revision", "ahead_by", "disposition", "readme_change_citation_admin_only", "outcome_artifact_candidate_paths", "audit_sha256")}, indent=2))


if __name__ == "__main__":
    main()
