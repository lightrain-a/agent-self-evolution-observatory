from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .paper_preparation_protocol import validate_paper_preparation_receipt
from .presubmission_freeze import validate_freeze, verify_current_frozen_artifacts

HANDOFF_SCHEMA_VERSION = "1.0"
HANDOFF_STATUS = "MACHINE_HANDOFF_READY_HUMAN_CONFIRMATION_REQUIRED"
AUTHORITY = {"scientific": False, "experiment": False, "gpu": False, "submission": False}


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _latest_event(row: Mapping[str, Any], event_type: str) -> dict[str, Any]:
    for event in reversed(list(row.get("events") or [])):
        if isinstance(event, Mapping) and event.get("event_type") == event_type:
            return dict(event)
    return {}


def _latest_freeze(freeze_ledger: Mapping[str, Any]) -> dict[str, Any]:
    event = _latest_event(freeze_ledger, "pre-submission-freeze")
    receipt = event.get("receipt") or {}
    return dict(receipt) if isinstance(receipt, Mapping) else {}


def _latest_preparation(paper_ledger: Mapping[str, Any]) -> dict[str, Any]:
    event = _latest_event(paper_ledger, "paper-preparation")
    receipt = event.get("receipt") or {}
    return dict(receipt) if isinstance(receipt, Mapping) else {}


def handoff_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "paper_id": receipt.get("paper_id"),
        "contract_sha256": receipt.get("contract_sha256"),
        "paper_preparation_receipt_sha256": receipt.get("paper_preparation_receipt_sha256"),
        "freeze_sha256": receipt.get("freeze_sha256"),
        "venue_policy_snapshot_sha256": receipt.get("venue_policy_snapshot_sha256"),
        "frozen_artifacts": receipt.get("frozen_artifacts") or [],
        "deadlines_aoe": receipt.get("deadlines_aoe") or {},
        "human_checklist": receipt.get("human_checklist") or [],
        "must_not_submit_if_hash_mismatch": receipt.get("must_not_submit_if_hash_mismatch"),
        "must_not_submit_if_freeze_stale": receipt.get("must_not_submit_if_freeze_stale"),
        "external_human_submission_authority_required": receipt.get("external_human_submission_authority_required"),
        "status": receipt.get("status"),
    }


