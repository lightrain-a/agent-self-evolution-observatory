#!/usr/bin/env python3
"""Execute the prospective B1 MemRL R53 full-350 source-build phase.

R53 is a fresh scientific lineage after the R51 support stop.  It does not
resume, append to, or reuse the R45-M1 memory bank.  It preserves the already
qualified host/model/runtime substrate while expanding the source universe to
all 350 tasks in the frozen training split and retaining the transaction
semantics that the upstream LLBRunner does not provide by itself:

* exact preregistered source-ID order rather than the runner's sorted key order;
* batch_size=1 with fail-closed single-unit execution;
* one durable memory snapshot and completed-ID ledger row after every source
  memory write;
* no skipped/replaced source unit after an execution or memory-write failure.

Validation and confirmatory units are never opened by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import socket
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from typing import Any

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
EXPECTED_MANIFEST_STATUS = "MEMRL_R53_FULL350_SOURCE_EXECUTION_MANIFEST_FROZEN_ZERO_VALIDATION_OUTCOMES"
EXPECTED_AUTH_STATUS = "HUMAN_BOUNDED_R53_FULL350_SOURCE_EXECUTION_AUTHORITY_RECORDED"
API_KEY = "local-b1-r43"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object:{path}")
    return value


def _sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _append_jsonl(path: pathlib.Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def _verify_receipt_hash(payload: dict[str, Any], key: str = "receipt_sha256") -> bool:
    observed = payload.get(key)
    if not isinstance(observed, str) or len(observed) != 64:
        return False
    return observed == _digest({k: v for k, v in payload.items() if k != key})


def _materialize_full350_ids(dataset: dict[str, Any], source_build: dict[str, Any]) -> list[str]:
    seed = str(source_build.get("selection_seed_string") or "")
    if seed != "B1-R43-SOURCE-20260829":
        raise RuntimeError("r53-source-selection-seed-drift")
    selected = sorted(
        (str(key) for key in dataset.keys()),
        key=lambda key: hashlib.sha256(f"{seed}|{key}".encode()).hexdigest(),
    )
    if len(selected) != 350 or len(set(selected)) != 350:
        raise RuntimeError("r53-full-source-universe-drift")
    selected_ids_sha256 = hashlib.sha256("\n".join(selected).encode()).hexdigest()
    if selected_ids_sha256 != source_build.get("selected_ids_sha256"):
        raise RuntimeError("source-selected-id-hash-drift")
    return selected


def _verify_model_identity(model_identity: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {}
    models = manifest["execution_manifest"]["models"]
    for kind in ("llm", "embedding"):
        evidence = model_identity.get(kind) or {}
        frozen = models.get(kind) or {}
        if evidence.get("manifest_sha256") != frozen.get("artifact_manifest_sha256"):
            raise RuntimeError(f"{kind}-manifest-drift")
        root = pathlib.Path(str(evidence.get("root") or ""))
        if root != pathlib.Path(str(frozen.get("root") or "")) or not root.is_dir():
            raise RuntimeError(f"{kind}-root-drift")
        bad: list[str] = []
        total = 0
        for row in evidence.get("files") or []:
            target = root / str(row.get("path") or "")
            if not target.is_file():
                bad.append(str(row.get("path") or ""))
                continue
            size = target.stat().st_size
            total += size
            if size != int(row.get("bytes") or -1) or _sha(target) != row.get("sha256"):
                bad.append(str(row.get("path") or ""))
        if bad:
            raise RuntimeError(f"{kind}-file-drift:" + ",".join(bad[:5]))
        report[kind] = {
            "root": str(root),
            "file_count": len(evidence.get("files") or []),
            "bytes": total,
            "manifest_sha256": evidence.get("manifest_sha256"),
        }
    return report


def _preflight(
    manifest_path: pathlib.Path,
    auth_path: pathlib.Path,
    model_identity_path: pathlib.Path,
    outdir: pathlib.Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = _load(manifest_path)
    auth = _load(auth_path)
    model_identity = _load(model_identity_path)
    if manifest.get("paper_id") != PAPER_ID or auth.get("paper_id") != PAPER_ID:
        raise RuntimeError("paper-id-drift")
    if manifest.get("status") != EXPECTED_MANIFEST_STATUS or not _verify_receipt_hash(manifest):
        raise RuntimeError("r45m1-migration-manifest-invalid")
    if auth.get("status") != EXPECTED_AUTH_STATUS or not _verify_receipt_hash(auth):
        raise RuntimeError("execution-authorization-invalid")
    bindings = auth.get("bindings") or {}
    bound = bindings.get("source_manifest") or {}
    if bound.get("sha256") != _sha(manifest_path) or bound.get("receipt_sha256") != manifest.get("receipt_sha256"):
        raise RuntimeError("authorization-source-manifest-binding-drift")
    runner_bound = bindings.get("source_runner") or {}
    if runner_bound.get("sha256") != _sha(pathlib.Path(__file__).resolve()):
        raise RuntimeError("authorization-source-runner-binding-drift")
    authority = auth.get("authority") or {}
    if authority.get("execution") is not True or authority.get("local_gpu") is not True or authority.get("external_provider_spend") is not False:
        raise RuntimeError("execution-authority-not-bounded")

    lineage = auth.get("lineage") or {}
    replacement_limits = auth.get("replacement_limits") or {}
    pre_accounting = auth.get("pre_authority_accounting") or {}
    if lineage.get("replacement") != "R53-FULL350" or lineage.get("resume_of_old_r45") is not False:
        raise RuntimeError("r53-lineage-drift")
    if replacement_limits.get("old_r45_remote_access") is not False or replacement_limits.get("old_r45_artifact_reuse") is not False:
        raise RuntimeError("old-r45-quarantine-drift")
    if replacement_limits.get("partial_effect_inspection") is not False:
        raise RuntimeError("partial-effect-inspection-authorized")
    if any(int(pre_accounting.get(key) or 0) != 0 for key in ("scientific_source_units_executed", "validation_units_opened", "confirmatory_outcomes_observed")):
        raise RuntimeError("pre-authority-outcome-exposure")
    source_scope = (auth.get("authorized_scope") or {}).get("source_build") or {}
    if source_scope.get("authorized") is not True or int(source_scope.get("count") or 0) != 1 or int(source_scope.get("exact_selected_source_tasks") or 0) != 350:
        raise RuntimeError("r53-source-scope-drift")
    if source_scope.get("source_selection_sha256") != "a8b8f519e41522d4222e5cadde214b5c7318b7c307a620fbd0c8c9827c0443f4":
        raise RuntimeError("r53-authority-source-selection-drift")

    execution = manifest.get("execution_manifest") or {}
    host = execution.get("host") or {}
    source = execution.get("source") or {}
    source_build = execution.get("source_build") or {}
    if socket.gethostname() != host.get("logical_name"):
        raise RuntimeError(f"host-drift:{socket.gethostname()}!={host.get('logical_name')}")
    if pathlib.Path(sys.executable).resolve() != pathlib.Path(str(host.get("python") or "")).resolve():
        raise RuntimeError("python-executable-drift")
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        raise RuntimeError("PYTHONDONTWRITEBYTECODE-must-be-1")
    runtime_site = pathlib.Path(str(host.get("pythonpath") or ""))
    if not runtime_site.is_dir() or str(runtime_site) not in sys.path:
        raise RuntimeError("runtime-site-not-active")
    runtime_manifest = runtime_site.parent / "python-runtime-manifest.json"
    if not runtime_manifest.is_file() or _sha(runtime_manifest) != host.get("runtime_manifest_file_sha256"):
        raise RuntimeError("runtime-manifest-file-drift")
    runtime_payload = _load(runtime_manifest)
    if runtime_payload.get("tree_sha256") != host.get("runtime_tree_sha256") or runtime_payload.get("manifest_sha256") != host.get("runtime_manifest_sha256"):
        raise RuntimeError("runtime-tree-drift")

    source_root = pathlib.Path(str(source.get("checkout") or ""))
    if not source_root.is_dir() or _git(source_root, "rev-parse", "HEAD") != source.get("revision"):
        raise RuntimeError("source-revision-drift")
    if _git(source_root, "status", "--porcelain"):
        raise RuntimeError("source-checkout-dirty")
    for rel, expected in (source.get("pinned_source_file_sha256") or {}).items():
        path = source_root / rel
        if not path.is_file() or _sha(path) != expected:
            raise RuntimeError(f"source-file-drift:{rel}")

    split_path = source_root / str(source_build.get("split") or "")
    if not split_path.is_file() or _sha(split_path) != source_build.get("split_sha256"):
        raise RuntimeError("source-split-drift")
    dataset = _load(split_path)
    selected = _materialize_full350_ids(dataset, source_build)
    # Materialize the frozen deterministic order only in memory.  The signed
    # manifest freezes the split hash, seed, count, and ordered-ID digest; this
    # avoids a manually transcribed 350-ID list while preserving exact replay.
    source_build["selected_ids"] = selected

    docker_id = subprocess.check_output(
        ["docker", "image", "inspect", str((execution.get("runtime_image") or {}).get("execution_tag")), "--format", "{{.Id}}"],
        text=True,
    ).strip()
    if docker_id != (execution.get("runtime_image") or {}).get("id"):
        raise RuntimeError("runtime-image-id-drift")

    adapter = execution.get("external_runtime_adapter") or {}
    with urllib.request.urlopen(str(adapter.get("loopback_base_url") or "").rstrip("/") + "/models", timeout=5) as response:
        models_payload = json.loads(response.read().decode("utf-8"))
    model_ids = {str(row.get("id")) for row in models_payload.get("data") or []}
    if {str(adapter.get("llm_model_id")), str(adapter.get("embedding_model_id"))} - model_ids:
        raise RuntimeError("loopback-model-route-drift")

    model_report = _verify_model_identity(model_identity, manifest)
    preflight = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "role": "R53_FULL350_SOURCE_EXECUTION_PREFLIGHT_ZERO_VALIDATION_OUTCOME",
        "recorded_at": _now(),
        "source_manifest_receipt_sha256": manifest.get("receipt_sha256"),
        "authorization_receipt_sha256": auth.get("receipt_sha256"),
        "source_revision": source.get("revision"),
        "source_split_sha256": source_build.get("split_sha256"),
        "selected_ids_sha256": source_build.get("selected_ids_sha256"),
        "selected_count": len(selected),
        "runtime_tree_sha256": host.get("runtime_tree_sha256"),
        "runtime_manifest_sha256": host.get("runtime_manifest_sha256"),
        "runtime_image_id": docker_id,
        "model_identity": model_report,
        "loopback_model_ids": sorted(model_ids),
        "confirmatory_outcomes_observed": 0,
        "scientific_authority": False,
    }
    preflight["receipt_sha256"] = _digest({k: v for k, v in preflight.items() if k != "receipt_sha256"})
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "preflight.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest, auth, preflight


def _build_service_and_runner(manifest: dict[str, Any], outdir: pathlib.Path):
    execution = manifest["execution_manifest"]
    source_build = execution["source_build"]
    source_root = pathlib.Path(execution["source"]["checkout"])
    # Import the exact source checkout already verified by _preflight.  The
    # frozen runtime site provides third-party dependencies; MemRL itself is
    # intentionally executed from its pinned, clean source tree rather than
    # copied into or installed over that runtime.
    source_root_text = str(source_root)
    if source_root_text not in sys.path:
        sys.path.insert(0, source_root_text)
    split_path = source_root / source_build["split"]
    adapter = execution["external_runtime_adapter"]
    base_url = adapter["loopback_base_url"]
    llm_model = adapter["llm_model_id"]
    embed_model = adapter["embedding_model_id"]

    runtime_dir = outdir / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    mos = {
        "chat_model": {
            "backend": "openai",
            "config": {"model_name_or_path": llm_model, "api_key": API_KEY, "api_base": base_url},
        },
        "mem_reader": {
            "backend": "simple_struct",
            "config": {
                "llm": {
                    "backend": "openai",
                    "config": {"model_name_or_path": llm_model, "api_key": API_KEY, "api_base": base_url},
                },
                "embedder": {
                    "backend": "universal_api",
                    "config": {
                        "provider": "openai",
                        "model_name_or_path": embed_model,
                        "api_key": API_KEY,
                        "base_url": base_url,
                    },
                },
                "chunker": {
                    "backend": "sentence",
                    "config": {
                        "tokenizer_or_token_counter": "character",
                        "chunk_size": 500,
                        "chunk_overlap": 128,
                        "min_sentences_per_chunk": 1,
                    },
                },
            },
        },
        "user_manager": {"backend": "sqlite", "config": {"db_path": str(runtime_dir / "users.db")}},
        "top_k": 5,
    }
    mos_path = runtime_dir / "mos_config.json"
    mos_path.write_text(json.dumps(mos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    from memrl.providers.embedding import OpenAIEmbedder
    from memrl.providers.llm import OpenAILLM
    from memrl.run.llb_rl_runner import LLBRunner
    from memrl.service.memory_service import MemoryService
    from memrl.service.strategies import BuildStrategy, RetrieveStrategy, StrategyConfiguration, UpdateStrategy
    from memrl.service.value_driven import RLConfig

    llm = OpenAILLM(
        api_key=API_KEY,
        base_url=base_url,
        model=llm_model,
        default_temperature=0.0,
        default_max_tokens=512,
        provider="openai",
    )
    embedder = OpenAIEmbedder(
        api_key=API_KEY,
        base_url=base_url,
        model=embed_model,
        provider="openai",
    )
    rl_row = source_build["rl"]
    rl = RLConfig(
        epsilon=float(rl_row["epsilon"]),
        tau=float(rl_row["tau"]),
        alpha=float(rl_row["alpha"]),
        gamma=float(rl_row["gamma"]),
        q_init_pos=float(rl_row["q_init_pos"]),
        q_init_neg=float(rl_row["q_init_neg"]),
        success_reward=float(rl_row["success_reward"]),
        failure_reward=float(rl_row["failure_reward"]),
        sim_threshold=float(rl_row["sim_threshold_os"]),
        topk=int(rl_row["topk"]),
        novelty_threshold=float(rl_row["novelty_threshold"]),
        weight_sim=float(rl_row["weight_sim"]),
        weight_q=float(rl_row["weight_q"]),
    )
    service = MemoryService(
        mos_config_path=str(mos_path),
        llm_provider=llm,
        embedding_provider=embedder,
        strategy_config=StrategyConfiguration(
            BuildStrategy.PROCEDURALIZATION,
            RetrieveStrategy.QUERY,
            UpdateStrategy.ADJUSTMENT,
        ),
        user_id=str(source_build["user_id"]),
        num_workers=1,
        db_max_concurrency=1,
        mem_cache_max_size=10000,
        q_cache_max_size=1000000,
        max_keywords=int(source_build["max_keywords"]),
        memory_confidence=float(source_build["memory_confidence"]),
        add_similarity_threshold=float(source_build["add_similarity_threshold"]),
        enable_value_driven=True,
        rl_config=rl,
        use_z_score_normalization=True,
        dedup_by_task_id=False,
        sim_norm_mean=float(source_build["sim_norm_mean"]),
        sim_norm_std=float(source_build["sim_norm_std"]),
    )

    class FailClosedSourceRunner(LLBRunner):
        def _sample_from_indices(self, sample_indices, *args, **kwargs):  # type: ignore[override]
            expected = [str(x) for x in sample_indices]
            rows = super()._sample_from_indices(sample_indices, *args, **kwargs)
            got = [str(row.get("sample_index")) for row in rows]
            if got != expected:
                raise RuntimeError(f"source-unit-execution-failed:expected={expected}:got={got}")
            return rows

    runner = FailClosedSourceRunner(
        root=outdir,
        memory_service=service,
        llm_provider=llm,
        embedding_provider=embedder,
        exp_name="b1_r45_memrl_source",
        random_seed=int(source_build["random_seed"]),
        num_section=1,
        batch_size=1,
        max_steps=int(source_build["max_steps"]),
        rl_config=rl,
        bon=int(source_build["bon"]),
        retrieve_k=int(source_build["retrieve_k"]),
        mode=str(source_build["mode"]),
        task="os",
        split_file=str(split_path),
        valid_interval=0,
        test_interval=0,
        train_set_ratio=1.0,
        start_section=0,
        algorithm=str(source_build["algorithm"]),
        val_before_train=False,
        system_prompt="",
        os_timeout=int(source_build["os_timeout_seconds"]),
        valid_file=None,
    )
    selected = [str(x) for x in source_build["selected_ids"]]
    runner.section_splits = [selected]
    if runner.batch_size != 1 or runner.num_section != 1 or runner.section_splits != [selected]:
        raise RuntimeError("runner-transaction-shape-drift")
    return service, runner


def _completed_rows(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise RuntimeError("invalid-completed-ledger-row")
            rows.append(value)
    return rows


def _execute_source(manifest: dict[str, Any], outdir: pathlib.Path, *, resume: bool) -> dict[str, Any]:
    execution = manifest["execution_manifest"]
    source_build = execution["source_build"]
    selected = [str(x) for x in source_build["selected_ids"]]
    completed_path = outdir / "completed-source-units.jsonl"
    completed = _completed_rows(completed_path)
    completed_ids = [str(row.get("task_id")) for row in completed]
    if completed_ids != selected[: len(completed_ids)]:
        raise RuntimeError("completed-ledger-is-not-selected-id-prefix")
    if completed and not resume:
        raise RuntimeError("existing-source-exposure-requires-explicit-resume")

    service, runner = _build_service_and_runner(manifest, outdir)
    start = len(completed_ids)
    if start:
        latest = completed[-1].get("checkpoint_snapshot_root")
        if not latest or not pathlib.Path(str(latest)).is_dir():
            raise RuntimeError("resume-checkpoint-missing")
        service.load_checkpoint_snapshot(str(latest))
    remaining = selected[start:]
    runner.section_splits = [remaining]
    if not remaining:
        return {"status": "SOURCE_BUILD_ALREADY_COMPLETE", "completed": len(completed_ids)}

    original_add = service.add_memories
    next_position = start

    def audited_add(*args: Any, **kwargs: Any):
        nonlocal next_position
        metadatas = kwargs.get("metadatas")
        successes = kwargs.get("successes")
        if not isinstance(metadatas, list) or len(metadatas) != 1 or not isinstance(successes, list) or len(successes) != 1:
            raise RuntimeError("source-add-memories-not-single-unit")
        task_id = str((metadatas[0] or {}).get("sample_index"))
        expected_id = selected[next_position]
        if task_id != expected_id:
            raise RuntimeError(f"source-order-drift:{task_id}!={expected_id}")
        result = original_add(*args, **kwargs)
        pairs = list(result) if isinstance(result, (list, tuple)) else []
        if len(pairs) != 1 or len(pairs[0]) != 2 or not pairs[0][1]:
            raise RuntimeError(f"source-memory-write-failed:{task_id}")
        checkpoint_base = outdir / "checkpoints" / f"{next_position + 1:03d}-{task_id}"
        checkpoint_id = f"source-{next_position + 1:03d}-{task_id}"
        snapshot = service.save_checkpoint_snapshot(str(checkpoint_base), ckpt_id=checkpoint_id)
        snapshot_root = checkpoint_base / "snapshot" / checkpoint_id
        row = {
            "position": next_position,
            "task_id": task_id,
            "success": bool(successes[0]),
            "memory_id_sha256": hashlib.sha256(str(pairs[0][1]).encode()).hexdigest(),
            "checkpoint_snapshot_root": str(snapshot_root),
            "checkpoint_visible_memories": snapshot.get("visible_memories"),
            "checkpoint_textual_memory_md5": snapshot.get("textual_memory_md5"),
            "completed_at": _now(),
        }
        _append_jsonl(completed_path, row)
        next_position += 1
        return result

    service.add_memories = audited_add  # type: ignore[assignment]
    runner.run()
    final_rows = _completed_rows(completed_path)
    if [str(row.get("task_id")) for row in final_rows] != selected:
        raise RuntimeError("source-build-did-not-complete-exact-selected-order")
    trace_path = outdir / "source-trace.jsonl"
    receipt: dict[str, Any] = {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "role": "R53_FULL350_FROZEN_MEMRL_SOURCE_BUILD_EXECUTION",
        "recorded_at": _now(),
        "status": "SOURCE_BUILD_COMPLETE",
        "selected_count": len(selected),
        "completed_count": len(final_rows),
        "completed_ids_sha256": _digest([str(row.get("task_id")) for row in final_rows]),
        "success_count": sum(bool(row.get("success")) for row in final_rows),
        "failure_count": sum(not bool(row.get("success")) for row in final_rows),
        "completed_ledger_sha256": _sha(completed_path),
        "trace_jsonl_sha256": _sha(trace_path) if trace_path.is_file() else "",
        "source_manifest_receipt_sha256": manifest.get("receipt_sha256"),
        "validation_opened": False,
        "confirmatory_outcomes_observed": 0,
        "external_provider_calls": 0,
        "scientific_authority": False,
    }
    receipt["receipt_sha256"] = _digest({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    (outdir / "source-build-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--authorization", type=pathlib.Path, required=True)
    parser.add_argument("--model-identity", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    outdir = args.output_dir.resolve()
    manifest, _auth, preflight = _preflight(
        args.manifest.resolve(), args.authorization.resolve(), args.model_identity.resolve(), outdir
    )
    if args.preflight_only:
        print(json.dumps({"status": "PREFLIGHT_PASS", "receipt_sha256": preflight["receipt_sha256"], "confirmatory_outcomes_observed": 0}, sort_keys=True))
        return

    os.environ["TRACE_JSONL_PATH"] = str(outdir / "source-trace.jsonl")
    os.environ.pop("TRACE_SAMPLE_FILTER", None)
    result = _execute_source(manifest, outdir, resume=args.resume)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
