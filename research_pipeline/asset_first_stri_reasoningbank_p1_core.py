"""Frozen ReasoningBank P1 primitives: provenance, Ark calls, and Docker agent."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import re
import subprocess
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkCompatibilityError,
    ArkReasoningBankClient,
    ArkReasoningBankSettings,
    CANONICAL_SECRET_FILE,
)

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_ROOT = Path("/data/wyt/agent-self-evolution-observatory/external/stri-reasoningbank-iclr2026")
OFFICIAL_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
FIXTURE_PATH = ROOT / "generated/asset-first-stri-reasoningbank-p1-task-fixtures-20260829.json"
CORRECTION_PATH = ROOT / "generated/asset-first-stri-reasoningbank-paper-config-correction-20260829.json"
RETRIEVAL_CERT_PATH = ROOT / "generated/asset-first-stri-reasoningbank-p1-retrieval-certificate-result-20260829.json"
CONFIG_PATH = OFFICIAL_ROOT / "third_party/src/minisweagent/config/extra/swebench.yaml"
AGENT_PATH = OFFICIAL_ROOT / "third_party/src/minisweagent/agents/default.py"
INSTRUCTION_PATH = OFFICIAL_ROOT / "third_party/src/minisweagent/memory/instruction.py"
SELECTION_PATH = OFFICIAL_ROOT / "third_party/src/minisweagent/memory/memory_management.py"
RUNNER_PATH = OFFICIAL_ROOT / "third_party/src/minisweagent/run/extra/swebench.py"
EXPECTED_HASHES = {
    FIXTURE_PATH: "adfa5aca503e3d8d07f4c5e0f86a03da6a58ffedf91ba9d1e9623ae8915d4114",
    CORRECTION_PATH: "ffff870b0bf874c65afb20464ec705cad61ef80712f893b5bc4e195d2480a071",
    RETRIEVAL_CERT_PATH: "b22f79d91e419a010e7e58e658feee424832fe091b506363269c6082e9549f34",
    CONFIG_PATH: "d8bcea20ceb4798a99661074535abd7ba7c188bd4cbc7bd2505eb7c48e54ea41",
    AGENT_PATH: "428a78335cbfb365ba8e6622effc8959104f08e8f32068727625bcb296da756c",
    INSTRUCTION_PATH: "08e11fbeac1ba9e20d1dafb20728be24194b56bdfea33f05f6a1220ae2cc9bae",
    SELECTION_PATH: "fe71285a878920d501013ab86b58ef12c9c08071ee0e690061774d5ff5588955",
    RUNNER_PATH: "8365112cd2dd2f3dbd74eff611b5d166530c6ddac4b09b674ae384da96531951",
}
MODEL = "deepseek-v4-pro-ga-260813"
BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
DOCKER_HOST = "unix:///run/user/1006/e1-reasoningbank-docker.sock"
PID_NAMESPACE = "host"
BASE_STATE_RULE = "exact_or_clean_tree_equivalent_descendant"
STEP_LIMIT = 250
COMMAND_TIMEOUT_SECONDS = 60
EVALUATOR_TIMEOUT_SECONDS = 1800
MAX_RETRIES = 2
MEMORY_PREFIX = (
    "\n\nBelow are some memory items that I accumulated from past interaction from "
    "the environment that may be helpful to solve the task. You can use it when you "
    "feel it's relevant. In each step, please first explicitly discuss if you want "
    "to use each memory item or not, and then take action.\n"
)
FORMAT_RE = re.compile(r"```bash\n(.*?)\n```", re.DOTALL)


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, payload: dict[str, Any]) -> str:
    out = copy.deepcopy(payload)
    out["payload_sha256"] = sha256_text(canonical_json(payload))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sha256_file(path)


def run_host(
    command: list[str], *, timeout: int | float, docker: bool = False,
    decode_errors: str = "strict",
) -> dict[str, Any]:
    env = os.environ.copy()
    if docker:
        env["DOCKER_HOST"] = DOCKER_HOST
    started = utcnow()
    try:
        completed = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            encoding="utf-8", errors=decode_errors,
            timeout=timeout, env=env, check=False,
        )
        return {
            "started_at_utc": started, "finished_at_utc": utcnow(),
            "returncode": completed.returncode, "output": completed.stdout or "",
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        return {
            "started_at_utc": started, "finished_at_utc": utcnow(),
            "returncode": None, "output": output, "timed_out": True,
        }


def verify_frozen_inputs() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256_file(path)
        checks[str(path)] = {"expected": expected, "actual": actual, "pass": actual == expected}
    commit = run_host(["git", "-C", str(OFFICIAL_ROOT), "rev-parse", "HEAD"], timeout=10)
    actual_commit = commit["output"].strip()
    checks["official_commit"] = {
        "expected": OFFICIAL_COMMIT, "actual": actual_commit,
        "pass": commit["returncode"] == 0 and actual_commit == OFFICIAL_COMMIT,
    }
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    checks["fixture_visibility"] = {
        "pass": all(
            row["visibility_invariant"]["evaluator_only_fields_never_enter_model_messages"]
            and not row["visibility_invariant"]["gold_patch_content_persisted_in_fixture"]
            for row in fixtures["fixtures"]
        )
    }
    if not all(bool(item["pass"]) for item in checks.values()):
        raise RuntimeError("frozen input verification failed")
    return checks


def load_config() -> dict[str, Any]:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    if config["agent"]["step_limit"] != STEP_LIMIT:
        raise RuntimeError("official step limit drift")
    if config["environment"]["timeout"] != COMMAND_TIMEOUT_SECONDS:
        raise RuntimeError("official environment timeout drift")
    return config


def load_instructions() -> dict[str, str]:
    tree = ast.parse(INSTRUCTION_PATH.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"SUCCESSFUL_SI", "FAILED_SI"}:
                    result[target.id] = ast.literal_eval(node.value)
    if set(result) != {"SUCCESSFUL_SI", "FAILED_SI"}:
        raise RuntimeError("official memory instructions not found")
    return result


def load_agent_default(field: str) -> Any:
    """Read an AgentConfig default from the frozen official implementation."""
    tree = ast.parse(AGENT_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != "AgentConfig":
            continue
        for item in node.body:
            if (
                isinstance(item, ast.AnnAssign)
                and isinstance(item.target, ast.Name)
                and item.target.id == field
                and item.value is not None
            ):
                return ast.literal_eval(item.value)
    raise RuntimeError(f"official AgentConfig default not found: {field}")


def render_timeout_observation(config: dict[str, Any], action: str, output: str) -> str:
    template = config["agent"].get("timeout_template") or load_agent_default("timeout_template")
    visible = Template(template).render(action={"action": action}, output=output)
    if not visible.strip():
        raise RuntimeError("official timeout observation rendered empty")
    return visible


def load_fixtures() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["fixtures"]


def render_messages(task: str, selected_memory: str = "") -> list[dict[str, str]]:
    config = load_config()
    system = Template(config["agent"]["system_template"]).render()
    if selected_memory:
        system += MEMORY_PREFIX + selected_memory
    user = Template(config["agent"]["instance_template"]).render(task=task)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def append_nonempty_assistant_message(
    messages: list[dict[str, str]], content: str,
) -> bool:
    """Keep provider-illegal empty assistant content out of replayed history."""
    if not content:
        return False
    messages.append({"role": "assistant", "content": content})
    return True


def safe_model_receipt(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "requested_model": result.get("requested_model"),
        "resolved_model": result.get("resolved_model"),
        "text": result.get("raw_text", result.get("text", "")),
        "usage": result.get("usage") or {},
        "transport_attempts": result.get("transport_attempts"),
        "response_id_sha256": sha256_text(str(result.get("response_id") or "")),
        "credential_material_present": False,
    }


def make_client() -> ArkReasoningBankClient:
    base = ArkReasoningBankSettings.from_env_file(CANONICAL_SECRET_FILE)
    if base.base_url.rstrip("/") != BASE_URL:
        raise RuntimeError(f"Ark base URL drift: {base.base_url}")
    return ArkReasoningBankClient(ArkReasoningBankSettings(
        api_key=base.api_key, base_url=BASE_URL, model=MODEL,
        timeout_seconds=120.0, max_retries=MAX_RETRIES,
    ))


@dataclass
class DockerRun:
    image: str
    base_commit: str
    run_id: str
    exact_base: bool = False

    def __post_init__(self) -> None:
        suffix = re.sub(r"[^a-z0-9_.-]+", "-", self.run_id.lower())[-70:]
        self.name = f"e1-rb-{suffix}-{uuid.uuid4().hex[:8]}"
        self.created = False

    def start(self) -> dict[str, Any]:
        inspect = run_host(
            ["docker", "image", "inspect", self.image, "--format", "{{json .RepoDigests}} {{.Architecture}}"],
            timeout=30, docker=True,
        )
        if inspect["returncode"] != 0:
            raise RuntimeError(f"frozen image unavailable: {self.image}")
        created = run_host([
            "docker", "create", "--platform", "linux/amd64",
            "--pid", PID_NAMESPACE, "--name", self.name,
            "--entrypoint", "sleep", self.image, "infinity",
        ], timeout=60, docker=True)
        if created["returncode"] != 0:
            raise RuntimeError(f"docker create failed: {created['output'][-800:]}")
        self.created = True
        started = run_host(["docker", "start", self.name], timeout=60, docker=True)
        if started["returncode"] != 0:
            raise RuntimeError(f"docker start failed: {started['output'][-800:]}")
        if not re.fullmatch(r"[0-9a-f]{40}", self.base_commit):
            raise RuntimeError("invalid frozen base commit")
        if self.exact_base:
            pre_normalization = self.exec(
                "git rev-parse HEAD && "
                f"git cat-file -e {self.base_commit}^{{commit}} && "
                f"git merge-base --is-ancestor {self.base_commit} HEAD && "
                "test -z \"$(git status --porcelain=v1 --untracked-files=all)\"",
                timeout=30,
            )
            if pre_normalization["returncode"] != 0:
                raise RuntimeError(
                    "Q4 exact-base normalization precondition failed: "
                    f"{pre_normalization['output'].strip()}"
                )
            normalization = self.exec(
                f"git reset --hard {self.base_commit}",
                timeout=30,
            )
            if normalization["returncode"] != 0:
                raise RuntimeError(
                    "Q4 exact-base normalization action failed: "
                    f"{normalization['output'].strip()}"
                )
            base_state = self.exec(
                f'test "$(git rev-parse HEAD)" = "{self.base_commit}" && '
                "test -z \"$(git status --porcelain=v1 --untracked-files=all)\" && "
                "git rev-parse HEAD",
                timeout=30,
            )
            if base_state["returncode"] != 0:
                raise RuntimeError(
                    "Q4 exact-base normalization postcondition failed: "
                    f"{base_state['output'].strip()}"
                )
            base_state["pre_normalization"] = pre_normalization
            base_state["normalization"] = normalization
            base_state["normalization_action"] = (
                "git reset --hard <frozen expected base commit>"
            )
            base_state["git_clean_invoked"] = False
            rule = "exact_base_after_preregistered_hard_reset"
        else:
            base_state = self.exec(
                "git rev-parse HEAD && "
                f"git cat-file -e {self.base_commit}^{{commit}} && "
                f"git merge-base --is-ancestor {self.base_commit} HEAD && "
                f"git diff --quiet {self.base_commit}..HEAD && "
                "test -z \"$(git status --porcelain=v1)\"",
                timeout=30,
            )
            if base_state["returncode"] != 0:
                raise RuntimeError(
                    "base state is not an exact or clean tree-equivalent descendant: "
                    f"{base_state['output'].strip()}"
                )
            rule = BASE_STATE_RULE
        base_state["expected_base_commit"] = self.base_commit
        base_state["observed_head"] = base_state["output"].strip()
        base_state["rule"] = rule
        return {"image_inspect": inspect, "base_commit_receipt": base_state}

    def exec(self, action: str, *, timeout: int | float = COMMAND_TIMEOUT_SECONDS) -> dict[str, Any]:
        return run_host([
            "docker", "exec", "--workdir", "/testbed",
            "--env", "PAGER=cat", "--env", "MANPAGER=cat", "--env", "LESS=-R",
            "--env", "PIP_PROGRESS_BAR=off", "--env", "TQDM_DISABLE=1",
            self.name, "bash", "-lc", action,
        ], timeout=timeout, docker=True)

    def close(self) -> None:
        if self.created:
            run_host(["docker", "rm", "-f", self.name], timeout=60, docker=True)
            self.created = False


def execute_agent(
    fixture: dict[str, Any], *, selected_memory: str, run_id: str,
    exact_base: bool = False,
) -> tuple[dict[str, Any], DockerRun]:
    task = fixture["model_visible"]["problem_statement"]
    config = load_config()
    messages = render_messages(task, selected_memory)
    client = make_client()
    container = DockerRun(
        fixture["image_pull_reference"],
        fixture["model_visible"]["base_commit"],
        run_id,
        exact_base=exact_base,
    )
    runtime_receipt = container.start()
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    exit_status, result, failure = "", "", None
    call_count = 0
    try:
        while True:
            if call_count >= STEP_LIMIT:
                exit_status = "LimitsExceeded"
                messages.append({"role": "user", "content": ""})
                break
            request = {
                "model": MODEL, "input": copy.deepcopy(messages),
                "temperature": 0.0, "store": True,
            }
            requests.append(request)
            try:
                response = client.create_response(
                    input_items=messages, model=MODEL, temperature=0.0,
                    max_output_tokens=None, store=True,
                )
            except ArkCompatibilityError as error:
                failure = {"failure_layer": "provider", **error.safe_receipt()}
                exit_status = "ArkCompatibilityError"
                break
            call_count += 1
            receipt = safe_model_receipt(response)
            responses.append(receipt)
            if receipt["resolved_model"] != MODEL:
                failure = {
                    "failure_layer": "provider_identity", "expected": MODEL,
                    "actual": receipt["resolved_model"],
                }
                exit_status = "ProviderIdentityDrift"
                break
            content = str(receipt["text"])
            assistant_message_recorded = append_nonempty_assistant_message(messages, content)
            parsed = FORMAT_RE.findall(content)
            if len(parsed) != 1:
                visible = Template(config["agent"]["format_error_template"]).render(actions=parsed)
                messages.append({"role": "user", "content": visible})
                actions.append({
                    "step": call_count, "type": "format_error",
                    "candidate_action_count": len(parsed),
                    "assistant_output_empty": not assistant_message_recorded,
                    "provider_status": receipt["status"],
                    "model_visible_observation": visible,
                })
                continue
            action = parsed[0].strip()
            output = container.exec(action)
            row = {
                "step": call_count, "type": "shell", "action": action,
                "started_at_utc": output["started_at_utc"],
                "finished_at_utc": output["finished_at_utc"],
                "returncode": output["returncode"], "timed_out": output["timed_out"],
                "raw_output": output["output"],
            }
            actions.append(row)
            if output["timed_out"]:
                visible = render_timeout_observation(config, action, output["output"])
                row["model_visible_observation"] = visible
                messages.append({"role": "user", "content": visible})
                continue
            lines = output["output"].lstrip().splitlines(keepends=True)
            if lines and lines[0].strip() in {
                "MINI_SWE_AGENT_FINAL_OUTPUT", "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT",
            }:
                result = "".join(lines[1:])
                exit_status = "Submitted"
                messages.append({"role": "user", "content": result})
                row["submission_marker"] = lines[0].strip()
                row["model_visible_observation"] = result
                break
            visible = Template(config["agent"]["action_observation_template"]).render(
                output={"returncode": output["returncode"], "output": output["output"]}
            )
            row["model_visible_observation"] = visible
            messages.append({"role": "user", "content": visible})
    except Exception as error:
        failure = {
            "failure_layer": "implementation", "error_type": type(error).__name__,
            "message": str(error),
        }
        exit_status = type(error).__name__
    patch = container.exec(
        "git -c core.fileMode=false diff --binary HEAD && git status --porcelain=v1",
        timeout=60,
    )
    trajectory = {
        "schema_version": 1, "run_id": run_id, "created_at_utc": utcnow(),
        "instance_id": fixture["instance_id"], "task_sha256": sha256_text(task),
        "model_visible_task": copy.deepcopy(fixture["model_visible"]),
        "selected_memory": selected_memory,
        "selected_memory_sha256": sha256_text(selected_memory),
        "provider": {
            "base_url": BASE_URL, "model": MODEL, "temperature": 0.0,
            "max_output_tokens": "omitted", "seed": "omitted", "top_p": "omitted",
            "max_retries": MAX_RETRIES,
        },
        "runtime": {
            "docker_host": DOCKER_HOST, "image": fixture["image_pull_reference"],
            "platform": "linux/amd64", "pid_namespace": PID_NAMESPACE,
            "base_state_rule": BASE_STATE_RULE,
            "environment_timeout_seconds": COMMAND_TIMEOUT_SECONDS,
            "step_limit": STEP_LIMIT,
            "cost_limit_usd": "official=3.0; not enforceable under Ark Plan",
            "receipt": runtime_receipt,
        },
        "exit_status": exit_status, "result": result, "failure": failure,
        "R1_model_visible_requests": requests, "model_responses": responses,
        "messages": messages, "R2_first_behavioral_decision": actions[0] if actions else None,
        "R3_actions": actions, "patch_and_status": patch,
        "resource_accounting": {
            "model_calls": call_count,
            "input_tokens": sum(int((x.get("usage") or {}).get("input_tokens", 0)) for x in responses),
            "output_tokens": sum(int((x.get("usage") or {}).get("output_tokens", 0)) for x in responses),
            "provider_transport_attempts": sum(int(x.get("transport_attempts") or 0) for x in responses),
        },
        "credential_material_present": False,
    }
    return trajectory, container