def build_handoff_receipt(
    *,
    paper_ledger: Mapping[str, Any],
    freeze_ledger: Mapping[str, Any],
    venue_policy: Mapping[str, Any],
) -> dict[str, Any]:
    paper_id = str(paper_ledger.get("paper_id") or "")
    if not paper_id or str(freeze_ledger.get("paper_id") or "") != paper_id:
        raise RuntimeError("paper/freeze identity mismatch")
    if str(paper_ledger.get("current_state") or "") != "SUBMISSION_READY":
        raise RuntimeError(f"{paper_id} is not SUBMISSION_READY")
    preparation = _latest_preparation(paper_ledger)
    if preparation.get("pass") is not True or not validate_paper_preparation_receipt(preparation):
        raise RuntimeError(f"{paper_id} paper preparation is not a valid PASS")
    freeze_errors = validate_freeze(freeze_ledger)
    if freeze_errors:
        raise RuntimeError(f"{paper_id} freeze ledger is structurally invalid: {freeze_errors}")
    drift = verify_current_frozen_artifacts(freeze_ledger)
    if drift:
        raise RuntimeError(f"{paper_id} frozen artifacts are stale: {drift}")
    freeze = _latest_freeze(freeze_ledger)
    if freeze.get("status") != "MACHINE_FROZEN_HUMAN_SIGNOFF_PENDING":
        raise RuntimeError(f"{paper_id} latest freeze is not handoff eligible")
    policy_sha = str(venue_policy.get("snapshot_sha256") or "")
    if not policy_sha or _digest({k: v for k, v in venue_policy.items() if k != "snapshot_sha256"}) != policy_sha:
        raise RuntimeError("venue policy snapshot digest mismatch")
    if str(freeze.get("venue_policy_snapshot_sha256") or "") != policy_sha:
        raise RuntimeError(f"{paper_id} freeze/policy snapshot mismatch")
    artifacts = []
    for row in freeze.get("frozen_artifacts") or []:
        if not isinstance(row, Mapping):
            continue
        artifacts.append({
            "label": str(row.get("label") or "artifact"),
            "filename": Path(str(row.get("path") or "artifact")).name,
            "sha256": str(row.get("sha256") or ""),
            "bytes": int(row.get("bytes") or 0),
        })
    checklist = list(dict.fromkeys([
        *[str(x) for x in freeze.get("human_checklist") or [] if str(x)],
        "confirm title and abstract used for reviewer bidding are the intended final submission metadata",
        "confirm every author accepts responsibility for the final manuscript and AI-assisted artifacts",
        "capture final OpenReview form snapshot and pass venue-form consistency audit",
        "recompute and compare every frozen artifact SHA256 immediately before upload",
    ]))
    receipt: dict[str, Any] = {
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "receipt_type": "machine-submission-handoff",
        "paper_id": paper_id,
        "title": str((paper_ledger.get("contract") or {}).get("title") or paper_id),
        "contract_sha256": str(paper_ledger.get("contract_sha256") or ""),
        "paper_preparation_receipt_sha256": str(preparation.get("receipt_sha256") or ""),
        "freeze_sha256": str(freeze.get("freeze_sha256") or ""),
        "venue": str(venue_policy.get("venue") or ""),
        "venue_policy_snapshot_sha256": policy_sha,
        "deadlines_aoe": dict(venue_policy.get("deadlines_aoe") or {}),
        "frozen_artifacts": artifacts,
        "machine_verified": {
            "paper_acceptance_submission_ready": True,
            "paper_preparation_8_of_8_pass": int((preparation.get("summary") or {}).get("passed_gates") or 0) == 8,
            "freeze_structural_integrity_pass": True,
            "freeze_artifact_bytes_current": True,
            "venue_policy_snapshot_bound": True,
            "ai_use_disclosure_decision_recorded_by_preparation_gate": True,
            "venue_form_consistency_audit_required_before_human_signoff": True,
        },
        "human_checklist": checklist,
        "human_confirmation_status": "PENDING_HUMAN",
        "must_not_submit_if_hash_mismatch": True,
        "must_not_submit_if_freeze_stale": True,
        "external_human_submission_authority_required": True,
        "status": HANDOFF_STATUS,
        "handoff_at": str(freeze.get("frozen_at") or freeze_ledger.get("updated_at") or ""),
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["handoff_sha256"] = _digest(handoff_identity(receipt))
    return receipt


def validate_handoff_receipt(receipt: Mapping[str, Any]) -> bool:
    if str(receipt.get("receipt_type") or "") != "machine-submission-handoff":
        return False
    if receipt.get("status") != HANDOFF_STATUS:
        return False
    if receipt.get("human_confirmation_status") != "PENDING_HUMAN":
        return False
    if any(receipt.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
        return False
    return str(receipt.get("handoff_sha256") or "") == _digest(handoff_identity(receipt))


def append_handoff(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_handoff_receipt(receipt):
        raise RuntimeError("invalid machine handoff receipt")
    paper_id = str(receipt.get("paper_id") or "")
    directory = Path(root) / "paper-submission-handoffs"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{paper_id}.json"
    lock = directory / f".{paper_id}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        row = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "schema_version": HANDOFF_SCHEMA_VERSION,
            "paper_id": paper_id,
            "events": [],
            "authority": dict(AUTHORITY),
        }
        latest = _latest_event(row, "machine-submission-handoff")
        latest_receipt = latest.get("receipt") if isinstance(latest.get("receipt"), Mapping) else {}
        if latest_receipt.get("handoff_sha256") == receipt.get("handoff_sha256"):
            return row
        event = {
            "event_type": "machine-submission-handoff",
            "receipt": dict(receipt),
            "recorded_at": str(receipt.get("handoff_at") or ""),
            "scientific_authority": False,
            "experiment_authority": False,
            "gpu_authority": False,
            "submission_authority": False,
        }
        event["event_id"] = _digest([paper_id, len(row.get("events") or []), event])[:24]
        row.setdefault("events", []).append(event)
        row["updated_at"] = event["recorded_at"]
        _atomic(path, row)
        return row


def validate_handoff_ledger(row: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if (row.get("authority") or {}) != AUTHORITY:
        errors.append("handoff ledger must not grant authority")
    for event in row.get("events") or []:
        if not isinstance(event, Mapping) or event.get("event_type") != "machine-submission-handoff":
            errors.append("unknown handoff event")
            continue
        receipt = event.get("receipt") or {}
        if not isinstance(receipt, Mapping) or not validate_handoff_receipt(receipt):
            errors.append("invalid handoff receipt")
        if any(event.get(key) is True for key in ("scientific_authority", "experiment_authority", "gpu_authority", "submission_authority")):
            errors.append("handoff event leaked authority")
    return list(dict.fromkeys(errors))


def render_handoff_markdown(receipt: Mapping[str, Any]) -> str:
    artifacts = receipt.get("frozen_artifacts") or []
    checks = receipt.get("human_checklist") or []
    deadlines = receipt.get("deadlines_aoe") or {}
    translations = {
        "confirm complete author list and OpenReview profiles": "确认完整作者名单，并逐一确认 OpenReview profile / email / affiliation。",
        "confirm author quota and reciprocal-reviewing obligations": "确认作者投稿配额与 reciprocal reviewing 义务。",
        "confirm dual-submission compliance": "确认不存在违反 venue policy 的实质相同稿件并行投稿。",
        "acknowledge ICLR Code of Ethics": "所有作者确认 ICLR Code of Ethics / Conduct 要求。",
        "review and approve mandatory AI-use disclosure": "所有作者审阅并批准强制 AI-use disclosure。",
        "verify final PDF/source/supplement hashes immediately before upload": "上传前最后一次核对 PDF / source / supplement 的 SHA256。",
        "confirm title and abstract used for reviewer bidding are the intended final submission metadata": "确认用于 reviewer bidding 的标题与摘要就是计划提交的正式 metadata。",
        "confirm every author accepts responsibility for the final manuscript and AI-assisted artifacts": "确认每位作者对最终稿及 AI-assisted artifacts 承担责任。",
        "capture final OpenReview form snapshot and pass venue-form consistency audit": "保存最终 OpenReview 表单快照，并通过 title / abstract / keywords / author visibility / AI-use disclosure / supplement 的逐字段一致性审计。",
        "recompute and compare every frozen artifact SHA256 immediately before upload": "真实上传前重新计算并逐项比对所有冻结工件 SHA256。",
    }
    lines = [
        f"# 投稿交接单 · {receipt.get('title')}",
        "",
        "> 机器侧已经完成论文准备、字节冻结与交接打包；当前仍需作者人工确认。此文件不代表论文已经投稿。",
        "",
        f"- Paper ID: `{receipt.get('paper_id')}`",
        f"- 当前状态: `{receipt.get('status')}`",
        f"- 目标会议: `{receipt.get('venue')}`",
        f"- Freeze SHA256: `{receipt.get('freeze_sha256')}`",
        f"- Preparation receipt SHA256: `{receipt.get('paper_preparation_receipt_sha256')}`",
        f"- Venue-policy snapshot SHA256: `{receipt.get('venue_policy_snapshot_sha256')}`",
        f"- 摘要截止（AOE）: `{deadlines.get('abstract','')}`",
        f"- 全文截止（AOE）: `{deadlines.get('full_paper','')}`",
        "",
        "## 1. 已冻结的上传工件",
        "",
    ]
    for item in artifacts:
        lines.append(f"- `{item.get('label')}` · `{item.get('filename')}` · {item.get('bytes')} bytes · SHA256 `{item.get('sha256')}`")
    lines += [
        "",
        "## 2. 作者需要逐项确认",
        "",
    ]
    for item in checks:
        lines.append(f"- [ ] {translations.get(str(item), str(item))}")
    lines += [
        "",
        "## 3. 上传硬规则",
        "",
        "**只要任何冻结工件的 SHA256 与本交接单不一致，或者 machine freeze 已 stale，就禁止继续上传；必须重新生成 freeze 与 handoff。**",
        "",
        "本交接单的 scientific / experiment / GPU / submission authority 全部为 0。只有明确的人类提交授权才能进入真实 `SUBMITTED`。",
        "",
    ]
    return "\n".join(lines)
