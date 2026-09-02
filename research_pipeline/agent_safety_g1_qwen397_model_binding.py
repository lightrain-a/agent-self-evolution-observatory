from __future__ import annotations

import hashlib
import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from research_pipeline.agent_safety_g1_qwen397_capability_requal import (
    EXPERIMENT_ID,
    MODEL,
    PREREG_SHA,
    load_json,
    validate_prereg,
)

BASE_URL = "https://api.aa.com.cn/api/v1"
API_KEY_ENV = "AA_API_KEY"


class BindingError(RuntimeError):
    pass


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def atomic_bytes(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    raw = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    atomic_bytes(path, raw)


def _read_http_raw(
    request: urllib.request.Request,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
    timeout: float = 120.0,
) -> tuple[bytes, dict[str, str], int]:
    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read()
            headers = {str(k): str(v) for k, v in response.headers.items()}
            code = int(getattr(response, "status", 200))
            return raw, headers, code
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        raise BindingError(f"provider transport failure; no automatic retry:{type(exc).__name__}") from exc


def _safe_headers(headers: dict[str, str]) -> dict[str, str]:
    allow = {"date", "content-type", "x-request-id", "request-id", "cf-ray", "server"}
    return {k: v for k, v in headers.items() if k.lower() in allow}


def parse_model_ids(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if not isinstance(data, list):
        return []
    ids = []
    for row in data:
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            ids.append(row["id"])
    return sorted(set(ids))


def run_binding(
    *,
    prereg_path: Path,
    output_dir: Path,
    api_key: str,
    base_url: str = BASE_URL,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    prereg = load_json(prereg_path)
    errors = validate_prereg(prereg)
    if errors:
        raise BindingError("invalid capability prereg:" + ";".join(errors))
    if prereg.get("contract_sha256") != PREREG_SHA:
        raise BindingError("unexpected prereg digest")
    if not api_key.strip():
        raise BindingError(f"{API_KEY_ENV} is not configured")
    output_dir.mkdir(parents=True, exist_ok=True)
    catalog_raw_path = output_dir / "provider-models-response.raw.json"
    binding_raw_path = output_dir / "provider-binding-response.raw.json"
    receipt_path = output_dir / "model-binding-receipt.json"
    if any(path.exists() for path in (catalog_raw_path, binding_raw_path, receipt_path)):
        raise BindingError("refuse to overwrite an existing model-binding attempt")

    auth = {"Authorization": "Bearer " + api_key, "Accept": "application/json"}
    models_req = urllib.request.Request(base_url.rstrip("/") + "/models", headers=auth, method="GET")
    catalog_raw, catalog_headers, catalog_code = _read_http_raw(models_req, opener=opener)
    atomic_bytes(catalog_raw_path, catalog_raw)
    try:
        catalog = json.loads(catalog_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BindingError("persisted model catalog is not valid JSON; no retry") from exc
    model_ids = parse_model_ids(catalog)
    if MODEL not in model_ids:
        receipt = {
            "schema_version": "g1-qwen397-model-binding-v1",
            "experiment_id": EXPERIMENT_ID,
            "prereg_contract_sha256": PREREG_SHA,
            "status": "STOP_MODEL_BINDING",
            "reason": "REQUESTED_MODEL_ABSENT_FROM_CATALOG",
            "requested_model": MODEL,
            "returned_model": None,
            "base_url": base_url.rstrip("/"),
            "catalog_http_status": catalog_code,
            "catalog_sha256": sha256_bytes(catalog_raw),
            "catalog_safe_headers": _safe_headers(catalog_headers),
            "binding_request_executed": False,
            "api_key_persisted": False,
            "scientific_authority": False,
        }
        atomic_json(receipt_path, receipt)
        return receipt

    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Reply with exactly MODEL_BINDING_OK"}],
        "temperature": 0.1,
        "max_tokens": 16,
        "seed": 0,
        "enable_thinking": False,
    }
    binding_req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        headers={**auth, "Content-Type": "application/json"},
        method="POST",
    )
    binding_raw, binding_headers, binding_code = _read_http_raw(binding_req, opener=opener)
    atomic_bytes(binding_raw_path, binding_raw)
    try:
        response = json.loads(binding_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BindingError("persisted binding response is not valid JSON; no retry") from exc
    returned_model = response.get("model") if isinstance(response, dict) else None
    system_fingerprint = response.get("system_fingerprint") if isinstance(response, dict) else None
    status = "MODEL_BINDING_PASS" if returned_model == MODEL else "STOP_MODEL_BINDING"
    receipt = {
        "schema_version": "g1-qwen397-model-binding-v1",
        "experiment_id": EXPERIMENT_ID,
        "prereg_contract_sha256": PREREG_SHA,
        "status": status,
        "reason": None if status == "MODEL_BINDING_PASS" else "RETURNED_MODEL_MISMATCH_OR_MISSING",
        "requested_model": MODEL,
        "returned_model": returned_model,
        "system_fingerprint": system_fingerprint,
        "base_url": base_url.rstrip("/"),
        "catalog_http_status": catalog_code,
        "binding_http_status": binding_code,
        "catalog_sha256": sha256_bytes(catalog_raw),
        "binding_response_sha256": sha256_bytes(binding_raw),
        "catalog_safe_headers": _safe_headers(catalog_headers),
        "binding_safe_headers": _safe_headers(binding_headers),
        "catalog_contains_requested_model": True,
        "binding_request_executed": True,
        "provider_requests": {"catalog": 1, "binding_chat": 1},
        "capability_payload_compatibility": {"temperature": 0.1, "seed": 0, "enable_thinking": False},
        "api_key_persisted": False,
        "scientific_authority": False,
    }
    atomic_json(receipt_path, receipt)
    return receipt


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="G1 Qwen3.5-397B model-binding gate")
    parser.add_argument("--prereg", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", default=os.getenv("AA_BASE_URL", BASE_URL))
    args = parser.parse_args()
    api_key = os.getenv(API_KEY_ENV, "")
    receipt = run_binding(
        prereg_path=args.prereg,
        output_dir=args.output_dir,
        api_key=api_key,
        base_url=args.base_url,
    )
    print(json.dumps({
        "status": receipt["status"],
        "requested_model": receipt["requested_model"],
        "returned_model": receipt.get("returned_model"),
        "api_key_persisted": False,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
