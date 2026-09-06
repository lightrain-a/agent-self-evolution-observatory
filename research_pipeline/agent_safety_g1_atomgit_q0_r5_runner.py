from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

from research_pipeline.agent_safety_g1_atomgit_chat_adapter import (
    MIN_CANDIDATE_START_REMAINING,
    MODEL_SPECS,
    probe_codingplan_usage,
)
from research_pipeline.agent_safety_g1_atomgit_q0_runner import (
    MAX_STEPS,
    TASK_IDS,
    RunnerError,
    candidate_receipt,
    configure_imports,
    load,
    run_episode,
)
from research_pipeline.agent_safety_g1_qwen397_benign_runner import atomic_json

ROOT = Path(__file__).resolve().parents[1]
R5_RUNNER_PATH = Path(__file__).resolve()
Q0_RUNNER_PATH = ROOT / "research_pipeline/agent_safety_g1_atomgit_q0_runner.py"
CHAT_ADAPTER_PATH = ROOT / "research_pipeline/agent_safety_g1_atomgit_chat_adapter.py"
R5_CANDIDATES = ["mimo-v2.5", "mimo-v2.5-pro"]
R3_CANDIDATES = ["qwen3.8-27b", "GLM-5.2", "deepseek-v4-flash"]
R3_CLOSEOUT = ROOT / "generated/agent-safety-g1-atomgit-q0-r3-closeout-20260906.json"
CATALOG = ROOT / "generated/agent-constraint-externality-codingplan-catalog-b1-20260903.json"
MIMO25_RESULT = ROOT / "generated/agent-constraint-externality-codingplan-mimo25-capability-b2-result-20260903.json"
MIMO25PRO_RESULT = ROOT / "generated/agent-constraint-externality-codingplan-mimo25pro-capability-b3-result-20260903.json"
SEARCH_B2 = ROOT / "generated/agent-constraint-externality-capability-backbone-search-state-b2-20260903.json"
SEARCH_B3 = ROOT / "generated/agent-constraint-externality-capability-backbone-search-state-b3-20260903.json"

EXPECTED_SHA256 = {
    R3_CLOSEOUT.name: "9a41facbaf1a1b1b921d6bc1767ce165af8429180c73d692687a7a8d90a578f7",
    CATALOG.name: "792927b03c2404c602a95c10c0e03724495ea80d02fc4be3c4503d580909781a",
    MIMO25_RESULT.name: "7bbe1c0ce20ab86ff37ec912fcde17cfad9a3a444581fbc7a0b2e2033d9d328c",
    MIMO25PRO_RESULT.name: "6af38f2b43b6fe9ee0acb94dc63a98e2d582145443828eb55c103cfee9fb1935",
    SEARCH_B2.name: "410c54c69622dab44d6c1d98622f47b957260729f1ac04dcc95dc67e91331f1f",
    SEARCH_B3.name: "6efd9a58c3408799fff2ebd872e7699495b200e264214cc0ac6f51668dbe67a4",
}

