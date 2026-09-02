from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import (
    OBJECT_ID,
    sha256_file,
    sha256_value,
)

PROVIDER_PROFILE = "AtomGit-qwen3.8-27b"
MODEL = "qwen3.8-27b"
CONTEXT_WINDOW = 262144
MAX_OUTPUT_TOKENS = 65536
RETRY_MAX_ATTEMPTS = 1
OUTPUT = Path("generated/agent-constraint-externality-codingplan-qwen38-mcp-provider-qualification-m1-20260902.json")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def jsonl_rows(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def build_files(root: Path, auth_source: Path) -> None:
    home = root / "atomhome"
    work = root / "work"
    home.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    os.chmod(home, 0o700)
    shutil.copy2(auth_source, home / "auth.toml")
    os.chmod(home / "auth.toml", stat.S_IRUSR | stat.S_IWUSR)
    server = root / "mcp_server.py"
    write(
        server,
        """import json,sys\n"
        "TOOLS=[{'name':'ping_a','description':'Return synthetic A','inputSchema':{'type':'object','properties':{},'required':[]}},{'name':'ping_b','description':'Return synthetic B','inputSchema':{'type':'object','properties':{},'required':[]}}]\n"
        "def send(x): print(json.dumps(x,separators=(',',':')),flush=True)\n"
        "for line in sys.stdin:\n"
        "  try:r=json.loads(line)\n"
        "  except Exception:continue\n"
        "  if 'id' not in r:continue\n"
        "  i=r['id'];m=r.get('method')\n"
        "  if m=='initialize':send({'jsonrpc':'2.0','id':i,'result':{'protocolVersion':r.get('params',{}).get('protocolVersion','2024-11-05'),'capabilities':{'tools':{}},'serverInfo':{'name':'ace','version':'1'}}})\n"
        "  elif m=='tools/list':send({'jsonrpc':'2.0','id':i,'result':{'tools':TOOLS}})\n"
        "  elif m=='tools/call':\n"
        "    n=r.get('params',{}).get('name');send({'jsonrpc':'2.0','id':i,'result':{'content':[{'type':'text','text':json.dumps({'ok':True,'tool':n})}],'isError':False}})\n"
        "  else:send({'jsonrpc':'2.0','id':i,'result':{}})\n""",
    )
    gate = root / "gate.py"
    audit = root / "gate-audit.jsonl"
    write(
        gate,
        """import json,sys\n"
        "try:p=json.load(sys.stdin)\n"
        "except Exception:p={}\n"
        "name=str(p.get('tool_name',''))\n"
        f"open({str(audit)!r},'a',encoding='utf-8').write(json.dumps({{'tool_name':name,'allowed':name.startswith('mcp__ace__')}})+'\\n')\n"
        "if name.startswith('mcp__ace__'):print(json.dumps({'action':'allow'}))\n"
        "else:print(json.dumps({'action':'block','reason':'ACE scientific harness permits only mcp__ace__* tools'}))\n""",
    )
    write(
        home / "mcp.json",
        json.dumps(
            {
                "mcpServers": {
                    "ace": {
                        "command": "/usr/bin/python3",
                        "args": [str(server)],
                        "timeout_ms": 5000,
                        "trust": True,
                        "autoApprove": ["ping_a", "ping_b"],
                    }
                }
            },
            sort_keys=True,
        ),
    )
    write(
        work / ".hooks.json",
        json.dumps(
            {
                "hooks": {
                    "ace-tool-gate": {
                        "event": "pre_tool_use",
                        "matcher": "*",
                        "command": f"/usr/bin/python3 {gate}",
                        "timeout_ms": 3000,
                    }
                }
            },
            sort_keys=True,
        ),
    )
    write(
        root / "config.toml",
        "\n".join(
            [
                f'default_provider="{PROVIDER_PROFILE}"',
                f'default_model="{PROVIDER_PROFILE}"',
                "auto_update=false",
                "lsp.enabled=false",
                "subagent.enabled=false",
                "tools.todo.enabled=false",
                "[provider_accounts.AtomGit]",
                'provider="openai"',
                'base_url="https://llm-api.atomgit.com/v1"',
                f'[models."{PROVIDER_PROFILE}"]',
                'account="AtomGit"',
                f'model="{MODEL}"',
                f"context_window={CONTEXT_WINDOW}",
                f"max_tokens={MAX_OUTPUT_TOKENS}",
                f"retry_max_attempts={RETRY_MAX_ATTEMPTS}",
                "[coding]",
                "max_rounds=3",
                "",
            ]
        ),
    )


def run(root: Path, auth_source: Path) -> dict[str, Any]:
    build_files(root, auth_source)
    env = dict(os.environ)
    env.update(
        {
            "ATOMCODE_HOME": str(root / "atomhome"),
            "ATOMCODE_TODO": "0",
            "ATOMCODE_REQUEST_USER_INPUT": "0",
            "ATOMCODE_MEMORY_TOOL": "0",
        }
    )
    command = [
        "atomcode",
        "--config",
        str(root / "config.toml"),
        "--provider",
        PROVIDER_PROFILE,
        "--ephemeral",
        "--no-telemetry",
        "--output-format",
        "jsonl",
        "-C",
        str(root / "work"),
        "-p",
        (
            "Synthetic provider qualification only. Call both available MCP tools "
            "mcp__ace__ping_a and mcp__ace__ping_b, preferably in parallel. Use no other "
            "tools. After both succeed, reply exactly MCP_NATIVE_OK."
        ),
    ]
    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
        env=env,
    )
    rows = jsonl_rows(completed.stdout)
    usage = [row for row in rows if row.get("type") == "usage"]
    starts = [row for row in rows if row.get("type") == "tool.started"]
    errors = [row for row in rows if row.get("type") == "error"]
    text = "".join(
        str(row.get("text", "")) for row in rows if row.get("type") == "message.delta"
    ).strip()
    audit_path = root / "gate-audit.jsonl"
    audit = jsonl_rows(audit_path.read_text(encoding="utf-8") if audit_path.exists() else "")
    tool_names = [str(row.get("name", "")) for row in starts]
    if completed.returncode != 0:
        raise RuntimeError(f"AtomCode MCP qualification exited {completed.returncode}")
    if errors:
        raise RuntimeError(f"AtomCode MCP qualification emitted error: {errors[-1]}")
    if set(tool_names) != {"mcp__ace__ping_a", "mcp__ace__ping_b"}:
        raise RuntimeError(f"Unexpected MCP tool calls: {tool_names}")
    if text != "MCP_NATIVE_OK":
        raise RuntimeError(f"Unexpected final message: {text!r}")
    if not audit or any(not row.get("allowed") for row in audit):
        raise RuntimeError(f"MCP qualification gate audit invalid: {audit}")
    started = next((row for row in rows if row.get("type") == "run.started"), {})
    if str(started.get("model")) != MODEL:
        raise RuntimeError(f"Resolved model drift: {started.get('model')}")
    payload: dict[str, Any] = {
        "schema_version": "ace-codingplan-qwen38-mcp-provider-qualification-m1-v1",
        "object_id": OBJECT_ID,
        "status": "CODINGPLAN_QWEN38_MCP_NATIVE_PROVIDER_QUALIFICATION_PASS",
        "provider_profile": PROVIDER_PROFILE,
        "resolved_model": MODEL,
        "context_window": CONTEXT_WINDOW,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "retry_max_attempts": RETRY_MAX_ATTEMPTS,
        "live_probe": {
            "codingplan_request_count": len(usage),
            "tool_started_names": tool_names,
            "all_executed_tools_passed_scientific_gate": True,
            "final_message": text,
            "usage": [
                {
                    "round": row.get("round"),
                    "request_id": row.get("request_id"),
                    "prompt_tokens": row.get("prompt_tokens", 0),
                    "completion_tokens": row.get("completion_tokens", 0),
                    "cached_tokens": row.get("cached_tokens", 0),
                }
                for row in usage
            ],
        },
        "harness": {
            "mcp_tool_prefix": "mcp__ace__",
            "pre_tool_gate_reads_tool_name_from_stdin_json": True,
            "all_non_ace_tools_denied": True,
            "todo_disabled": True,
            "request_user_input_disabled": True,
            "memory_tool_disabled": True,
            "official_atomcode_binary": True,
            "direct_gateway_auth_bypass": False,
        },
        "scientific_outcomes_observed": 0,
        "f0_authorized": False,
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--auth-source", type=Path, default=Path.home() / ".atomcode/auth.toml")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"Refusing overwrite: {args.output}")
    payload = run(args.runtime_root, args.auth_source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "model": MODEL,
                "codingplan_requests": payload["live_probe"]["codingplan_request_count"],
                "content_sha256": payload["content_sha256"],
                "file_sha256": sha256_file(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
