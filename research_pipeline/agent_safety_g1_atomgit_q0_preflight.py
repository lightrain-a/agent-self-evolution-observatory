from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AMENDMENT = ROOT / "generated/agent-safety-g1-atomgit-cost-aware-q0-amendment-r4-20260906.json"
DEFAULT_NETWORK_ADDENDUM = ROOT / "generated/agent-safety-g1-atomgit-q0-browser-network-addendum-r4p2-20260906.json"
DEFAULT_AWM = Path("/data/wyt/agent-safety-discovery-20260818/substrate-assets-r9/agent-workflow-memory")
DEFAULT_BROWSERART = Path("/data/wyt/agent-safety-discovery-20260818/substrate-assets-r9/browser-art-pinned-0d72180042f2")
EXPECTED_AWM_COMMIT = "8c0ff8cd11d648c8fceb99e4e42f37e3b75381b1"
EXPECTED_BROWSERART_COMMIT = "0d72180042f2a076c68e1114e7494cb3fc7dd30b"
EXPECTED_DATASET_SHA256 = "8edea0d4d393cae54e0ee39361ca0f5643c02cf02e694dcf9a543cce8116e774"
EXPECTED_GENERIC_AGENT_SHA256 = "0cd844f94881850aba8fd1956837e8e7e2f87e3168629596674593859b1da424"


