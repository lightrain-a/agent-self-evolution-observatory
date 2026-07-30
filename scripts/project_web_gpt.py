#!/usr/bin/env python3
"""Call the signed-in ChatGPT web UI inside the configured project.

Every new Oracle browser conversation is opened under
ORACLE_CHATGPT_PROJECT_URL rather than the ordinary ChatGPT home page.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

EXPECTED_HOST = os.getenv("EXPECTED_RESEARCH_HOST", "admin01-NF5468M5")
DEFAULT_ORACLE = "/root/bin/oracle-browser"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip().rstrip("\r")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask ChatGPT in the configured project through Oracle browser mode."
    )
    parser.add_argument("question", help="Prompt to send")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--file", action="append", default=[], help="File to attach; repeatable")
    parser.add_argument("--slug", default="agent-project-review", help="Oracle session slug")
    parser.add_argument("--model", default="", help="Optional ChatGPT browser model label")
    parser.add_argument("--timeout", type=int, default=300, help="Oracle timeout in seconds")
    parser.add_argument("--output", type=Path, help="Keep final answer at this path")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if socket.gethostname() != EXPECTED_HOST:
        raise SystemExit(
            f"Refusing to run outside {EXPECTED_HOST}; current host is {socket.gethostname()}"
        )

    project_root = Path(
        os.getenv("PROJECT_ROOT", "/home/wyt/code/agent-self-evolution-observatory")
    )
    load_env(project_root / ".env")
    project_url = os.getenv("ORACLE_CHATGPT_PROJECT_URL", "").strip()
    if not project_url:
        raise SystemExit("ORACLE_CHATGPT_PROJECT_URL is not configured in .env")

    output = args.output
    temporary = False
    if output is None:
        handle = tempfile.NamedTemporaryFile(prefix="project_web_gpt_", suffix=".md", delete=False)
        handle.close()
        output = Path(handle.name)
        output.unlink(missing_ok=True)
        temporary = True
    output.parent.mkdir(parents=True, exist_ok=True)

    oracle_bin = os.getenv("ORACLE_BROWSER_BIN", DEFAULT_ORACLE)
    command = [oracle_bin]
    # The /root/bin/oracle-browser wrapper already injects browser mode, the
    # CDP endpoint, and the current-model strategy. Duplicating those options
    # caused long runs to acquire conflicting ChatGPT tabs.
    if Path(oracle_bin).name != "oracle-browser":
        command += [
            "--engine", "browser",
            "--remote-chrome", os.getenv("ORACLE_REMOTE_CHROME", "127.0.0.1:9222"),
            "--browser-model-strategy", "current" if not args.model else "select",
        ]
    command += [
        "--chatgpt-url", project_url,
        "--browser-archive", "never",
        "--force",
        "--slug", args.slug,
        "--timeout", f"{max(60, args.timeout)}s",
        "--no-notify",
        "--write-output", str(output),
    ]
    if args.model:
        command += ["--model", args.model]
    for file_name in args.file:
        command += ["--file", file_name]
    command += ["-p", args.question.strip()]

    env = os.environ.copy()
    env.setdefault("DISPLAY", ":99")
    completed = subprocess.run(
        command,
        cwd=project_root,
        env=env,
        text=True,
        capture_output=True,
        timeout=max(90, args.timeout + 30),
        check=False,
    )
    if completed.returncode != 0:
        payload = {
            "ok": False,
            "project_url": project_url,
            "error": f"Oracle exited with {completed.returncode}",
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
        }
        print(json.dumps(payload, ensure_ascii=False) if args.json else payload["error"])
        return 1
    if not output.exists():
        raise SystemExit("Oracle succeeded but no output file was created")
    answer = output.read_text(encoding="utf-8").strip()
    payload = {"ok": True, "project_url": project_url, "answer": answer}
    print(json.dumps(payload, ensure_ascii=False) if args.json else answer)
    if temporary:
        output.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
