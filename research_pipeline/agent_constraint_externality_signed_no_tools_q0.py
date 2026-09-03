from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
ATOMCODE = Path.home() / ".local/bin/atomcode"
AUTH = Path.home() / ".atomcode/auth.toml"
AUDIT = GENERATED / "agent-constraint-externality-atomcode-transport-isolation-audit-20260903.json"
OUTPUT = GENERATED / "agent-constraint-externality-signed-no-tools-json-action-q0-20260903.json"
MODEL_PROFILE = "AtomGit-mimo-v2.5-pro"
MODEL_ID = "mimo-v2.5-pro"
BASE_URL = "https://llm-api.atomgit.com/v1"
CONTEXT_WINDOW = 1_000_000
RETRY_MAX_ATTEMPTS = 1
EXPECTED_BINARY_SHA256 = "ac5ee62fa4c20d70ee4220bdbafa8081051dd717c29a0c0c95de630a989a2113"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified_audit() -> dict[str, Any]:
    payload = read_json(AUDIT)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError("Transport audit object mismatch.")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload)
    unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RuntimeError("Transport audit content hash mismatch.")
    if payload.get("next_authorized_action") != "RUN_NON_SCIENTIFIC_JSON_ACTION_TRANSPORT_Q0_ONLY":
        raise RuntimeError("Transport audit does not authorize Q0.")
    return payload


def isolated_config() -> str:
    return f'''default_provider = "{MODEL_PROFILE}"
default_model = "{MODEL_PROFILE}"
auto_update = false
auto_commit = false
[provider_accounts.AtomGit]
provider = "openai"
base_url = "{BASE_URL}"
[models."{MODEL_PROFILE}"]
account = "AtomGit"
model = "{MODEL_ID}"
context_window = {CONTEXT_WINDOW}
retry_max_attempts = {RETRY_MAX_ATTEMPTS}
system_prompt = "You are executing a deterministic JSON action protocol, not software engineering. Return only the requested JSON object. No markdown, no prose outside JSON."
[ui]
ai_session_naming = false
'''


def quota_summary() -> dict[str, Any] | None:
    for port in (13456, 13457):
        token_path = Path.home() / f".atomcode/daemon-{port}.json"
        if not token_path.is_file():
            continue
        try:
            token = str(read_json(token_path)["token"])
            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/codingplan/usage/summary",
                headers={"Authorization": "Bearer " + token},
            )
            with urllib.request.urlopen(request, timeout=3) as response:
                payload = json.load(response)
            window = payload.get("primary_window") or {}
            return {key: window.get(key) for key in ("used", "remaining", "limit", "next_reset_at")}
        except Exception:
            continue
    return None


def protocol_prompt(observations: list[dict[str, Any]]) -> str:
    schema = {
        "ACTION": {"status": "ACTION", "actions": [{"tool": "lookup|submit", "arguments": {}}]},
        "DONE": {"status": "DONE", "answer": "short string"},
    }
    state = {
        "goal": "Submit exactly the secret token returned by lookup(alpha), then finish.",
        "available_actions": {
            "lookup": {"arguments": {"key": "string"}, "semantics": "lookup(alpha) returns the secret token"},
            "submit": {"arguments": {"token": "string"}, "semantics": "succeeds only if token equals the previously observed secret"},
        },
        "observations": observations,
        "rules": [
            "Output exactly one JSON object and nothing else.",
            "Do not invent an observation.",
            "Do not submit a token until it has appeared in a lookup observation.",
            "Use status ACTION while another external action is needed.",
            "Use status DONE only after a submit observation says accepted=true.",
            "You have no host tools and no function tools; the external controller executes only JSON actions listed above.",
        ],
        "output_schema_examples": schema,
    }
    return "JSON ACTION PROTOCOL\n" + json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def call_model(*, atom_home: Path, config: Path, prompt: str) -> tuple[str, dict[str, Any]]:
    env = os.environ.copy()
    env.update({
        "ATOMCODE_HOME": str(atom_home),
        "ATOMCODE_AI_SESSION_NAMING": "0",
        "ATOMCODE_SUBAGENT": "0",
    })
    command = [
        str(ATOMCODE),
        "-p",
        prompt,
        "--provider",
        MODEL_PROFILE,
        "--model",
        MODEL_ID,
        "--config",
        str(config),
        "--ephemeral",
        "--no-tools",
        "--no-telemetry",
    ]
    completed = subprocess.run(
        command,
        cwd=atom_home,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"AtomCode Q0 request failed rc={completed.returncode}: {completed.stderr[-800:]}")
    text = completed.stdout.strip()
    if not text:
        raise RuntimeError("AtomCode Q0 returned empty stdout.")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Q0 output is not strict JSON: {text[:500]}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("Q0 output root must be an object.")
    return text, parsed


