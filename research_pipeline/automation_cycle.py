from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .config import PROJECT_ROOT, StorageSettings
from .cvpr_idea_factory import write_cvpr_idea_bank
from .discussion_portfolio import write_discussion_portfolio
from .human_terminal_state import write_human_terminal_state
from .p0_admission import write_p0_admission_state
from .iclr_experiment_audit import write_audit as write_iclr_audit
from .iclr_idea_factory import write_iclr_idea_bank
from .idea_discovery_v3 import write_idea_discovery_v3
from .idea_discovery_v31 import write_idea_discovery_v31
from .idea_discovery_v5 import write_idea_discovery_v5
from .idea_discovery_v51 import write_idea_discovery_v51
from .idea_discovery_v52 import write_idea_discovery_v52
from .idea_discovery_v53 import write_idea_discovery_v53
from .idea_discovery_v4 import write_idea_discovery_v4
from .machine_school_idea_factory import write_machine_school_bank
from .live_pipeline import sync_semantic_scholar
from .published_experiment_audit import write_audit as write_published_audit
from .research_system import write_research_system_state
from .publication import PUBLICATION_OK_STATES, publish_generated_state


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@contextmanager
def cycle_lock(path: Path, *, stale_after_seconds: float = 21600) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and time.time() - path.stat().st_mtime > stale_after_seconds:
        path.unlink(missing_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise RuntimeError(f"Another automation cycle is active: {path}") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({"pid": os.getpid(), "started_at": _now()}))
        yield
    finally:
        path.unlink(missing_ok=True)


def run_cycle(
    *,
    mode: str = "daily",
    sync_literature: bool = False,
    web_review_limit: int = 0,
    publish: bool = False,
) -> dict[str, Any]:
    storage = StorageSettings.from_env()
    storage.ensure()
    run_dir = storage.run_dir / "automation"
    run_dir.mkdir(parents=True, exist_ok=True)
    lock = storage.lock_dir / ".research-automation-cycle.lock"
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "started_at": _now(),
        "mode": mode,
        "sync_literature": sync_literature,
        "web_review_limit": web_review_limit,
        "publish": publish,
        "steps": [],
        "status": "running",
    }
    with cycle_lock(lock):
        if sync_literature:
            report["steps"].append(_step("literature-sync", _sync_literature))
        if mode in {"weekly", "manual"}:
            report["steps"].append(_step("iclr-bank", write_iclr_idea_bank))
            report["steps"].append(_step("machine-school-inspired-bank", write_machine_school_bank))
            report["steps"].append(_step("solution-first-idea-discovery-v3", write_idea_discovery_v3))
            report["steps"].append(_step("reviewer-repaired-idea-discovery-v31", write_idea_discovery_v31))
            report["steps"].append(_step("expanded-idea-discovery-v5", write_idea_discovery_v5))
            report["steps"].append(_step("reviewer-targeted-idea-discovery-v51", write_idea_discovery_v51))
            report["steps"].append(_step("second-order-idea-discovery-v52", write_idea_discovery_v52))
            report["steps"].append(_step("final-boundary-idea-discovery-v53", write_idea_discovery_v53))
            report["steps"].append(_step("discussion-ready-portfolio", write_discussion_portfolio))
            report["steps"].append(_step("constrained-combination-idea-discovery-v4", write_idea_discovery_v4))
            report["steps"].append(_step("iclr-audit", write_iclr_audit))
            report["steps"].append(_step("cvpr-followup-bank", write_cvpr_idea_bank))
            report["steps"].append(_step("published-visual-audit", write_published_audit))
        report["steps"].append(_step("human-terminal-idea-state", write_human_terminal_state))
        report["steps"].append(_step("p0-admission-state", write_p0_admission_state))
        report["steps"].append(_step("research-system-state", write_research_system_state))
        if web_review_limit > 0:
            report["steps"].append(_step("project-web-gpt-repair-review", lambda: _run_web_reviews(web_review_limit, storage)))
        report["status"] = "pass" if all(step["status"] == "pass" for step in report["steps"]) else "degraded"
    report["completed_at"] = _now()
    stamp = report["completed_at"].replace(":", "-")
    report_path = run_dir / f"cycle-{stamp}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest = run_dir / "latest.json"
    latest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if publish:
        # Rebuild once so the public state can include the latest cycle report, then publish
        # only if normalized content has changed.
        write_human_terminal_state()
        write_p0_admission_state()
        write_research_system_state()
        publication_started = time.time()
        try:
            publication_result = publish_generated_state(mode=mode)
            publication_status = "pass" if publication_result.get("status") in PUBLICATION_OK_STATES else "fail"
            publication = {
                "name": "publish-generated-state",
                "status": publication_status,
                "duration_seconds": round(time.time() - publication_started, 3),
                "summary": publication_result,
            }
        except Exception as error:
            publication = {
                "name": "publish-generated-state",
                "status": "fail",
                "duration_seconds": round(time.time() - publication_started, 3),
                "error": f"{type(error).__name__}: {error}",
            }
        report["steps"].append(publication)
        if publication["status"] != "pass":
            report["status"] = "degraded"
        report["completed_at"] = _now()
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        latest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def _step(name: str, function: Any) -> dict[str, Any]:
    started = time.time()
    try:
        result = function()
        return {
            "name": name,
            "status": "pass",
            "duration_seconds": round(time.time() - started, 3),
            "summary": _safe_summary(result),
        }
    except Exception as error:  # keep the cycle alive and preserve prior valid artifacts
        return {
            "name": name,
            "status": "fail",
            "duration_seconds": round(time.time() - started, 3),
            "error": f"{type(error).__name__}: {error}",
        }


