"""Deterministic R2 first-action and R3 trajectory observables."""
from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import canonical_json, sha256_text

PATH_RE = re.compile(r"(?<![A-Za-z0-9_.-])((?:\./|/)?[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+|[A-Za-z0-9_.-]+\.py)(?=$|[\s:'\"])")
PY_TARGET_RE = re.compile(r"([A-Za-z0-9_./-]+\.py)(?:::{1,2}([A-Za-z0-9_.]+))?")


def action_class(action: str) -> str:
    normalized = action.strip()
    first = normalized.splitlines()[0].strip() if normalized else ""
    if any(marker in normalized for marker in (
        "MINI_SWE_AGENT_FINAL_OUTPUT", "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT")):
        return "SUBMIT"
    if re.match(r"^(ls|find|tree|pwd)(\s|$)", first):
        return "LIST"
    if re.match(r"^(rg|grep|git\s+grep)(\s|$)", first):
        return "SEARCH"
    if re.match(r"^(cat|sed\s+-n|head|tail|less|git\s+(diff|status|show))(\s|$)", first):
        return "READ"
    if re.match(r"^(pytest|tox|nox|make\s+test|python(?:\d+(?:\.\d+)?)?\s+-m\s+(pytest|unittest))(\s|$)", first):
        return "TEST"
    if (
        "apply_patch" in first
        or re.match(r"^(sed\s+-i|perl\s+-pi|tee|touch|rm|mv|cp)(\s|$)", first)
        or ("python" in first and any(token in normalized for token in (
            "write_text(", "open(", "Path(")))
    ):
        return "EDIT"
    return "OTHER"


def first_action_signature(actions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not actions:
        base = {
            "parse_valid": False, "action_class": "OTHER",
            "first_referenced_path": None, "first_referenced_python_symbol_or_module": None,
            "action_sha256": sha256_text(""),
        }
    else:
        row = actions[0]
        valid = row.get("type") == "shell" and bool(str(row.get("action") or "").strip())
        action = str(row.get("action") or "") if valid else ""
        paths = PATH_RE.findall(action)
        py = PY_TARGET_RE.search(action)
        python_target = None
        if py:
            python_target = py.group(2) or py.group(1)
        base = {
            "parse_valid": valid,
            "action_class": action_class(action) if valid else "OTHER",
            "first_referenced_path": paths[0] if paths else None,
            "first_referenced_python_symbol_or_module": python_target,
            "action_sha256": sha256_text(action),
        }
    base["signature_sha256"] = sha256_text(canonical_json(base))
    return base


def trajectory_observables(*, actions: Sequence[Mapping[str, Any]], patch: str,
                           modified_files: Sequence[str], edit_target: Mapping[str, Any],
                           model_call_count: int, exit_status: str) -> dict[str, Any]:
    shell = [row for row in actions if row.get("type") == "shell"]
    tests = [row for row in shell if action_class(str(row.get("action") or "")) == "TEST"]
    hunk_count = sum(1 for line in patch.splitlines() if line.startswith("@@ "))
    return {
        "first_action": first_action_signature(actions),
        "modified_file_set": sorted(set(modified_files)),
        "final_patch_sha256": sha256_text(patch),
        "edit_target_set": dict(edit_target),
        "modified_file_count": len(set(modified_files)),
        "diff_hunk_count": hunk_count,
        "model_call_count": model_call_count,
        "shell_action_count": len(shell),
        "tests_run_indicator": bool(tests),
        "tests_run_count": len(tests),
        "trajectory_length": len(actions),
        "submission_state": exit_status,
    }
