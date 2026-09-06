from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from research_pipeline.agent_safety_g1_atomgit_q0_preflight import (
    DEFAULT_NETWORK_ADDENDUM,
    load_network_addendum,
    sha256_file,
)
from research_pipeline.agent_safety_g1_atomgit_q0_runner import (
    BROWSER_NETWORK_ADDENDUM_ID,
    BROWSER_NETWORK_MODE,
    ModelTextServer,
    browser_chromium_kwargs,
    validate_browser_runtime,
)
from research_pipeline.agent_safety_g1_qwen397_benign_runner import (
    atomic_json,
    configure_imports,
)

DEFAULT_AWM = Path("/data/wyt/agent-safety-discovery-20260818/substrate-assets-r9/agent-workflow-memory")
DEFAULT_BROWSERART = Path("/data/wyt/agent-safety-discovery-20260818/substrate-assets-r9/browser-art-pinned-0d72180042f2")
TASK_IDS = list(range(10))
MAX_STEPS = 10


class NetworkQualificationError(RuntimeError):
    pass


def qualify(*, awm_root: Path, browserart_root: Path, proxy: str, addendum_path: Path) -> dict[str, Any]:
    validate_browser_runtime()
    addendum = load_network_addendum(addendum_path)
    if addendum["artifact_id"] != BROWSER_NETWORK_ADDENDUM_ID:
        raise NetworkQualificationError("browser-network addendum identity drift")
    chromium_kwargs = browser_chromium_kwargs(proxy)
    configure_imports(awm_root, browserart_root)
    import gymnasium as gym

    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="g1-atomgit-q0-network-qualification-") as td:
        runtime_root = Path(td)
        for task_id in TASK_IDS:
            server = ModelTextServer(browserart_root, task_id, "qwen3.8-27b")
            env = None
            started = time.monotonic()
            try:
                episode_dir = runtime_root / f"task-{task_id}"
                episode_dir.mkdir()
                server.start(episode_dir)
                with contextlib.redirect_stdout(io.StringIO()):
                    env = gym.make(
                        f"browsergym/hbb_benign.{task_id}",
                        disable_env_checker=True,
                        max_episode_steps=MAX_STEPS,
                        headless=True,
                        wait_for_user_message=False,
                        pw_chromium_kwargs=chromium_kwargs,
                    )
                    obs, _ = env.reset(seed=0)
                page = env.unwrapped.page
                url = page.url if page is not None else ""
                rows.append(
                    {
                        "task_id": task_id,
                        "reset_pass": bool(obs) and page is not None and bool(url),
                        "observation_key_count": len(obs) if hasattr(obs, "keys") else -1,
                        "page_url_nonempty": bool(url),
                        "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
                    }
                )
            except BaseException as exc:
                rows.append(
                    {
                        "task_id": task_id,
                        "reset_pass": False,
                        "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
                        "error_class": type(exc).__name__,
                        "error": str(exc)[:500],
                    }
                )
            finally:
                if env is not None:
                    try:
                        env.close()
                    except Exception:
                        pass
                try:
                    server.stop()
                except Exception:
                    pass

    passed = sum(row["reset_pass"] is True for row in rows)
    result: dict[str, Any] = {
        "schema_version": "g1-atomgit-q0-browser-network-qualification-v1",
        "artifact_id": "AGENT-SAFETY-G1-ATOMGIT-Q0-BROWSER-NETWORK-QUALIFICATION-R4P2-20260906",
        "paper_id": "AGENT-SAFETY-R9",
        "status": "BROWSER_NETWORK_ZERO_MODEL_10_OF_10_PASS" if passed == len(TASK_IDS) else "BROWSER_NETWORK_ZERO_MODEL_QUALIFICATION_HOLD",
        "browser_network_mode": BROWSER_NETWORK_MODE,
        "browser_network_addendum_id": BROWSER_NETWORK_ADDENDUM_ID,
        "browser_network_addendum_sha256": sha256_file(addendum_path),
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "python_executable": str(Path(sys.executable)),
        "python_prefix": sys.prefix,
        "python_base_prefix": sys.base_prefix,
        "proxy_endpoint": proxy,
        "same_proxy_for_all_ten_tasks": True,
        "task_specific_proxy_override": False,
        "page_or_task_rewrite": False,
        "task_ids": TASK_IDS,
        "required_reset_pass_count": 10,
        "reset_pass_count": passed,
        "rows": rows,
        "provider_calls": 0,
        "model_requests": 0,
        "browser_actions": 0,
        "scientific_outcomes_observed": 0,
        "harmful_calls": 0,
        "q0_execution_authorized": False,
        "p0_execution_authorized": False,
        "p1_execution_authorized": False,
        "scientific_authority": False,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--awm-root", type=Path, default=DEFAULT_AWM)
    parser.add_argument("--browserart-root", type=Path, default=DEFAULT_BROWSERART)
    parser.add_argument("--network-addendum", type=Path, default=DEFAULT_NETWORK_ADDENDUM)
    parser.add_argument("--browser-proxy", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise NetworkQualificationError(f"refusing overwrite: {args.output}")
    result = qualify(
        awm_root=args.awm_root,
        browserart_root=args.browserart_root,
        proxy=args.browser_proxy,
        addendum_path=args.network_addendum,
    )
    atomic_json(args.output, result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "reset_pass_count": result["reset_pass_count"],
                "provider_calls": 0,
                "q0_execution_authorized": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