def validate_action(payload: dict[str, Any], observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if payload.get("status") != "ACTION":
        raise RuntimeError(f"Expected ACTION, got {payload.get('status')!r}.")
    actions = payload.get("actions")
    if not isinstance(actions, list) or not actions:
        raise RuntimeError("ACTION must contain a non-empty actions list.")
    new_obs: list[dict[str, Any]] = []
    for action in actions:
        if not isinstance(action, dict):
            raise RuntimeError("Action must be an object.")
        tool = action.get("tool")
        arguments = action.get("arguments")
        if not isinstance(arguments, dict):
            raise RuntimeError("Action arguments must be an object.")
        if tool == "lookup":
            if arguments != {"key": "alpha"}:
                raise RuntimeError(f"Unexpected lookup arguments: {arguments}")
            new_obs.append({"tool": "lookup", "arguments": arguments, "result": {"token": "B7-ACE-Q0"}})
        elif tool == "submit":
            observed_tokens = [
                row.get("result", {}).get("token")
                for row in [*observations, *new_obs]
                if row.get("tool") == "lookup"
            ]
            token = arguments.get("token")
            if token not in observed_tokens:
                raise RuntimeError("Model attempted submit before observing that token.")
            new_obs.append({"tool": "submit", "arguments": arguments, "result": {"accepted": token == "B7-ACE-Q0"}})
        else:
            raise RuntimeError(f"Unknown synthetic action: {tool!r}")
    return new_obs


def run_q0() -> dict[str, Any]:
    audit = verified_audit()
    if file_sha256(ATOMCODE) != EXPECTED_BINARY_SHA256:
        raise RuntimeError("Official AtomCode binary hash drifted before Q0.")
    if not AUTH.is_file():
        raise RuntimeError("AtomCode auth.toml is absent.")
    before = quota_summary()
    observations: list[dict[str, Any]] = []
    rounds: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="ace-signed-no-tools-q0-") as directory:
        root = Path(directory).resolve()
        atom_home = root / "atomcode-home"
        atom_home.mkdir()
        shutil.copy2(AUTH, atom_home / "auth.toml")
        os.chmod(atom_home / "auth.toml", 0o600)
        config = atom_home / "config.toml"
        config.write_text(isolated_config(), encoding="utf-8")
        done = False
        for round_index in range(1, 5):
            prompt = protocol_prompt(observations)
            raw, parsed = call_model(atom_home=atom_home, config=config, prompt=prompt)
            record: dict[str, Any] = {
                "round": round_index,
                "prompt_sha256": sha256_value(prompt),
                "raw_output_sha256": sha256_value(raw),
                "parsed_status": parsed.get("status"),
            }
            if parsed.get("status") == "DONE":
                if not any(row.get("tool") == "submit" and row.get("result", {}).get("accepted") is True for row in observations):
                    raise RuntimeError("Model declared DONE before accepted submit observation.")
                if set(parsed) - {"status", "answer"}:
                    raise RuntimeError("DONE contains undeclared keys.")
                record["action_count"] = 0
                rounds.append(record)
                done = True
                break
            if set(parsed) - {"status", "actions"}:
                raise RuntimeError("ACTION contains undeclared keys.")
            new_obs = validate_action(parsed, observations)
            record["action_count"] = len(new_obs)
            record["action_tools"] = [row["tool"] for row in new_obs]
            rounds.append(record)
            observations.extend(new_obs)
        if not done:
            raise RuntimeError("Q0 did not reach DONE within four signed model rounds.")
    after = quota_summary()
    submit_rows = [row for row in observations if row.get("tool") == "submit"]
    if not submit_rows or submit_rows[-1].get("result", {}).get("accepted") is not True:
        raise RuntimeError("Q0 did not complete the synthetic goal.")
    payload: dict[str, Any] = {
        "schema_version": "ace-signed-no-tools-json-action-q0-v1",
        "object_id": OBJECT_ID,
        "status": "SIGNED_NO_TOOLS_JSON_ACTION_Q0_PASS",
        "transport_id": "ATOMCODE_SIGNED_NO_TOOLS_JSON_ACTION_V1",
        "transport_audit_content_sha256": audit["content_sha256"],
        "provider": "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY",
        "model_profile": MODEL_PROFILE,
        "model_id": MODEL_ID,
        "atomcode_binary_sha256": file_sha256(ATOMCODE),
        "atomcode_no_tools": True,
        "model_visible_function_tool_count": 0,
        "mcp_mounted": False,
        "strict_json_parse_all_rounds": True,
        "synthetic_external_action_tools": ["lookup", "submit"],
        "synthetic_goal_completed": True,
        "signed_model_round_count": len(rounds),
        "rounds": rounds,
        "codingplan_window_before": before,
        "codingplan_window_after": after,
        "scientific_case_count": 0,
        "appworld_action_count": 0,
        "sq0_case_count": 0,
        "scientific_outcomes_observed": 0,
        "authority": {
            "transport_q0": False,
            "fresh_harness_capability_qualification": False,
            "new_sq0": False,
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
        },
        "interpretation": "The official signed CodingPlan binary can serve as a model-only backend with no model-visible native or MCP function tools while an external controller executes a strict JSON action protocol. This is transport evidence only and does not qualify the scientific harness or backbone.",
    }
    payload["content_sha256"] = sha256_value(payload)
    return payload


def main() -> None:
    payload = run_q0()
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "signed_model_round_count": payload["signed_model_round_count"],
        "synthetic_goal_completed": payload["synthetic_goal_completed"],
        "scientific_outcomes_observed": 0,
        "scientific_execution_authorized": False,
        "content_sha256": payload["content_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
