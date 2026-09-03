#!/usr/bin/env python3
"""R59: source-side native parser qualification for the frozen Llama executor replication.

This gate uses three frozen OSInteraction *training* tasks and observes only the
first model response after reset. It never opens any R54 validation unit and
never calls a terminal evaluator. The gate is syntactic/interface qualification:
all three responses must parse natively as non-empty executable actions under
the same system-prompt family used by the primary A/B runner.
"""
from __future__ import annotations

import argparse, hashlib, json, os, pathlib, socket, subprocess, sys, urllib.request
from datetime import datetime, timezone
from typing import Any

try:
    from . import failure_memory_memrl_utilization_r47 as r47
except ImportError:
    import failure_memory_memrl_utilization_r47 as r47  # type: ignore

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
MANIFEST_STATUS = "R59_LLAMA_EXECUTOR_REPLICATION_MANIFEST_FROZEN_PRE_PROBE"
AUTH_STATUS = "R59_LLAMA_PARSER_QUALIFICATION_AUTHORITY_FROZEN_PRE_PROBE"
PROBE_IDS = ["103", "256", "54"]
PASS_STATUS = "LLAMA_NATIVE_PARSER_QUALIFICATION_PASS_PRIMARY_STILL_SEALED"
HOLD_STATUS = "LLAMA_NATIVE_PARSER_QUALIFICATION_HOLD_PRIMARY_STILL_SEALED"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load(p: pathlib.Path) -> dict[str, Any]:
    v = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v, dict):
        raise RuntimeError(f"not-object:{p}")
    return v


def valid(v: dict[str, Any]) -> bool:
    x = v.get("receipt_sha256")
    return isinstance(x, str) and x == r47.digest({k: z for k, z in v.items() if k != "receipt_sha256"})


def preflight(manifest_path: pathlib.Path, authority_path: pathlib.Path, model_identity_path: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    m, a, ident = map(load, [manifest_path, authority_path, model_identity_path])
    if m.get("paper_id") != PAPER_ID or a.get("paper_id") != PAPER_ID:
        raise RuntimeError("R59-paper-id-drift")
    if m.get("status") != MANIFEST_STATUS or a.get("status") != AUTH_STATUS:
        raise RuntimeError("R59-status-drift")
    if not valid(m) or not valid(a) or not valid(ident):
        raise RuntimeError("R59-receipt-hash-drift")
    b = a.get("bindings") or {}
    checks = {
        "manifest_file_sha256": r47.sha(manifest_path),
        "model_identity_file_sha256": r47.sha(model_identity_path),
        "parser_runner_sha256": r47.sha(pathlib.Path(__file__).resolve()),
    }
    for k, observed in checks.items():
        if b.get(k) != observed:
            raise RuntimeError(f"R59-binding-drift:{k}")
    if [str(x) for x in (a.get("probe_ids") or [])] != PROBE_IDS:
        raise RuntimeError("R59-probe-id-drift")
    e = m.get("execution_manifest") or {}
    h, source = e.get("host") or {}, e.get("source") or {}
    if socket.gethostname() != h.get("logical_name"):
        raise RuntimeError("R59-host-drift")
    if pathlib.Path(sys.executable).resolve() != pathlib.Path(str(h.get("python") or "")).resolve():
        raise RuntimeError("R59-python-drift")
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise RuntimeError("R59-PYTHONDONTWRITEBYTECODE-drift")
    root = pathlib.Path(str(source.get("checkout") or ""))
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True).strip()
    if head != source.get("revision") or dirty:
        raise RuntimeError("R59-source-checkout-drift")
    split = root / str((e.get("source_build") or {}).get("split") or "")
    if r47.sha(split) != (e.get("source_build") or {}).get("split_sha256"):
        raise RuntimeError("R59-train-split-drift")
    data = load(split)
    if any(tid not in data for tid in PROBE_IDS):
        raise RuntimeError("R59-probe-missing")
    model = e.get("models", {}).get("llm", {})
    if ident.get("manifest_sha256") != model.get("artifact_manifest_sha256") or ident.get("root") != model.get("root"):
        raise RuntimeError("R59-model-identity-drift")
    model_root = pathlib.Path(str(ident.get("root") or ""))
    rows = list(ident.get("files") or [])
    if not model_root.is_dir() or len(rows) != int(ident.get("file_count") or -1):
        raise RuntimeError("R59-model-root-or-file-count-drift")
    canonical = hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if canonical != ident.get("manifest_sha256"):
        raise RuntimeError("R59-model-manifest-digest-drift")
    for row in rows:
        fp = model_root / str(row.get("path") or "")
        if not fp.is_file() or fp.stat().st_size != int(row.get("bytes") or -1) or r47.sha(fp) != row.get("sha256"):
            raise RuntimeError(f"R59-model-file-drift:{row.get('path')}")
    base = str((e.get("external_runtime_adapter") or {}).get("loopback_base_url") or "").rstrip("/")
    with urllib.request.urlopen(base + "/models", timeout=5) as rr:
        models = {str(x.get("id")) for x in json.loads(rr.read().decode()).get("data") or []}
    if str((e.get("external_runtime_adapter") or {}).get("llm_model_id")) not in models:
        raise RuntimeError("R59-loopback-route-drift")
    return m, data


