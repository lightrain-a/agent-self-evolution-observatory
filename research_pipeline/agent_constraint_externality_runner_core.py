from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
PROVIDER_ID = "TYPICAL_TOKEN_OPENAI_RESPONSES_API"
DEFAULT_BASE_URL = "https://api.aa.com.cn/api/v1"
REQUESTED_MODEL = "qwen3.7-flash-2026-07-15"
ALLOWED_ALIAS = "qwen3.7-flash"
MAX_RETRIES = 0
MAX_TOOL_CALLS = 12
TERMINAL_EVENTS = {"COMPLETION", "FAILURE"}


class RunnerError(RuntimeError):
    pass


class DuplicateDispatchError(RunnerError):
    pass


class UnknownAfterDispatchError(RunnerError):
    pass


class ProviderCallError(RunnerError):
    pass


class MalformedToolCallError(RunnerError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_no_secret(value: Any) -> None:
    encoded = canonical_bytes(value).decode("utf-8", errors="ignore")
    forbidden = ("Bearer ", "sk-", os.getenv("AA_API_KEY", "") or "__UNSET__")
    if any(token != "__UNSET__" and token in encoded for token in forbidden):
        raise RunnerError("Secret-like material is forbidden in runner artifacts.")


@dataclass(frozen=True)
class EpisodeUnit:
    namespace: str
    key: tuple[str | int, ...]
    stage: str
    family_id: str
    arm: str | None = None
    branch: str | None = None
    seed: int | None = None
    repeat: int | None = None

    @property
    def unit_id(self) -> str:
        return self.namespace + ":" + "|".join(str(item) for item in self.key)

    def validate(self) -> None:
        if self.namespace == "capability":
            if len(self.key) != 3:
                raise RunnerError("Capability key must be (model_id, family_id, repeat).")
        elif self.namespace == "source":
            if len(self.key) != 2:
                raise RunnerError("Source key must be (family_id, source).")
        elif self.namespace == "probe":
            if len(self.key) != 4:
                raise RunnerError("Probe key must be (family_id, arm, branch, seed).")
        else:
            raise RunnerError(f"Unknown episode namespace: {self.namespace}")


@dataclass
class ProviderReceipt:
    response_id: str
    requested_model: str
    resolved_model: str
    provider: str
    base_url: str
    output: list[dict[str, Any]]
    usage: dict[str, Any] = field(default_factory=dict)
    capability_snapshot: dict[str, Any] = field(default_factory=dict)
    status: str = "completed"

    def safe_dict(self) -> dict[str, Any]:
        value = asdict(self)
        ensure_no_secret(value)
        return value


class Provider(Protocol):
    request_count: int

    def create_response(
        self,
        *,
        model: str,
        instructions: str,
        input_items: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        temperature: float,
    ) -> ProviderReceipt: ...


class AppendOnlyLedger:
    """Exactly-once episode ledger. A dispatch is never replayable."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def rows(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for number, line in enumerate(
            self.path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RunnerError(f"Malformed ledger row {number}.") from exc
            rows.append(row)
        return rows

    def _append(self, row: dict[str, Any]) -> None:
        ensure_no_secret(row)
        line = canonical_bytes(row) + b"\n"
        with self.path.open("ab", buffering=0) as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def states(self) -> dict[str, str]:
        states: dict[str, str] = {}
        for row in self.rows():
            unit_id = row["unit_id"]
            event = row["event"]
            if event == "DISPATCH":
                if unit_id in states:
                    raise DuplicateDispatchError(f"Duplicate dispatch: {unit_id}")
                states[unit_id] = "UNKNOWN_AFTER_DISPATCH"
            elif event in TERMINAL_EVENTS:
                if states.get(unit_id) != "UNKNOWN_AFTER_DISPATCH":
                    raise RunnerError(f"Terminal event without open dispatch: {unit_id}")
                states[unit_id] = event
            else:
                raise RunnerError(f"Unknown ledger event: {event}")
        return states

    def dispatch(
        self,
        unit: EpisodeUnit,
        *,
        prompt_sha256: str,
        snapshot_sha256: str,
        repair_sha256: str | None,
        requested_model: str,
        provider: str,
        base_url: str,
    ) -> None:
        unit.validate()
        if unit.unit_id in self.states():
            raise DuplicateDispatchError(
                f"Refusing automatic replay of dispatched unit {unit.unit_id}"
            )
        self._append({
            "schema_version": "ace-exactly-once-ledger-v1",
            "object_id": OBJECT_ID,
            "event": "DISPATCH",
            "unit_id": unit.unit_id,
            "unit": asdict(unit),
            "stage": unit.stage,
            "family_id": unit.family_id,
            "arm": unit.arm,
            "branch": unit.branch,
            "seed": unit.seed,
            "model_id": requested_model,
            "provider": provider,
            "prompt_sha256": prompt_sha256,
            "initial_snapshot_sha256": snapshot_sha256,
            "repair_sha256": repair_sha256,
            "base_url": base_url,
            "dispatch_timestamp_ns": time.time_ns(),
            "attempt": 1,
            "status": "DISPATCHED",
            "max_retries": MAX_RETRIES,
        })

    def complete(
        self, unit: EpisodeUnit, *, receipts: list[ProviderReceipt], result: dict[str, Any]
    ) -> None:
        if self.states().get(unit.unit_id) != "UNKNOWN_AFTER_DISPATCH":
            raise RunnerError("Completion requires exactly one open dispatch.")
        self._append({
            "schema_version": "ace-exactly-once-ledger-v1",
            "object_id": OBJECT_ID,
            "event": "COMPLETION",
            "unit_id": unit.unit_id,
            "provider_receipts": [receipt.safe_dict() for receipt in receipts],
            "result": result,
            "time_ns": time.time_ns(),
        })

    def fail(
        self,
        unit: EpisodeUnit,
        *,
        failure_class: str,
        message: str,
        receipts: list[ProviderReceipt],
    ) -> None:
        if self.states().get(unit.unit_id) != "UNKNOWN_AFTER_DISPATCH":
            raise RunnerError("Failure requires exactly one open dispatch.")
        self._append({
            "schema_version": "ace-exactly-once-ledger-v1",
            "object_id": OBJECT_ID,
            "event": "FAILURE",
            "unit_id": unit.unit_id,
            "failure_class": failure_class,
            "message": message[:500],
            "provider_receipts": [receipt.safe_dict() for receipt in receipts],
            "retry_attempted": False,
            "time_ns": time.time_ns(),
        })

    def assert_all_terminal(self, units: Iterable[EpisodeUnit]) -> None:
        states = self.states()
        missing = [unit.unit_id for unit in units if states.get(unit.unit_id) not in TERMINAL_EVENTS]
        if missing:
            raise UnknownAfterDispatchError(
                "Partial aggregate firewall: non-terminal units remain: " + ", ".join(missing)
            )


class TypicalResponsesClient:
    """OpenAI Responses-compatible client with one HTTP attempt per request."""

    request_count = 0

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout_seconds: float = 120.0,
        opener: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        if not api_key.strip():
            raise ProviderCallError("AA_API_KEY is not configured.")
        self._api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._opener = opener

    def create_response(
        self,
        *,
        model: str,
        instructions: str,
        input_items: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        temperature: float,
    ) -> ProviderReceipt:
        body = {
            "model": model,
            "instructions": instructions,
            "input": input_items,
            "tools": tools,
            "temperature": temperature,
            "store": False,
        }
        request = urllib.request.Request(
            self.base_url + "/responses",
            data=canonical_bytes(body),
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        self.request_count += 1
        try:
            with self._opener(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ProviderCallError(
                f"Provider transport failed without retry: {type(exc).__name__}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise ProviderCallError("Provider response JSON was malformed; no retry.") from exc
        output = payload.get("output")
        if not isinstance(output, list):
            raise ProviderCallError("Provider response lacked output list; no retry.")
        resolved = payload.get("model")
        if not isinstance(resolved, str) or not resolved:
            raise ProviderCallError("Provider response lacked resolved model identity.")
        return ProviderReceipt(
            response_id=str(payload.get("id", "")),
            requested_model=model,
            resolved_model=resolved,
            provider=PROVIDER_ID,
            base_url=self.base_url,
            output=output,
            usage=payload.get("usage") or {},
            capability_snapshot={
                "custom_function_tools": True,
                "responses_api": True,
                "temperature": temperature,
                "max_retries": MAX_RETRIES,
            },
            status=str(payload.get("status", "completed")),
        )


class FakeProvider:
    """Deterministic provider used only by M1 qualification."""

    def __init__(
        self,
        scripted_outputs: list[list[dict[str, Any]]],
        *,
        fail_at: int | None = None,
        resolved_model: str = REQUESTED_MODEL,
    ) -> None:
        self.scripted_outputs = list(scripted_outputs)
        self.fail_at = fail_at
        self.resolved_model = resolved_model
        self.request_count = 0

    def create_response(self, **kwargs: Any) -> ProviderReceipt:
        self.request_count += 1
        if self.fail_at == self.request_count:
            raise ProviderCallError("Synthetic transport failure; no retry.")
        if not self.scripted_outputs:
            raise ProviderCallError("Synthetic provider exhausted; no retry.")
        return ProviderReceipt(
            response_id=f"mock-{self.request_count}",
            requested_model=str(kwargs["model"]),
            resolved_model=self.resolved_model,
            provider="M1_FAKE_PROVIDER",
            base_url="mock://m1",
            output=self.scripted_outputs.pop(0),
            usage={"input_tokens": 1, "output_tokens": 1},
            capability_snapshot={
                "custom_function_tools": True,
                "responses_api": True,
                "temperature": kwargs["temperature"],
                "max_retries": MAX_RETRIES,
            },
        )


class ToolWorld(Protocol):
    @property
    def tools(self) -> list[dict[str, Any]]: ...

    def execute(self, name: str, arguments: dict[str, Any]) -> Any: ...


def function_calls(output: list[dict[str, Any]]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for item in output:
        if item.get("type") != "function_call":
            continue
        if not all(isinstance(item.get(key), str) for key in ("name", "arguments", "call_id")):
            raise MalformedToolCallError("Function call fields are malformed.")
        try:
            arguments = json.loads(item["arguments"])
        except json.JSONDecodeError as exc:
            raise MalformedToolCallError("Function call arguments are malformed JSON.") from exc
        if not isinstance(arguments, dict):
            raise MalformedToolCallError("Function call arguments must decode to an object.")
        calls.append({"name": item["name"], "arguments": arguments, "call_id": item["call_id"]})
    return calls


def run_episode(
    *,
    unit: EpisodeUnit,
    instruction: str,
    snapshot_sha256: str,
    repair_sha256: str | None,
    world: ToolWorld,
    provider: Provider,
    ledger: AppendOnlyLedger,
    model: str = REQUESTED_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    crash_after_dispatch: bool = False,
    result_evaluator: Callable[[], dict[str, Any]] | None = None,
    max_tool_calls: int = MAX_TOOL_CALLS,
) -> dict[str, Any]:
    dispatch_provider = str(getattr(provider, "provider_id", PROVIDER_ID))
    dispatch_base_url = str(getattr(provider, "base_url", base_url))
    ledger.dispatch(
        unit,
        prompt_sha256=sha256_value(instruction),
        snapshot_sha256=snapshot_sha256,
        repair_sha256=repair_sha256,
        requested_model=model,
        provider=dispatch_provider,
        base_url=dispatch_base_url,
    )
    if crash_after_dispatch:
        raise UnknownAfterDispatchError("Synthetic crash after durable dispatch.")
    receipts: list[ProviderReceipt] = []
    input_items: list[dict[str, Any]] = [{"role": "user", "content": instruction}]
    tool_calls = 0
    try:
        while True:
            receipt = provider.create_response(
                model=model,
                instructions=(
                    "Complete the task using tools. Preserve unrelated state. "
                    "When finished, return a concise completion message."
                ),
                input_items=input_items,
                tools=world.tools,
                temperature=0.0,
            )
            receipts.append(receipt)
            calls = function_calls(receipt.output)
            if not calls:
                result = {
                    "status": "COMPLETED",
                    "tool_call_count": tool_calls,
                    "provider_request_count": len(receipts),
                    "resolved_model": receipt.resolved_model,
                }
                if result_evaluator is not None:
                    result["evaluation"] = result_evaluator()
                ledger.complete(unit, receipts=receipts, result=result)
                return result
            input_items.extend(receipt.output)
            for call in calls:
                tool_calls += 1
                if tool_calls > max_tool_calls:
                    raise RunnerError("Tool-call cap exceeded.")
                output = world.execute(call["name"], call["arguments"])
                input_items.append({
                    "type": "function_call_output",
                    "call_id": call["call_id"],
                    "output": json.dumps(output, ensure_ascii=False, sort_keys=True),
                })
    except Exception as exc:
        ledger.fail(
            unit,
            failure_class=type(exc).__name__,
            message=str(exc),
            receipts=receipts,
        )
        raise


class DictionaryWorld:
    """M1-only mutable tool world."""

    def __init__(self, state: dict[str, Any] | None = None) -> None:
        self.state = dict(state or {})
        self._tools = [{
            "type": "function",
            "name": "set_value",
            "description": "Set one key to a JSON value.",
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}, "value": {}},
                "required": ["key", "value"],
                "additionalProperties": False,
            },
        }]

    @property
    def tools(self) -> list[dict[str, Any]]:
        return self._tools

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        if name != "set_value":
            raise MalformedToolCallError(f"Unknown tool: {name}")
        self.state[str(arguments["key"])] = arguments["value"]
        return {"ok": True}
