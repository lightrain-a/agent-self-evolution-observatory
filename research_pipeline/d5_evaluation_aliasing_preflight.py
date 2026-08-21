from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from .d5_evaluation_aliasing_protocol import compile_contract
from .d5_state_sufficiency_f0 import _read_jsonl, historical_task_exposure

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTRACT = ROOT / "generated/d5-evaluation-aliasing-qwen-v2-contract.json"
DEFAULT_OUTPUT = ROOT / "generated/d5-evaluation-aliasing-qwen-v2-preflight.json"


def _gpu_memory() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        line = subprocess.check_output(command, text=True, timeout=10).splitlines()[0]
        index, name, total, used, free, util = [item.strip() for item in line.split(",", 5)]
        return {
            "available": True,
            "index": int(index),
            "name": name,
            "memory_total_mib": int(total),
            "memory_used_mib": int(used),
            "memory_free_mib": int(free),
            "utilization_percent": int(util),
        }
    except Exception as error:
        return {"available": False, "error_class": type(error).__name__}


def _local_vllm_model(base_url: str = "http://127.0.0.1:18002") -> str:
    try:
        with urlopen(base_url.rstrip("/") + "/v1/models", timeout=3) as response:
            payload = json.load(response)
        models = [str(row.get("id") or "") for row in payload.get("data") or [] if isinstance(row, dict)]
        return models[0] if len(models) == 1 else ",".join(sorted(models))
    except Exception:
        return ""


def build_preflight(*, contract_path: Path, source_memories_path: Path, private_v1_contract_path: Path,
                    historical_runs_root: Path, alfworld_root: Path, alfworld_config: Path,
                    model_path: Path, required_free_mib: int = 18000) -> dict[str, Any]:
    frozen = json.loads(contract_path.read_text(encoding="utf-8"))
    rebuilt = compile_contract(
        source_memories_path=source_memories_path,
        v1_contract_path=private_v1_contract_path,
        historical_runs_root=historical_runs_root,
        alfworld_root=alfworld_root,
        alfworld_config=alfworld_config,
        model_path=model_path,
    )
    contract_pass = rebuilt["contract_sha256"] == frozen.get("contract_sha256")

    task_ids = [str(row["task_relpath"]) for stage in ("stage_a", "stage_b") for row in frozen[stage]["tasks"]]
    exposed = historical_task_exposure(historical_runs_root)
    leaked = sorted(set(task_ids) & exposed)
    tasks_exist = all((alfworld_root / task_id).is_file() for task_id in task_ids)
    source_ids = {str(row["memory_id"]) for row in _read_jsonl(source_memories_path)}
    memories_present = all(mid in source_ids for mid in frozen["frozen_history_object"]["memory_ids"])

    gpu = _gpu_memory()
    gpu_ready = bool(gpu.get("available") and int(gpu.get("memory_free_mib") or 0) >= required_free_mib)
    blocking_model = _local_vllm_model()
    provenance_pass = contract_pass and not leaked and tasks_exist and memories_present
    ready = provenance_pass and gpu_ready

    return {
        "schema_version": "1.0",
        "preflight_id": "D5-EVALUATION-ALIASING-QWEN-V2-PREFLIGHT",
        "status": "READY_FOR_STAGE_A" if ready else ("HOLD_PROVENANCE" if not provenance_pass else "HOLD_COMPUTE"),
        "contract_sha256": frozen.get("contract_sha256"),
        "provenance_gate": {
            "pass": provenance_pass,
            "contract_rebuild_matches": contract_pass,
            "frozen_tasks": len(task_ids),
            "frozen_tasks_exist": tasks_exist,
            "frozen_tasks_with_execution_exposure": leaked,
            "frozen_memories_present": memories_present,
        },
        "compute_gate": {
            "pass": gpu_ready,
            "required_free_memory_mib": required_free_mib,
            "gpu": gpu,
            "existing_local_vllm_model": blocking_model,
            "preempt_existing_service_authorized": False,
        },
        "next_if_ready": "Execute only Stage A common-panel qualification. Stage B remains sealed until Stage A exact-equivalence and nondegeneracy gates pass.",
        "on_hold": "No scientific update. Do not replace the frozen model, task panel, memory trio, or placebo definition to obtain a runnable realization.",
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-memories", type=Path, required=True)
    parser.add_argument("--private-v1-contract", type=Path, required=True)
    parser.add_argument("--historical-runs-root", type=Path, required=True)
    parser.add_argument("--alfworld-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--required-free-mib", type=int, default=18000)
    args = parser.parse_args()
    payload = build_preflight(
        contract_path=args.contract,
        source_memories_path=args.source_memories,
        private_v1_contract_path=args.private_v1_contract,
        historical_runs_root=args.historical_runs_root,
        alfworld_root=args.alfworld_root,
        alfworld_config=args.config,
        model_path=args.model,
        required_free_mib=args.required_free_mib,
    )
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