class PreflightError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def load_amendment(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("artifact_id") != "AGENT-SAFETY-G1-ATOMGIT-COST-AWARE-Q0-AMENDMENT-R4-20260906":
        raise PreflightError("unexpected AtomGit Q0 amendment")
    if value.get("status") != "FROZEN_ZERO_PROVIDER_Q0_MODEL_SELECTION_AMENDMENT_NO_HARMFUL_AUTHORITY":
        raise PreflightError("AtomGit Q0 amendment is not frozen")
    if value.get("authority", {}).get("q0_model_requests") is not False:
        raise PreflightError("preflight requires Q0 model requests to remain unauthorized")
    if value.get("authority", {}).get("harmful_model_calls") is not False:
        raise PreflightError("harmful model calls must remain unauthorized")
    return value


def load_network_addendum(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("artifact_id") != "AGENT-SAFETY-G1-ATOMGIT-Q0-BROWSER-NETWORK-ADDENDUM-R4P2-20260906":
        raise PreflightError("unexpected AtomGit Q0 browser-network addendum")
    if value.get("status") != "FROZEN_ZERO_MODEL_REQUEST_BROWSER_NETWORK_ADDENDUM_NO_Q0_AUTHORITY":
        raise PreflightError("AtomGit Q0 browser-network addendum is not frozen")
    runtime = value.get("runtime_contract", {})
    if runtime.get("browser_network_mode") != "UNIFORM_CHROMIUM_PROXY_ALL_Q0_TASKS":
        raise PreflightError("browser-network mode drift")
    if runtime.get("same_proxy_endpoint_for_all_ten_tasks") is not True or runtime.get("task_specific_proxy_or_route_override") is not False:
        raise PreflightError("browser-network addendum permits task-specific routing")
    if value.get("authority", {}).get("q0_model_requests") is not False or value.get("authority", {}).get("harmful_model_calls") is not False:
        raise PreflightError("browser-network addendum illegally opens model execution")
    return value


def resolve_browser_proxy(explicit: str | None = None) -> str | None:
    value = (explicit or os.getenv("G1_BROWSER_PROXY", "")).strip()
    return value or None


def probe_browser_proxy(proxy: str | None) -> dict[str, Any]:
    if not proxy:
        return {
            "mode": "UNIFORM_CHROMIUM_PROXY_ALL_Q0_TASKS",
            "proxy_endpoint": None,
            "requests": [],
            "pass": False,
            "reason": "browser proxy is not configured",
        }
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    rows: list[dict[str, Any]] = []
    for name, url in (
        ("twitter_static_transport", "https://twitter.com/compose/twitter-logo.png"),
        ("google_transport", "https://www.google.com/"),
    ):
        started = time.monotonic()
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with opener.open(request, timeout=8) as response:
                response.read(1)
                rows.append({"name": name, "status": int(response.status), "elapsed_ms": round((time.monotonic() - started) * 1000, 1), "pass": 200 <= int(response.status) < 400})
        except Exception as exc:
            rows.append({"name": name, "status": None, "elapsed_ms": round((time.monotonic() - started) * 1000, 1), "pass": False, "error_class": type(exc).__name__})
    return {
        "mode": "UNIFORM_CHROMIUM_PROXY_ALL_Q0_TASKS",
        "proxy_endpoint": proxy,
        "requests": rows,
        "pass": bool(rows) and all(row["pass"] for row in rows),
        "task_specific_override": False,
        "provider_calls": 0,
    }


def git_head(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def git_dirty(path: Path) -> bool | None:
    if not (path / ".git").exists():
        return None
    try:
        raw = subprocess.check_output(["git", "-C", str(path), "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL)
        return bool(raw.strip())
    except Exception:
        return None


def resolve_atomcode() -> Path | None:
    found = shutil.which("atomcode")
    return Path(found).resolve() if found else None


def candidate_auth_paths(explicit: Path | None = None) -> list[Path]:
    rows: list[Path] = []
    if explicit is not None:
        rows.append(explicit.expanduser())
    env_path = os.getenv("ATOMCODE_AUTH_PATH", "").strip()
    if env_path:
        rows.append(Path(env_path).expanduser())
    rows.extend([Path.home() / ".atomcode/auth.toml", Path("/home/wyt/.atomcode/auth.toml")])
    dedup: list[Path] = []
    seen: set[str] = set()
    for row in rows:
        key = str(row)
        if key not in seen:
            seen.add(key)
            dedup.append(row)
    return dedup


def find_auth(explicit: Path | None = None) -> tuple[Path | None, list[str]]:
    checked = candidate_auth_paths(explicit)
    for path in checked:
        if path.is_file():
            return path.resolve(), [str(x) for x in checked]
    return None, [str(x) for x in checked]


def preflight(*, amendment: Path, network_addendum: Path = DEFAULT_NETWORK_ADDENDUM, awm_root: Path, browserart_root: Path, auth_path: Path | None = None, browser_proxy: str | None = None) -> dict[str, Any]:
    started = time.time_ns()
    frozen = load_amendment(amendment)
    network = load_network_addendum(network_addendum)
    dataset = browserart_root / "src/datasets/behaviors/hbb_benign.json"
    generic_agent = awm_root / "webarena/agents/legacy/agent.py"
    checks: dict[str, Any] = {}

    checks["amendment"] = {
        "path": str(amendment.resolve()),
        "status": frozen["status"],
        "candidate_order": [row["model_id"] for row in frozen["outcome_blind_candidate_order"]],
        "pass": True,
    }
    checks["browser_network_addendum"] = {
        "path": str(network_addendum.resolve()),
        "status": network["status"],
        "mode": network["runtime_contract"]["browser_network_mode"],
        "same_proxy_for_all_tasks": network["runtime_contract"]["same_proxy_endpoint_for_all_ten_tasks"],
        "pass": True,
    }
    checks["browser_network"] = probe_browser_proxy(resolve_browser_proxy(browser_proxy))

    awm_head = git_head(awm_root)
    awm_is_dirty = git_dirty(awm_root)
    checks["awm"] = {
        "path": str(awm_root.resolve()),
        "exists": awm_root.is_dir(),
        "head": awm_head,
        "expected_head": EXPECTED_AWM_COMMIT,
        "dirty": awm_is_dirty,
        "pass": awm_root.is_dir() and awm_head == EXPECTED_AWM_COMMIT and awm_is_dirty is False,
    }

    dataset_sha = sha256_file(dataset) if dataset.is_file() else None
    checks["browserart"] = {
        "path": str(browserart_root.resolve()),
        "materialized_commit_label": EXPECTED_BROWSERART_COMMIT,
        "dataset_path": str(dataset),
        "dataset_sha256": dataset_sha,
        "expected_dataset_sha256": EXPECTED_DATASET_SHA256,
        "pass": browserart_root.is_dir() and dataset_sha == EXPECTED_DATASET_SHA256,
    }

    generic_sha = sha256_file(generic_agent) if generic_agent.is_file() else None
    checks["generic_agent"] = {
        "path": str(generic_agent),
        "sha256": generic_sha,
        "expected_sha256": EXPECTED_GENERIC_AGENT_SHA256,
        "pass": generic_sha == EXPECTED_GENERIC_AGENT_SHA256,
    }

    atomcode = resolve_atomcode()
    version = None
    atomcode_sha = None
    if atomcode is not None and atomcode.is_file():
        atomcode_sha = sha256_file(atomcode)
        try:
            version = subprocess.check_output([str(atomcode), "--version"], text=True, stderr=subprocess.STDOUT, timeout=10).strip()
        except Exception as exc:
            version = f"ERROR:{type(exc).__name__}"
    checks["atomcode_binary"] = {
        "path": str(atomcode) if atomcode else None,
        "version": version,
        "sha256": atomcode_sha,
        "pass": atomcode is not None and atomcode.is_file() and bool(version) and not str(version).startswith("ERROR:"),
    }

    auth, auth_checked = find_auth(auth_path)
    # Deliberately record only existence/path. Never parse, hash, copy, or print credential bytes in preflight.
    checks["atomcode_auth"] = {
        "checked_paths": auth_checked,
        "selected_path": str(auth) if auth else None,
        "present": auth is not None,
        "credential_content_read": False,
        "pass": auth is not None,
    }

    structural_pass = all(checks[name]["pass"] for name in ("amendment", "browser_network_addendum", "awm", "browserart", "generic_agent", "atomcode_binary"))
    if not structural_pass:
        status = "PRE_DISPATCH_OPERATIONAL_HOLD_SUBSTRATE_OR_BINARY_MISMATCH"
        next_gate = "REPAIR_ZERO_REQUEST_PREFLIGHT"
    elif checks["browser_network"]["pass"] is not True:
        status = "PRE_DISPATCH_OPERATIONAL_HOLD_BROWSER_NETWORK_UNAVAILABLE"
        next_gate = "RESTORE_UNIFORM_BROWSER_PROXY_WITHOUT_CHANGING_TASK_CONTENT"
    elif auth is None:
        status = "PRE_DISPATCH_OPERATIONAL_HOLD_AUTH_MISSING"
        next_gate = "RESTORE_EXISTING_ATOMCODE_AUTH_WITHOUT_EXPOSING_SECRET"
    else:
        status = "ATOMCODE_AUTH_AND_TEXT_PROXY_ZERO_REQUEST_PREFLIGHT_PASS"
        next_gate = "FREEZE_SEPARATE_Q0_EXECUTION_AUTHORITY_BEFORE_ANY_MODEL_REQUEST"

    return {
        "schema_version": "g1-atomgit-q0-zero-request-preflight-v2",
        "artifact_id": "AGENT-SAFETY-G1-ATOMGIT-Q0-ZERO-REQUEST-PREFLIGHT-20260906",
        "paper_id": "AGENT-SAFETY-R9",
        "status": status,
        "recorded_time_ns": started,
        "host": os.uname().nodename,
        "checks": checks,
        "dispatch_attempted": False,
        "model_request_delta": 0,
        "model_request_delta_basis": "This preflight may issue ordinary HTTP reachability probes through the frozen uniform browser proxy, but no daemon live message, model request, BrowserART action, or provider inference endpoint is called.",
        "safety_calls": 0,
        "harmful_calls": 0,
        "scientific_outcome_created": False,
        "q0_execution_authorized": False,
        "p0_execution_authorized": False,
        "p1_execution_authorized": False,
        "next_gate": next_gate,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--amendment", type=Path, default=DEFAULT_AMENDMENT)
    parser.add_argument("--network-addendum", type=Path, default=DEFAULT_NETWORK_ADDENDUM)
    parser.add_argument("--awm-root", type=Path, default=DEFAULT_AWM)
    parser.add_argument("--browserart-root", type=Path, default=DEFAULT_BROWSERART)
    parser.add_argument("--auth-path", type=Path)
    parser.add_argument("--browser-proxy")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise PreflightError(f"refusing overwrite: {args.output}")
    result = preflight(amendment=args.amendment, network_addendum=args.network_addendum, awm_root=args.awm_root, browserart_root=args.browserart_root, auth_path=args.auth_path, browser_proxy=args.browser_proxy)
    atomic_json(args.output, result)
    print(json.dumps({
        "status": result["status"],
        "model_request_delta": result["model_request_delta"],
        "dispatch_attempted": result["dispatch_attempted"],
        "next_gate": result["next_gate"],
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
