#!/usr/bin/env python3
"""R80 execution-realization wrapper for the frozen R72/R73 B1 experiment.

Scientific design and statistics remain exactly R72/R73.  The only runtime
amendment is a path-only migration from the historically shared MemRL checkout
(which now contains unrelated untracked temp files) to a clean worktree at the
same pinned commit.  The wrapper re-runs the R73 static preflight, verifies the
clean checkout against the parent manifest's revision / pinned files / split,
then delegates execution to the frozen R73 implementation.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib
from typing import Any

try:
    from . import failure_memory_semantic_control_r73 as r73
except ImportError:
    import failure_memory_semantic_control_r73 as r73  # type: ignore

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
STATUS = "R80_R72_R73_EXECUTION_AUTHORITY_USER_GRANTED_PATH_EQUIVALENT_SOURCE"


def load(p: pathlib.Path) -> dict[str, Any]:
    v = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v, dict):
        raise RuntimeError(f"not-object:{p}")
    return v


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def verify_clean_override(parent_manifest: dict[str, Any], clean_source: pathlib.Path) -> None:
    import subprocess
    e = parent_manifest["execution_manifest"]
    src = e["source"]
    if not clean_source.is_dir():
        raise RuntimeError("clean-source-missing")
    head = subprocess.check_output(["git", "-C", str(clean_source), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(clean_source), "status", "--porcelain"], text=True).strip()
    if head != src["revision"] or dirty:
        raise RuntimeError(f"clean-source-not-equivalent:{head}:{dirty}")
    for rel, expected in (src.get("pinned_source_file_sha256") or {}).items():
        got = sha(clean_source / rel)
        if got != expected:
            raise RuntimeError(f"pinned-source-file-drift:{rel}:{got}")
    split = clean_source / e["confirmatory_units"]["split"]
    if sha(split) != e["confirmatory_units"]["split_sha256"]:
        raise RuntimeError("validation-split-drift-under-path-migration")


def patch_source(manifest: dict[str, Any], clean_source: pathlib.Path) -> dict[str, Any]:
    m = json.loads(json.dumps(manifest))
    m["execution_manifest"]["source"]["checkout"] = str(clean_source)
    return m


def authority_check(auth: dict[str, Any], protocol: dict[str, Any], model_key: str) -> pathlib.Path:
    if not r73.valid(auth):
        raise RuntimeError("r80-authority-invalid")
    if auth.get("status") != STATUS or auth.get("paper_id") != PAPER_ID:
        raise RuntimeError("r80-authority-status-drift")
    if auth.get("protocol_receipt_sha256") != protocol.get("receipt_sha256"):
        raise RuntimeError("r80-authority-protocol-drift")
    if (auth.get("bindings") or {}).get("r80_execute_runner_sha256") != sha(pathlib.Path(__file__).resolve()):
        raise RuntimeError("r80-runner-binding-drift")
    a = auth.get("authority") or {}
    if a.get(f"{model_key}_execution") is not True:
        raise RuntimeError(f"{model_key}-execution-not-authorized")
    if a.get("analysis") is not False:
        raise RuntimeError("analysis-must-remain-closed-during-execution")
    if any(a.get(k) for k in ["PSMG", "L3", "paper_claim_change"]):
        raise RuntimeError("r80-authority-too-broad")
    clean = pathlib.Path(str((auth.get("execution_realization") or {}).get("clean_source_checkout") or ""))
    if not clean.is_absolute():
        raise RuntimeError("clean-source-path-not-absolute")
    return clean


def main() -> None:
    p = argparse.ArgumentParser()
    for x in ["protocol", "panel", "hold", "token-audit", "review", "r2-review", "qwen-manifest", "llama-manifest", "r54", "authority", "output-dir"]:
        p.add_argument("--" + x, type=pathlib.Path, required=True)
    p.add_argument("--model", choices=["qwen", "llama"], required=True)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--validate-only", action="store_true")
    a = p.parse_args()

    protocol, panel, hold, ta, rv, r2, qm, lm, r54, auth = map(
        load,
        [a.protocol, a.panel, a.hold, a.token_audit, a.review, a.r2_review,
         a.qwen_manifest, a.llama_manifest, a.r54, a.authority],
    )
    manifests = r73.static_preflight(
        protocol, panel, hold, ta, rv, r2, qm, lm, r54, a.r54.resolve()
    )
    clean = authority_check(auth, protocol, a.model)
    verify_clean_override(manifests[a.model], clean)
    manifests = {k: patch_source(v, clean) for k, v in manifests.items()}

    # Delegate all treatment rendering, exposure-boundary handling, retries,
    # terminal ledger semantics, and trace persistence to the frozen R73 code.
    if a.validate_only:
        r73.runtime_preflight(manifests[a.model])
        print(json.dumps({
            "status": "R80_PATH_EQUIVALENT_RUNTIME_PREFLIGHT_PASS",
            "model": a.model,
            "clean_source_checkout": str(clean),
            "source_revision": manifests[a.model]["execution_manifest"]["source"]["revision"],
            "protocol_receipt_sha256": protocol["receipt_sha256"],
            "execution_still_not_started": True,
        }, sort_keys=True))
        return

    records = r73.runtime_records(protocol, panel, r54)
    r73.execute_stage(
        a.model,
        protocol,
        panel,
        manifests[a.model],
        records,
        a.output_dir.resolve(),
        a.resume,
    )
    print(json.dumps({"status": "R80_DELEGATED_R73_STAGE_TERMINAL", "model": a.model}, sort_keys=True))


if __name__ == "__main__":
    main()