AUTH_ID = "AGENT-SAFETY-G1-ATOMGIT-Q0-R5-RESIDUAL-EXECUTION-AUTHORITY-20260906"
AUTH_STATUS = "ATOMGIT_Q0_R5_RESIDUAL_BENIGN_CAPABILITY_EXECUTION_AUTHORIZED"
EXPECTED_BROWSER_ART_COMMIT = "0d72180042f2a076c68e1114e7494cb3fc7dd30b"
NETWORK_PROBE_URLS = [
    "http://127.0.0.1:8000/twitter",
    "http://127.0.0.1:8000/instagram",
    "https://www.google.com",
]
EXPECTED_BROWSER_PROXY = {
    "server": "http://127.0.0.1:7897",
    "bypass": "127.0.0.1,localhost",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def validate_static_provenance() -> dict[str, Any]:
    for path in (R3_CLOSEOUT, CATALOG, MIMO25_RESULT, MIMO25PRO_RESULT, SEARCH_B2, SEARCH_B3):
        if not path.is_file() or sha256_file(path) != EXPECTED_SHA256[path.name]:
            raise RunnerError(f"R5 provenance drift:{path.name}")
    r3 = load(R3_CLOSEOUT)
    b2 = load(SEARCH_B2)
    b3 = load(SEARCH_B3)
    catalog = load(CATALOG)
    m25 = load(MIMO25_RESULT)
    m25p = load(MIMO25PRO_RESULT)
    if r3.get("status") != "ATOMGIT_Q0_PROTOCOL_INCONCLUSIVE_STOP_ALL" or r3.get("candidate_order") != R3_CANDIDATES:
        raise RunnerError("R3 terminal closeout drift")
    if (r3.get("authority") or {}).get("q0_retry") is not False:
        raise RunnerError("R3 replay unexpectedly open")
    if b2.get("remaining_frozen_order") != R5_CANDIDATES:
        raise RunnerError("pre-G1 residual order is not exactly MiMo25 then MiMo25Pro")
    if b3.get("remaining_frozen_order") != ["mimo-v2.5-pro"]:
        raise RunnerError("pre-G1 final residual order drift")
    rows = {row.get("model_id"): row for row in catalog.get("models", [])}
    for model in R5_CANDIDATES:
        row = rows.get(model)
        if not row or row.get("profile") != f"AtomGit-{model}" or row.get("context_window") != 1_000_000 or row.get("max_tokens") is not None:
            raise RunnerError(f"pre-G1 catalog drift:{model}")
        if model not in MODEL_SPECS:
            raise RunnerError(f"R5 adapter does not recognize frozen residual model:{model}")
    if m25.get("model_id") != "mimo-v2.5" or m25p.get("model_id") != "mimo-v2.5-pro":
        raise RunnerError("pre-G1 capability result identity drift")
    return {
        "r3_status": r3["status"],
        "r3_total_model_requests": int(r3.get("total_scientific_model_requests") or 0),
        "residual_candidate_order": list(R5_CANDIDATES),
        "pre_g1_mimo25_status": m25.get("status"),
        "pre_g1_mimo25pro_status": m25p.get("status"),
    }


def validate_authority(authority: dict[str, Any]) -> None:
    if authority.get("artifact_id") != AUTH_ID or authority.get("status") != AUTH_STATUS:
        raise RunnerError("unexpected R5 execution authority")
    if authority.get("candidate_order") != R5_CANDIDATES:
        raise RunnerError("R5 residual candidate order drift")
    if authority.get("task_ids") != TASK_IDS or authority.get("max_steps") != MAX_STEPS or authority.get("required_success_count") != 10:
        raise RunnerError("R5 Q0 panel drift")
    if authority.get("r3_replay_forbidden") is not True or authority.get("r3_candidate_reentry_forbidden") is not True:
        raise RunnerError("R5 authority must keep R3 immutable")
    if authority.get("selection_uses_only_benign_capability") is not True or authority.get("residual_set_frozen_from_pre_g1_evidence") is not True:
        raise RunnerError("R5 outcome-blind selection boundary missing")
    for key in ("harmful_model_calls", "p0_execution_authorized", "p1_execution_authorized", "paper_claim_upgrade"):
        if authority.get(key) is not False:
            raise RunnerError(f"R5 authority illegally opens {key}")
    if authority.get("parent_r3_closeout_sha256") != EXPECTED_SHA256[R3_CLOSEOUT.name]:
        raise RunnerError("R5 parent R3 binding drift")
    code_bindings = authority.get("code_bindings") or {}
    expected_code = {
        "r5_runner_sha256": R5_RUNNER_PATH,
        "q0_runner_sha256": Q0_RUNNER_PATH,
        "chat_adapter_sha256": CHAT_ADAPTER_PATH,
    }
    for key, path in expected_code.items():
        if code_bindings.get(key) != sha256_file(path):
            raise RunnerError(f"R5 execution code binding drift:{key}")
    runtime = authority.get("runtime") or {}
    required_runtime = (
        "python",
        "awm_root",
        "browserart_root",
        "auth_path",
        "node_path",
        "static_server_pid_file",
        "static_server_root",
        "static_server_git_root",
        "static_server_git_commit",
        "parent_r3_run_root",
        "r5_run_root",
    )
    if any(not str(runtime.get(key) or "").strip() for key in required_runtime):
        raise RunnerError("R5 runtime binding incomplete")
    if runtime.get("static_server_git_commit") != EXPECTED_BROWSER_ART_COMMIT:
        raise RunnerError("R5 BrowserART commit binding drift")
    if runtime.get("network_probe_urls") != NETWORK_PROBE_URLS:
        raise RunnerError("R5 network readiness panel drift")
    if runtime.get("browser_proxy") != EXPECTED_BROWSER_PROXY:
        raise RunnerError("R5 browser proxy binding drift")
    if Path(runtime["r5_run_root"]).resolve() == Path(runtime["parent_r3_run_root"]).resolve():
        raise RunnerError("R5 run root collides with immutable R3 root")


def _pid_alive(path: Path) -> bool:
    try:
        pid = int(path.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def _pid_from_file(path: Path) -> int:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except Exception as exc:
        raise RunnerError("R5 static server pid file unreadable") from exc


def _proc_cmdline(pid: int) -> list[str]:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError as exc:
        raise RunnerError("R5 static server process unavailable") from exc
    return [part.decode("utf-8", errors="strict") for part in raw.split(b"\0") if part]


def _git_head(root: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if proc.returncode != 0:
        raise RunnerError(f"R5 BrowserART git identity unavailable:{root}")
    return proc.stdout.strip()


def _git_tracked_surface_clean(root: Path) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no", "--", "src/websites"],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    return proc.returncode == 0 and not proc.stdout.strip()


def validate_live_static_server(runtime: dict[str, Any]) -> None:
    pid_path = Path(runtime["static_server_pid_file"])
    if not _pid_alive(pid_path):
        raise RunnerError("R5 frozen BrowserART static server unavailable")
    pid = _pid_from_file(pid_path)
    args = _proc_cmdline(pid)
    expected_python = Path(runtime["python"]).resolve()
    if not args or Path(args[0]).resolve() != expected_python:
        raise RunnerError("R5 static server python drift")
    if len(args) < 3 or args[1:3] != ["-m", "http.server"]:
        raise RunnerError("R5 static server launcher drift")
    try:
        root_index = args.index("-d") + 1
        served_root = Path(args[root_index]).resolve()
    except (ValueError, IndexError) as exc:
        raise RunnerError("R5 static server root is not explicitly bound") from exc
    expected_root = Path(runtime["static_server_root"]).resolve()
    if served_root != expected_root:
        raise RunnerError("R5 static server served-root drift")
    port = int(runtime.get("static_server_port") or 8000)
    if str(port) not in args or not _port_open("127.0.0.1", port):
        raise RunnerError("R5 static server port drift or unavailable")
    live_git_root = Path(runtime["static_server_git_root"]).resolve()
    frozen_git_root = Path(runtime["browserart_root"]).resolve()
    expected_commit = runtime["static_server_git_commit"]
    if _git_head(live_git_root) != expected_commit or _git_head(frozen_git_root) != expected_commit:
        raise RunnerError("R5 BrowserART live/frozen commit drift")
    if not _git_tracked_surface_clean(live_git_root) or not _git_tracked_surface_clean(frozen_git_root):
        raise RunnerError("R5 BrowserART tracked website surface is dirty")


def _network_http_status_ready(http_status: Any) -> bool:
    return isinstance(http_status, int) and 200 <= http_status < 400


def validate_browser_network_readiness(urls: list[str], proxy: dict[str, str]) -> dict[str, Any]:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise RunnerError("R5 Playwright network preflight unavailable") from exc
    if proxy != EXPECTED_BROWSER_PROXY:
        raise RunnerError("R5 browser proxy binding drift")
    if not _port_open("127.0.0.1", 7897):
        raise RunnerError("R5 browser proxy transport unavailable")
    rows: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(proxy=dict(proxy))
        try:
            for url in urls:
                page = context.new_page()
                try:
                    response = page.goto(url, timeout=10_000)
                    http_status = response.status if response is not None else None
                    status = "LOAD_PASS" if _network_http_status_ready(http_status) else "LOAD_HTTP_ERROR"
                    rows.append({
                        "url": url,
                        "status": status,
                        "http_status": http_status,
                        "final_url": page.url,
                    })
                except PlaywrightTimeoutError as exc:
                    rows.append({"url": url, "status": "LOAD_TIMEOUT", "error_type": type(exc).__name__})
                except Exception as exc:
                    rows.append({"url": url, "status": "LOAD_ERROR", "error_type": type(exc).__name__})
                finally:
                    page.close()
        finally:
            context.close()
            browser.close()
    failed = [row for row in rows if row["status"] != "LOAD_PASS"]
    if failed:
        failed_urls = ",".join(row["url"] for row in failed)
        raise RunnerError(f"R5 browser network readiness failed:{failed_urls}")
    return {"status": "R5_BROWSER_NETWORK_READINESS_PASS", "proxy": dict(proxy), "rows": rows}


def validate_runtime(authority: dict[str, Any], *, output_root: Path, awm: Path, browserart: Path, auth_path: Path) -> None:
    runtime = authority["runtime"]
    if Path(sys.executable).resolve() != Path(runtime["python"]).resolve():
        raise RunnerError("R5 runtime python drift")
    if awm.resolve() != Path(runtime["awm_root"]).resolve() or browserart.resolve() != Path(runtime["browserart_root"]).resolve():
        raise RunnerError("R5 substrate path drift")
    if auth_path.resolve() != Path(runtime["auth_path"]).resolve() or not auth_path.is_file():
        raise RunnerError("R5 AtomCode auth binding unavailable")
    if output_root.resolve() != Path(runtime["r5_run_root"]).resolve():
        raise RunnerError("R5 output root drift")
    parent_root = Path(runtime["parent_r3_run_root"]).resolve()
    parent_receipt = parent_root / "q0-cascade-receipt.json"
    if not parent_receipt.is_file() or sha256_file(parent_receipt) != authority.get("parent_r3_cascade_receipt_sha256"):
        raise RunnerError("immutable R3 runtime receipt unavailable or drifted")
    if os.environ.get("NODE_PATH") != runtime["node_path"]:
        raise RunnerError("R5 NODE_PATH drift")
    validate_live_static_server(runtime)
    validate_browser_network_readiness(list(runtime["network_probe_urls"]), dict(runtime["browser_proxy"]))


def run_r5_cascade(*, authority: dict[str, Any], output_root: Path, awm: Path, browserart: Path, auth_path: Path) -> dict[str, Any]:
    provenance = validate_static_provenance()
    validate_authority(authority)
    validate_runtime(authority, output_root=output_root, awm=awm, browserart=browserart, auth_path=auth_path)
    if output_root.exists() and any(output_root.iterdir()):
        raise RunnerError("non-empty R5 output root")
    output_root.mkdir(parents=True, exist_ok=True)
    configure_imports(awm, browserart)
    candidates: list[dict[str, Any]] = []
    selected: str | None = None
    terminal = "ATOMGIT_Q0_R5_ALL_RESIDUAL_CANDIDATES_VALID_BENIGN_FAIL"
    for model_id in R5_CANDIDATES:
        model_root = output_root / model_id
        model_root.mkdir(parents=True, exist_ok=False)
        quota = probe_codingplan_usage(model_id=model_id, auth_path=auth_path, runtime_root=model_root / "quota-probe")
        atomic_json(model_root / "candidate-quota-admission.json", {
            "schema_version": "g1-atomgit-q0-r5-candidate-quota-admission-v1",
            "model_id": model_id,
            "usage": quota,
            "minimum_remaining_required": MIN_CANDIDATE_START_REMAINING,
            "model_request_dispatched": False,
            "admitted": isinstance(quota.get("remaining"), int) and quota["remaining"] >= MIN_CANDIDATE_START_REMAINING,
        })
        if not isinstance(quota.get("remaining"), int) or quota["remaining"] < MIN_CANDIDATE_START_REMAINING:
            candidates.append({
                "model_id": model_id,
                "status": "ATOMGIT_Q0_R5_CANDIDATE_NOT_STARTED_INSUFFICIENT_FULL_BUDGET",
                "episode_count": 0,
                "success_count": 0,
                "model_requests": 0,
                "quota_admission": quota,
                "safety_executed": False,
                "harmful_calls": 0,
                "episodes": [],
            })
            terminal = "ATOMGIT_Q0_R5_OPERATIONAL_HOLD_INSUFFICIENT_FULL_CANDIDATE_BUDGET"
            break
        episodes: list[dict[str, Any]] = []
        for task_id in TASK_IDS:
            row = run_episode(
                task_id,
                model_id=model_id,
                out=model_root,
                awm=awm,
                browserart=browserart,
                auth_path=auth_path,
                pw_context_kwargs={"proxy": dict(authority["runtime"]["browser_proxy"])},
            )
            episodes.append(row)
            if row["status"] != "COMPLETE_DIAGNOSTIC" or row["success_by_step10"] is False:
                break
        receipt = candidate_receipt(model_id, episodes)
        receipt["r5_residual_candidate"] = True
        atomic_json(model_root / "candidate-receipt.json", receipt)
        candidates.append(receipt)
        if receipt["status"] == "ATOMGIT_Q0_CANDIDATE_PASS":
            selected = model_id
            terminal = "ATOMGIT_Q0_R5_BENIGN_CAPABILITY_PASS"
            break
        if receipt["status"] == "ATOMGIT_Q0_PROTOCOL_INCONCLUSIVE_STOP_ALL":
            terminal = "ATOMGIT_Q0_R5_PROTOCOL_INCONCLUSIVE_STOP_ALL"
            break
    result = {
        "schema_version": "g1-atomgit-q0-r5-residual-cascade-receipt-v1",
        "artifact_id": "AGENT-SAFETY-G1-ATOMGIT-Q0-R5-RESIDUAL-CASCADE-RECEIPT-20260906",
        "status": terminal,
        "selected_primary": selected,
        "candidate_order": list(R5_CANDIDATES),
        "parent_r3_closeout_sha256": EXPECTED_SHA256[R3_CLOSEOUT.name],
        "r3_replayed": False,
        "pre_g1_provenance": provenance,
        "candidates": candidates,
        "total_model_requests": sum(int(row.get("model_requests") or 0) for row in candidates),
        "safety_executed": False,
        "harmful_calls": 0,
        "p0_execution_authorized": False,
        "p1_execution_authorized": False,
        "paper_claim_upgrade": False,
    }
    atomic_json(output_root / "q0-r5-cascade-receipt.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--awm-root", type=Path, required=True)
    parser.add_argument("--browserart-root", type=Path, required=True)
    parser.add_argument("--auth-path", type=Path, required=True)
    args = parser.parse_args()
    result = run_r5_cascade(
        authority=load(args.authority),
        output_root=args.output_root,
        awm=args.awm_root,
        browserart=args.browserart_root,
        auth_path=args.auth_path,
    )
    print(json.dumps({
        "status": result["status"],
        "selected_primary": result["selected_primary"],
        "total_model_requests": result["total_model_requests"],
        "harmful_calls": 0,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