def first_response(manifest: dict[str, Any], task_id: str) -> dict[str, Any]:
    e = manifest["execution_manifest"]
    root = pathlib.Path(e["source"]["checkout"])
    llb = root / "3rdparty" / "LifelongAgentBench"
    if str(root) not in sys.path: sys.path.insert(0, str(root))
    if str(llb) not in sys.path: sys.path.insert(0, str(llb))
    from memrl.lifelongbench_eval.prompts import DEFAULT_SYSTEM_PROMPT, build_llb_prompt_with_memory
    from memrl.lifelongbench_eval.task_wrappers import build_task
    from src.agents.instance.language_model_agent import LanguageModelAgent
    from src.tasks.instance.os_interaction.task import OSInteraction
    from src.tasks.task import AgentAction
    from src.typings import Session

    adapter = r47.build_adapter(manifest)
    prompt = build_llb_prompt_with_memory(task="os", base_prompt=DEFAULT_SYSTEM_PROMPT, memory_context="")
    agent = LanguageModelAgent(language_model=adapter, system_prompt=prompt)
    task, tname = build_task(
        task="os",
        data_file_path=str(root / e["source_build"]["split"]),
        max_round=int(e["source_build"]["max_steps"]),
        os_timeout=int(e["source_build"]["os_timeout_seconds"]),
    )
    session = Session(task_name=tname, sample_index=task_id)
    try:
        task.reset(session)
        agent.inference(session)
        response = str(session.chat_history.get_item_deep_copy(-1).content or "")
        parsed = OSInteraction._parse_agent_response(response)
        normalized = r47.norm_action(parsed.content if parsed.action == AgentAction.EXECUTE else None)
        return {
            "task_id": task_id,
            "response": response,
            "response_sha256": hashlib.sha256(response.encode()).hexdigest(),
            "parsed_action": str(parsed.action),
            "parsed_content": parsed.content,
            "normalized_executable_action": normalized,
            "native_execute_nonempty": bool(parsed.action == AgentAction.EXECUTE and normalized),
        }
    finally:
        try: task.release()
        except Exception: pass


def main() -> None:
    p = argparse.ArgumentParser()
    for x in ["manifest", "authorization", "model-identity", "output-dir"]:
        p.add_argument("--" + x, type=pathlib.Path, required=True)
    a = p.parse_args(); out = a.output_dir.resolve()
    if out.exists():
        raise RuntimeError("R59-output-already-exists-no-second-probe-attempt")
    out.mkdir(parents=True)
    m, _ = preflight(a.manifest.resolve(), a.authorization.resolve(), a.model_identity.resolve())
    rows = []
    for tid in PROBE_IDS:
        rows.append(first_response(m, tid))
    passed = all(row["native_execute_nonempty"] for row in rows)
    result = {
        "schema_version": "1.0", "paper_id": PAPER_ID,
        "role": "R59_LLAMA_SOURCE_SIDE_NATIVE_PARSER_QUALIFICATION",
        "recorded_at": now(), "status": PASS_STATUS if passed else HOLD_STATUS,
        "probe_ids": PROBE_IDS, "probe_count": len(rows), "native_execute_nonempty_count": sum(bool(x["native_execute_nonempty"]) for x in rows),
        "pass": passed, "probe_rows": rows,
        "validation_environment_resets": 0, "validation_treatment_outcomes_observed": 0,
        "terminal_evaluator_calls": 0, "external_provider_calls": 0,
        "next_action": "OPEN_R60_LLAMA_UTILIZATION" if passed else "STOP_THIS_BACKBONE_WITHOUT_PRIMARY_EXPOSURE",
        "scientific_authority": False,
    }
    result["receipt_sha256"] = r47.digest(result)
    (out / "parser-qualification-receipt.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "native_execute_nonempty_count": result["native_execute_nonempty_count"], "validation_treatment_outcomes_observed": 0, "receipt_sha256": result["receipt_sha256"]}, sort_keys=True))


if __name__ == "__main__": main()
