from __future__ import annotations

import argparse
import hashlib
import json
import pathlib


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(16 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compile_manifest(static_path: pathlib.Path, smoke_path: pathlib.Path) -> dict:
    static = load(static_path)
    smoke = load(smoke_path)
    if static.get("artifact_kind") != "pre-outcome-merged-policy-manifest":
        raise ValueError("static-artifact-kind")
    if static.get("status") != "STATIC_VALIDATED_PRE_OUTCOME_HF_MODEL":
        raise ValueError("static-not-validated")
    if static.get("environment_outcomes_read") is not False:
        raise ValueError("static-read-environment-outcomes")
    if smoke.get("artifact_kind") != "pre-outcome-vllm-smoke-receipt" or smoke.get("passed") is not True:
        raise ValueError("smoke-not-passed")
    if smoke.get("environment_outcomes_read") is not False:
        raise ValueError("smoke-read-environment-outcomes")
    if pathlib.Path(str(static.get("model_dir") or "")).resolve() != pathlib.Path(str(smoke.get("model_dir") or "")).resolve():
        raise ValueError("model-dir-mismatch")
    out = dict(static)
    out["status"] = "VALIDATED_PRE_OUTCOME_HF_MODEL"
    out["smoke"] = smoke
    out["validation_receipts"] = {
        "static_manifest_path": str(static_path),
        "static_manifest_sha256": sha(static_path),
        "vllm_smoke_path": str(smoke_path),
        "vllm_smoke_sha256": sha(smoke_path),
    }
    out["environment_outcomes_read"] = False
    out["scientific_authority"] = False
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--static", type=pathlib.Path, required=True)
    ap.add_argument("--smoke", type=pathlib.Path, required=True)
    ap.add_argument("--output", type=pathlib.Path, required=True)
    a = ap.parse_args()
    payload = compile_manifest(a.static, a.smoke)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = a.output.with_suffix(a.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(a.output)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