def _safe_summary(result: Any) -> Any:
    if not isinstance(result, dict):
        return str(result)[:500]
    for key in ("summary", "statistics", "health"):
        if key in result:
            return result[key]
    return {key: result[key] for key in list(result)[:8]}


def _sync_literature() -> dict[str, Any]:
    old_retries = os.environ.get("S2_MAX_RETRIES")
    old_timeout = os.environ.get("S2_TIMEOUT_SECONDS")
    os.environ["S2_MAX_RETRIES"] = os.getenv("AUTOMATION_S2_MAX_RETRIES", "2")
    os.environ["S2_TIMEOUT_SECONDS"] = os.getenv("AUTOMATION_S2_TIMEOUT_SECONDS", "20")
    try:
        return sync_semantic_scholar(
            total_limit=int(os.getenv("AUTOMATION_S2_LIMIT", "300")),
            per_query_limit=int(os.getenv("AUTOMATION_S2_PER_QUERY", "10")),
            citation_seed_count=int(os.getenv("AUTOMATION_S2_CITATION_SEEDS", "8")),
            citation_limit=int(os.getenv("AUTOMATION_S2_CITATION_LIMIT", "6")),
            citation_depth=1,
            force_refresh=False,
        )
    finally:
        if old_retries is None:
            os.environ.pop("S2_MAX_RETRIES", None)
        else:
            os.environ["S2_MAX_RETRIES"] = old_retries
        if old_timeout is None:
            os.environ.pop("S2_TIMEOUT_SECONDS", None)
        else:
            os.environ["S2_TIMEOUT_SECONDS"] = old_timeout


def _run_web_reviews(limit: int, storage: StorageSettings) -> dict[str, Any]:
    state_path = PROJECT_ROOT / "generated" / "research-system-state.json"
    if not state_path.exists():
        raise RuntimeError("research system state must be generated before web review")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    queue = (state.get("repair_queue") or {}).get("queue") or []
    idea_path = PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json"
    ideas_payload = json.loads(idea_path.read_text(encoding="utf-8"))
    ideas = {str(item["id"]): item for item in list(ideas_payload.get("passed_ideas") or []) + list(ideas_payload.get("blocked_ideas") or [])}
    output_dir = storage.run_dir / "reviews" / "automatic-repairs"
    output_dir.mkdir(parents=True, exist_ok=True)
    completed: list[dict[str, Any]] = []
    from .review_repair import build_web_review_prompt
    for item in queue[:limit]:
        idea = ideas.get(str(item["idea_id"]))
        if not idea:
            continue
        output = output_dir / f"{item['idea_id']}.md"
        command = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "project_web_gpt.py"),
            "--json", "--timeout", os.getenv("AUTOMATION_WEB_GPT_TIMEOUT", "240"),
            "--slug", f"auto-repair-{item['idea_id'][:35]}",
            "--output", str(output),
            build_web_review_prompt(item, idea),
        ]
        completed_process = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=300, check=False)
        completed.append({
            "idea_id": item["idea_id"],
            "returncode": completed_process.returncode,
            "output": str(output),
            "exists": output.exists(),
            "stderr": completed_process.stderr[-1000:],
        })
    return {"requested": limit, "completed": completed}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a fail-safe continuous research cycle.")
    parser.add_argument("--mode", choices=("daily", "weekly", "manual"), default="manual")
    parser.add_argument("--sync-literature", action="store_true")
    parser.add_argument("--web-review-limit", type=int, default=0)
    parser.add_argument("--publish", action="store_true", help="Publish substantive generated-artifact changes to origin/main.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_cycle(mode=args.mode, sync_literature=args.sync_literature, web_review_limit=max(args.web_review_limit, 0), publish=args.publish)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
