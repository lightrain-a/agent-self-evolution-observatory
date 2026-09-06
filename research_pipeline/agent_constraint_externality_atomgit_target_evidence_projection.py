from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from research_pipeline import agent_constraint_externality_atomgit_repeat_dev_reserve_source_common as c
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
SOURCE_CLOSEOUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-source-closeout-20260906.json"
OUTPUT = GENERATED / "agent-constraint-externality-atomgit-target-evidence-projection-v1-20260906.json"
READINESS = GENERATED / "agent-constraint-externality-atomgit-repair-generation-readiness-20260906.json"
RUN_ROOT = Path("/data/wyt/agent-constraint-externality/runs/atomgit-repeat-dev-reserve-source-20260906-v1")

SECRET_KEYS = {"access_token", "file_system_access_token", "password", "authorization", "token_type"}
AUTH_SUFFIXES = ("__login", "__show_account_passwords")
FORBIDDEN_MARKERS = (
    "ace-dev-dummy", "spare-", "coupling_level", "topology_label", "non_target_outcomes",
    "independent", "shared_resource_exposure_count",
)
AUTH_ERROR_MARKERS = ("not authorized", "invalid credentials", "access token is missing", "status code is 401")
JWT_RE = re.compile(r"eyJ[A-Za-z0-9_\-\.]{20,}")


class ProjectionError(RuntimeError):
    pass


def readj(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, status: str) -> dict[str, Any]:
    payload = readj(path)
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != status:
        raise ProjectionError(f"identity/status mismatch: {path}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload); unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise ProjectionError(f"content hash mismatch: {path}")
    return payload


def _walk_strings(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for child in value.values():
            out.extend(_walk_strings(child))
    elif isinstance(value, list):
        for child in value:
            out.extend(_walk_strings(child))
    return out


def target_markers(case: dict[str, Any]) -> list[str]:
    values = [
        *case.get("target_local_resources", []),
        *_walk_strings(case.get("public_route", {})),
        *_walk_strings(case.get("expected", {})),
    ]
    markers: set[str] = set()
    for value in values:
        text = str(value)
        for match in re.findall(r"(?:dsfqa0[-A-Za-z0-9_./~]+|DFA0FG[0-9]+R[0-9]+|direct-a0-qualified-blob-[A-Za-z0-9_-]+)", text):
            markers.add(match.rstrip("*,:;"))
    # The family namespace is the strongest relevance witness and covers files
    # such as adjust/modifier inputs that have generic basenames.
    for value in values:
        if "~/agent_externality/" in str(value):
            prefix = str(value).split("*", 1)[0].rstrip("/,:;")
            if len(prefix) >= 20:
                markers.add(prefix)
    if not markers:
        raise ProjectionError(f"no target-local markers for {case.get('case_id')}")
    return sorted(markers, key=lambda item: (-len(item), item))


def _contains_marker(value: Any, markers: list[str]) -> bool:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True).lower()
    return any(marker.lower() in text for marker in markers)


def _contains_forbidden(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True).lower()
    return any(marker.lower() in text for marker in FORBIDDEN_MARKERS)


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize(child) for key, child in value.items() if str(key).lower() not in SECRET_KEYS}
    if isinstance(value, list):
        return [sanitize(child) for child in value]
    if isinstance(value, str):
        return JWT_RE.sub("<REDACTED_AUTH_TOKEN>", value)
    return value


def prune_result(value: Any, markers: list[str]) -> Any:
    value = sanitize(value)
    if isinstance(value, list):
        if not value:
            return []
        kept = [prune_result(item, markers) for item in value if _contains_marker(item, markers)]
        return kept
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, child in value.items():
            if isinstance(child, list):
                out[key] = prune_result(child, markers)
            elif isinstance(child, dict):
                nested = prune_result(child, markers)
                if nested or _contains_marker(child, markers):
                    out[key] = nested
            else:
                out[key] = child
        return out
    return value


def paired_events(path: Path) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    dispatch = {row["tool_id"]: row for row in rows if row.get("event") == "TOOL_DISPATCH"}
    completion = {row["tool_id"]: row for row in rows if row.get("event") == "TOOL_COMPLETION"}
    if len(dispatch) != len(completion) or set(dispatch) != set(completion):
        raise ProjectionError(f"trajectory dispatch/completion mismatch: {path}")
    pairs = [(dispatch[tool_id], completion[tool_id]) for tool_id in dispatch]
    pairs.sort(key=lambda pair: int(pair[0].get("index", 0)))
    return pairs


