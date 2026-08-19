from __future__ import annotations

import json
import socket
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

from .paper_first_agent_safety_r9_f0_contract import sha_file
from .paper_first_agent_safety_r9_harmbench_server import MODEL_ID as HARMBENCH_MODEL_ID
from .paper_first_agent_safety_r9_harmbench_server import MODEL_REVISION as HARMBENCH_REVISION

QWEN_ID = "Qwen3-8B"
QWEN_REVISION = "b968826d9c46dd6066d109eabc6255188de91218"
QWEN_BASE_URL = "http://127.0.0.1:18000/v1"
HARMBENCH_HEALTH = "http://127.0.0.1:18001/health"
HARMBENCH_CLASSIFY = "http://127.0.0.1:18001/classify"
PROXY = "http://127.0.0.1:18888"
PROXY_BYPASS = "localhost,127.0.0.1,0.0.0.0"
LISTENER_PORT = 3000
PACKAGE_LOCK_SHA = "6d2fa41c0eb10bfae35e6e0e52899f149e73112cc34a506039915f6cd37104d4"
EXT = {"twitter": "txt", "review": "txt", "email": "json"}


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def http_json(url: str, payload: dict[str, Any] | None = None, timeout: float = 15) -> dict[str, Any]:
    if payload is None:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
    else:
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        req = urllib.request.Request(url, data=raw, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as res:
        require(int(getattr(res, "status", 0) or res.getcode()) == 200, f"HTTP status drift:{url}")
        return json.loads(res.read())


def verify_services() -> dict[str, Any]:
    qwen = http_json(QWEN_BASE_URL + "/models", timeout=8)
    rows = qwen.get("data") or []
    require(len(rows) == 1 and rows[0].get("id") == QWEN_ID, "Qwen model identity drift")
    require(QWEN_REVISION in str(rows[0].get("root") or ""), "Qwen revision/root drift")
    harm = http_json(HARMBENCH_HEALTH, timeout=8)
    require(harm.get("status") == "READY_HARMBENCH_TP2_SERVICE", "HarmBench not READY")
    require(harm.get("model_id") == HARMBENCH_MODEL_ID and harm.get("revision") == HARMBENCH_REVISION, "HarmBench identity drift")
    require(harm.get("tensor_parallel_size") == 2 and harm.get("temperature") == 0.0 and harm.get("max_tokens") == 1, "HarmBench contract drift")
    return {"qwen": rows[0], "harmbench": harm}


def port_open(port: int) -> bool:
    s = socket.socket(); s.settimeout(0.2)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def listener_path(browserart: Path, behavior: dict[str, Any], episode_id: str) -> Path:
    site = str(behavior["website"]).split(":")[-1]
    require(site in EXT, f"unsupported frozen website:{site}")
    return browserart / "src/websites/text_server/saved_logs" / f"{site}_behaviorID={int(behavior['id'])},llm={QWEN_ID},agent={episode_id}.{EXT[site]}"


def format_listener(path: Path, website: str) -> str:
    site = website.split(":")[-1]
    if site in ("twitter", "review"):
        return path.read_text(encoding="utf-8")
    if site == "email":
        rows = json.loads(path.read_text(encoding="utf-8"))
        require(isinstance(rows, list) and rows, "email listener output empty")
        return json.dumps(rows[0], ensure_ascii=False)
    raise RuntimeError(f"unsupported formatter:{site}")


def start_listener(browserart: Path, out: Path, behavior_id: int, episode_id: str):
    require(not port_open(LISTENER_PORT), "listener port already occupied")
    websites = browserart / "src/websites"
    require(sha_file(websites / "package-lock.json") == PACKAGE_LOCK_SHA, "BrowserART package-lock drift")
    (websites / "text_server/saved_logs").mkdir(parents=True, exist_ok=True)
    log = out / "listener-logs" / f"{episode_id}.log"; log.parent.mkdir(parents=True, exist_ok=True)
    handle = log.open("ab", buffering=0)
    proc = subprocess.Popen(
        ["node", "text_server/server.js", "--port=3000", f"--behavior_id={behavior_id}", f"--llm_name={QWEN_ID}", f"--agent_name={episode_id}"],
        cwd=websites, stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
    deadline = time.time() + 5
    while time.time() < deadline:
        if proc.poll() is not None:
            handle.close(); raise RuntimeError(f"listener exited rc={proc.returncode}")
        if port_open(LISTENER_PORT):
            return proc, handle
        time.sleep(0.1)
    proc.terminate(); handle.close(); raise RuntimeError("listener failed to bind")


def stop_listener(proc, handle) -> None:
    if proc is not None and proc.poll() is None:
        proc.terminate()
        try: proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait(timeout=3)
    if handle is not None: handle.close()
    require(not port_open(LISTENER_PORT), "listener port not released")


def wait_listener(path: Path, seconds: float = 5) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if path.exists() and path.stat().st_size > 0:
            time.sleep(0.15); return True
        time.sleep(0.1)
    return path.exists() and path.stat().st_size > 0


def classify(episode_id: str, behavior: dict[str, Any], text: str) -> tuple[int, str, dict[str, Any], int]:
    before = verify_services()["harmbench"]
    before_count = int(before.get("classifications") or 0)
    response = http_json(HARMBENCH_CLASSIFY, {
        "request_id": episode_id,
        "behavior": behavior.get("behavior") or "",
        "context": behavior.get("context") or "",
        "text_output": text,
    }, timeout=120)
    require(response.get("status") == "HARMBENCH_CLASSIFICATION_COMPLETE", "classification status drift")
    require(response.get("request_id") == episode_id, "classification request id drift")
    require(response.get("model_id") == HARMBENCH_MODEL_ID and response.get("revision") == HARMBENCH_REVISION, "classification identity drift")
    pred = response.get("prediction")
    require(isinstance(pred, int) and not isinstance(pred, bool) and pred in (0, 1), f"nonbinary prediction:{pred!r}")
    after = verify_services()["harmbench"]
    require(int(after.get("classifications") or 0) == before_count + 1, "classifier service counter did not advance exactly once")
    return int(pred), str(response.get("raw_label") or ""), response, before_count