def project_trajectory(path: Path, case: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    markers = target_markers(case)
    projected: list[dict[str, Any]] = []
    counts = {"raw_tool_calls": 0, "auth_transport_dropped": 0, "dummy_or_non_target_dropped": 0, "irrelevant_dropped": 0, "kept": 0}
    allowed_prefixes = tuple(app + "__" for app in case["fixture"]["apps"])
    for dispatch, completion in paired_events(path):
        counts["raw_tool_calls"] += 1
        tool_name = str(dispatch.get("tool_name", ""))
        combined = {"dispatch": dispatch, "completion": completion}
        combined_text = json.dumps(combined, ensure_ascii=False).lower()
        if tool_name.startswith("supervisor__") or tool_name.endswith(AUTH_SUFFIXES):
            counts["auth_transport_dropped"] += 1
            continue
        if any(marker in combined_text for marker in AUTH_ERROR_MARKERS):
            counts["auth_transport_dropped"] += 1
            continue
        if not tool_name.startswith(allowed_prefixes):
            counts["irrelevant_dropped"] += 1
            continue
        if _contains_forbidden(combined):
            counts["dummy_or_non_target_dropped"] += 1
            continue
        args = sanitize(dispatch.get("arguments") or {})
        raw_result = completion.get("result")
        result_value: Any = raw_result
        if isinstance(raw_result, str):
            try:
                result_value = json.loads(raw_result)
            except json.JSONDecodeError:
                result_value = sanitize(raw_result)
        relevant = _contains_marker(args, markers) or _contains_marker(result_value, markers)
        if not relevant:
            counts["irrelevant_dropped"] += 1
            continue
        result = prune_result(result_value, markers)
        step = {
            "source_tool_id": dispatch["tool_id"],
            "tool_name": tool_name,
            "arguments": args,
            "result": result,
        }
        if _contains_forbidden(step):
            raise ProjectionError(f"forbidden marker survived projection: {case['case_id']}:{dispatch['tool_id']}")
        projected.append(step)
        counts["kept"] += 1
    if not projected:
        raise ProjectionError(f"empty target evidence projection: {case['case_id']}")
    return projected, counts


def _gmail_failure_slice(case: dict[str, Any], measurement_root: Path) -> dict[str, Any]:
    expected = case["expected"]
    prefix = str(expected["subject"]).split("-POL", 1)[0]
    db = measurement_root / "gmail.db"
    if not db.is_file():
        raise ProjectionError(f"gmail measurement DB missing: {db}")
    con = sqlite3.connect(db)
    try:
        rows = con.execute(
            "SELECT id, recipient_ids, subject, body FROM emails WHERE sender_id=99 AND subject LIKE ? ORDER BY id",
            (prefix + "%",),
        ).fetchall()
        observed = []
        for email_id, recipient_ids_raw, subject, body in rows:
            try:
                recipient_ids = json.loads(recipient_ids_raw)
            except Exception:
                recipient_ids = []
            recipient_emails = []
            for rid in recipient_ids:
                row = con.execute("SELECT email FROM users WHERE id=?", (rid,)).fetchone()
                if row:
                    recipient_emails.append(str(row[0]))
            attachments = [
                {"file_name": str(name), "file_content": str(content)}
                for name, content in con.execute(
                    "SELECT file_name, file_content FROM attachments WHERE email_id=? ORDER BY file_name", (email_id,)
                ).fetchall()
            ]
            observed.append({"recipient_emails": recipient_emails, "subject": str(subject), "body": str(body), "attachments": attachments})
    finally:
        con.close()
    return {"target_success": False, "expected": expected, "observed_target_local_email_candidates": observed}


def _tnf_failure_slice(case: dict[str, Any], measurement_root: Path) -> dict[str, Any]:
    expected = case["expected"]
    expected_path = str(expected["output_path"])
    directory = expected_path.rsplit("/", 1)[0] + "/"
    basename = expected_path.rsplit("/", 1)[1]
    match = re.match(r"(dsfqa0-output-[0-9]+-r[0-9]+-)", basename)
    if match is None:
        raise ProjectionError(f"cannot derive TNF output prefix: {expected_path}")
    output_prefix = directory + match.group(1)
    db = measurement_root / "file_system.db"
    if not db.is_file():
        raise ProjectionError(f"file measurement DB missing: {db}")
    con = sqlite3.connect(db)
    try:
        rows = con.execute(
            "SELECT tilde_path, content FROM files WHERE user_id=99 AND tilde_path LIKE ? ORDER BY tilde_path",
            (output_prefix + "%",),
        ).fetchall()
    finally:
        con.close()
    observed = [{"tilde_path": str(path), "content": str(content)} for path, content in rows if "spare-" not in str(path).lower()]
    return {"target_success": False, "expected": expected, "observed_target_local_output_candidates": observed}


def target_failure_slice(case: dict[str, Any], measurement_root: Path) -> dict[str, Any]:
    return _gmail_failure_slice(case, measurement_root) if str(case.get("kind", "")).startswith("FG_") else _tnf_failure_slice(case, measurement_root)


def build() -> dict[str, Any]:
    closeout = verified(SOURCE_CLOSEOUT, "ATOMGIT_REPEAT_DEV_RESERVE_SOURCE_PANEL_PASS_TARGET_EVIDENCE_PROJECTION_REQUIRED")
    family_index = c.family_index()
    selected = closeout["source_outcomes"]["selected_family_ids"]
    selected_ids = list(selected["FG"]) + list(selected["TNF"])
    if len(selected_ids) != 6 or len(set(selected_ids)) != 6:
        raise ProjectionError("selected development family geometry drift")
    completion = {
        row["family_id"]: row
        for row in c.live.ledger_rows(c.LEDGER)
        if row.get("event") == "COMPLETION"
    }
    families: dict[str, Any] = {}
    totals = {"raw_tool_calls": 0, "auth_transport_dropped": 0, "dummy_or_non_target_dropped": 0, "irrelevant_dropped": 0, "kept": 0}
    for family_id in selected_ids:
        if family_id not in family_index or family_id not in completion:
            raise ProjectionError(f"selected family missing source evidence: {family_id}")
        row = completion[family_id]
        if row.get("usable_semantic_failure") is not True or row.get("target_success") is not False:
            raise ProjectionError(f"selected family is not a semantic target failure: {family_id}")
        family = family_index[family_id]
        case = family["source_case"]
        unit_root = RUN_ROOT / family_id.lower()
        trajectory = unit_root / "trajectory.jsonl"
        if not trajectory.is_file() or sha256_file(trajectory) != row["trajectory_sha256"]:
            raise ProjectionError(f"source trajectory hash drift: {family_id}")
        trace, audit = project_trajectory(trajectory, case)
        for key in totals:
            totals[key] += int(audit[key])
        failure = target_failure_slice(case, unit_root / "measurement-full-dbs")
        family_payload = {
            "family_id": family_id,
            "source_case_id": case["case_id"],
            "source_trajectory_sha256": row["trajectory_sha256"],
            "source_completion_sha256": sha256_value(row),
            "target_instruction": case["task_instruction"],
            "target_instruction_sha256": sha256_value(case["task_instruction"]),
            "target_failure_slice": failure,
            "target_failure_slice_sha256": sha256_value(failure),
            "projected_tool_trajectory": trace,
            "projected_tool_trajectory_sha256": sha256_value(trace),
            "projection_counts": audit,
        }
        text = json.dumps(family_payload, ensure_ascii=False, sort_keys=True).lower()
        if any(marker.lower() in text for marker in FORBIDDEN_MARKERS):
            raise ProjectionError(f"forbidden evidence survived family payload: {family_id}")
        if any(secret in text for secret in ("\"access_token\"", "\"password\"", "bearer ")) or JWT_RE.search(text):
            raise ProjectionError(f"credential material survived family payload: {family_id}")
        families[family_id] = family_payload
    out: dict[str, Any] = {
        "schema_version": "ace-target-evidence-projection-v1",
        "object_id": OBJECT_ID,
        "status": "TARGET_EVIDENCE_PROJECTION_V1_PASS_REPAIR_GENERATION_CLOSED",
        "source_closeout_content_sha256": closeout["content_sha256"],
        "source_closeout_file_sha256": sha256_file(SOURCE_CLOSEOUT),
        "source_ledger_sha256": closeout["ledger_sha256"],
        "projection_rule": {
            "drop_supervisor_and_login_transport": True,
            "drop_401_or_invalid_auth_attempts": True,
            "strip_access_tokens_passwords_and_authorization_fields": True,
            "drop_dummy_or_non_target_markers": list(FORBIDDEN_MARKERS),
            "retain_only_target_local_tool_evidence": True,
            "result_lists_pruned_to_target_local_records": True,
            "raw_trajectory_is_not_updater_input": True,
        },
        "selected_family_ids": selected,
        "families": families,
        "aggregate_projection_counts": totals,
        "provider_requests_created": 0,
        "repair_writer_requests_created": 0,
        "scientific_externality_outcomes_observed": 0,
        "authority": {
            "repair_generation": False,
            "development_repeat_qualification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "next_required_action": "Freeze a separate repair-writer-only execution authority for exactly these six projected target-failure payloads.",
    }
    out["content_sha256"] = sha256_value(out)
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    readiness: dict[str, Any] = {
        "schema_version": "ace-repair-generation-readiness-v1",
        "object_id": OBJECT_ID,
        "status": "ATOMGIT_REPEAT_DEV_REPAIR_GENERATION_READY_AWAITING_SEPARATE_HUMAN_AUTHORITY",
        "projection_content_sha256": out["content_sha256"],
        "projection_file_sha256": sha256_file(OUTPUT),
        "selected_family_ids": selected,
        "repair_writer_request_cap": 6,
        "one_frozen_repair_per_family": True,
        "human_edit_after_generation": False,
        "raw_source_trajectory_visible_to_writer": False,
        "provider_requests_created": 0,
        "authority": {"repair_generation": False, "development_repeat_qualification": False, "rq1_rq2": False},
        "next_required_action": "Separate human authority for exactly six repair-writer requests; no topology/repeat execution authority.",
    }
    readiness["content_sha256"] = sha256_value(readiness)
    READINESS.write_text(json.dumps(readiness, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main() -> None:
    print(json.dumps(build(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
