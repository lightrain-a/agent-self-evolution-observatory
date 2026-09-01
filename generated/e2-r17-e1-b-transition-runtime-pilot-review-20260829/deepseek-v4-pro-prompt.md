You are an independent adversarial pre-execution reviewer for the E2-R17 E1-B transition runtime Pilot. You are blind to the other reviewer. This Pilot is NOT the E1-B negative-control scientific experiment and cannot authorize MRW, held-out future-skill inference, paper claims, frontend promotion, or submission.

Reviewer endpoint: deepseek-v4-pro
Exact draft contract SHA-256: c279c328018c9e37e2d2676adc9f0c5118886a1a3e9222a2206ff99b723bdb35

The immediately preceding hosted provider-runtime Pilot passed 3/3 updater arms and established real SkillEvolver runtime/measurability. One execution boundary is still untested: whether a content-addressed learned SKILL.md produced under the dedicated updater runtime can be handed to the frozen actor/evaluator runtime through the exact updater-receipt provenance path, loaded as a noninitial skill, and evaluated by the same SpreadsheetBench verifier.

The proposed transition Pilot does exactly one such handoff. It generates one WIN-only learned skill from the same eight historical E0 pools used by the provider-runtime Pilot, then evaluates that learned skill at K=1 on the lexicographically first pre-existing development task `r17-b0-agj-p4`. The development result may not select or promote any method/model/runtime and is not reported as scientific effectiveness.

Audit the exact contract/code and answer:

1. HISTORICAL UPDATE SELECTION: Are the exact same eight historical E0 pool SHAs/order reused without outcome-driven reselection? Is the update WIN-only and V3.1 arm-blinded/selected-evidence-score semantics unchanged?

2. DEVELOPMENT TASK SELECTION: Is `r17-b0-agj-p4` fixed by lexicographic development task ID before learned-skill outcome is observed? Does any path access E1 common held-out tasks or select the development task based on performance?

3. UPDATER CAUSAL PURITY: Does the updater path still use ExactMatchedEvidenceBlockRenderer, BlindedEvidenceUnit, selected evidence score, pinned SkillEvolver, dedicated updater runtime, temperature=0, retry=0, thinking disabled, max_parse_attempts=1? No MRW or A/B comparison should occur.

4. NONINITIAL SKILL RECEIPT HANDOFF: After the WIN update, does the actor receive exactly `skill_post/SKILL.md` plus the matching `update_receipt.json`? Does the actor runner revalidate skill path, skill SHA, contract SHA and authorization SHA before accepting a noninitial skill? Is omission of a pre-known learned-skill SHA from authorization scope scientifically acceptable because the learned SHA is only known after the provider update and is instead content-addressed by the bound update receipt?

5. ACTOR RUNTIME / VERIFIER: Is actor execution under the independently frozen actor/evaluator venv, exact DeepSeek resolved identity, K=1, max_turns=10, same controlled suite and SpreadsheetBench verifier? Does the transition runner validate that the actor summary loaded the learned skill SHA and updater receipt SHA, without promoting the task score?

6. SHARED BUDGET: One contract-bound ProviderBudgetLedger is shared across the updater and actor subprocess. Is 20 total / 10 per unit fail-closed, with the updater nominally consuming 10 and the single actor rollout allowed at most 10? Can either role reset/reinitialize the ledger or bypass pre-I/O claims?

7. CHECKPOINT / FAILURE PRESERVATION: If updater completes, may it be safely reused for the evaluation stage using content-addressed update checkpoint? If either update or evaluation is partial/ambiguous, does the runner preserve the stale lock and refuse automatic rerun? Is this consistent with the failure-differential policy?

8. SCIENTIFIC BOUNDARY: Confirm 0 E1 common held-out access, 0 WIN-A/WIN-B equivalence inference, 0 MRW execution, 0 learned-skill effect promotion, and 0 paper authority. The single development outcome is allowed only to prove that the verifier completes with a receipt-bound noninitial skill.

9. FAILURE LEARNING: Does the contract appropriately separate runtime/implementation failure from scientific-mechanism failure? A transition Pilot failure cannot be used against R17's mechanism; it must be diagnosed and versioned. Conversely this Pilot PASS cannot support the R17 mechanism either.

10. DECISION: PASS only if no P0/P1 blocker remains. Even PASS must keep E1-B negative-control execution HOLD, MRW HOLD, and paper_claim_authority=false.

Return exactly one JSON object and no markdown using this schema:
{
  "draft_contract_sha256_acknowledged": "",
  "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_E1_B_TRANSITION_RUNTIME_PILOT|REVISE_TRANSITION_PILOT|STOP_TRANSITION_PILOT",
  "historical_update_selection_assessment": "",
  "development_task_selection_assessment": "",
  "updater_causal_purity_assessment": "",
  "noninitial_skill_receipt_handoff_assessment": "",
  "actor_runtime_and_verifier_assessment": "",
  "shared_provider_budget_assessment": "",
  "checkpoint_failure_preservation_assessment": "",
  "scientific_boundary_assessment": "",
  "failure_learning_policy_assessment": "",
  "remaining_blockers": [
    {
      "priority": "P0|P1",
      "issue": "",
      "why_blocking": "",
      "exact_repair": ""
    }
  ],
  "nonblocking_notes": [
    ""
  ],
  "transition_runtime_pilot_recommendation": "ALLOW_SEPARATE_FROZEN_TRANSITION_RUNTIME_PILOT_AUTHORIZATION|HOLD|STOP",
  "e1_b_negative_control_recommendation": "HOLD|STOP",
  "mrw_causal_comparison_recommendation": "HOLD|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}

Set `draft_contract_sha256_acknowledged` exactly to the SHA above. For PASS use verdict `PASS_TO_SEPARATELY_AUTHORIZED_E1_B_TRANSITION_RUNTIME_PILOT` and transition recommendation `ALLOW_SEPARATE_FROZEN_TRANSITION_RUNTIME_PILOT_AUTHORIZATION`. Keep both scientific recommendations HOLD and paper_claim_authority=false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: transition_pilot_draft | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-b-transition-runtime-pilot-draft-contract-20260829.json =====
{
  "actor": {
    "concurrency": 1,
    "k": 1,
    "max_output_tokens": 4096,
    "max_turns": 10,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "temperature": 0,
    "thinking": "disabled"
  },
  "actor_runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2",
    "role": "actor_evaluator",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "artifact_type": "e2-r17-e1-b-transition-runtime-pilot-contract",
  "authority": {
    "dual_preexecution_review": true,
    "e1_b_negative_control": false,
    "execute_transition_runtime_pilot": false,
    "mrw_causal_comparison": false,
    "paper_promotion": false,
    "submission": false
  },
  "bound_code": {
    "actor_runner": {
      "path": "scripts/run_e2_r17_actor_pool.py",
      "sha256": "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
    },
    "actor_runtime_validator": {
      "path": "scripts/run_e2_r17_e1_a_pool_support.py",
      "sha256": "24ea070b08399d48af99294615a508874f851af941f5bb0efabe341b0854617d"
    },
    "provider_budget": {
      "path": "research_pipeline/e2_r17_provider_budget.py",
      "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
    },
    "provider_runtime_helpers": {
      "path": "scripts/run_e2_r17_v31_provider_runtime_pilot.py",
      "sha256": "533f11ba2bfc85aa6fcea8bc1b9502a039cd7770055010a8838b78bb8b6041d5"
    },
    "renderer": {
      "path": "research_pipeline/e2_r17_evidence_window_v2.py",
      "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7"
    },
    "transition_runner": {
      "path": "scripts/run_e2_r17_e1_b_transition_runtime_pilot.py",
      "sha256": "2564252ac4ce54c076d47a35bd32f8bd319463b284f1a5e2d008bd581530058c"
    },
    "updater_adapter": {
      "path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
      "sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8"
    },
    "updater_wrapper": {
      "path": "research_pipeline/e2_r17_mindmemos_updater.py",
      "sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
    }
  },
  "budget": {
    "actor_max_calls": 10,
    "claim_before_provider_io": true,
    "claims_never_released": true,
    "max_provider_calls": 20,
    "max_provider_calls_per_unit": 10,
    "shared_ledger_relative_path": "checkpoints/provider_budget.sqlite3",
    "updater_nominal_calls": 10
  },
  "checkpoint": {
    "evaluation_failure": "checkpoints/evaluation_failure.json",
    "exclusive_lock": ".exclusive.lock",
    "partial_update_or_eval_auto_rerun": false,
    "preserve_lock_on_failure": true,
    "update_checkpoint": "checkpoints/update_completed.json"
  },
  "date": "2026-08-29",
  "development_evaluation": {
    "e1_common_heldout_accessed": false,
    "k": 1,
    "selection_rule": "Lexicographically first task ID from the pre-existing development split; frozen without reading any task outcome under the learned skill.",
    "task_id": "r17-b0-agj-p4",
    "used_for_scientific_effectiveness": false
  },
  "forbidden": [
    "E1 common heldout evaluation",
    "WIN-A/WIN-B equivalence inference",
    "MRW execution or method-effect comparison",
    "task/model/renderer selection based on development outcome",
    "paper/frontend/submission promotion",
    "automatic rerun after ambiguous provider call"
  ],
  "historical_inputs": {
    "e0_root": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828",
    "selected_pools": [
      {
        "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-agj-p1/pool_k8.json",
        "sha256": "3872f2b33f11130aeed073e46650c7d6c4a13c256632252a7102ea81c8492c0c",
        "task_id": "r17-b1-agj-p1"
      },
      {
        "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-agj-p4/pool_k8.json",
        "sha256": "1afa7d56dca0b3b04ab4c494e05c43ad49f6015e928cf8348a61af81eb753813",
        "task_id": "r17-b1-agj-p4"
      },
      {
        "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-fmv-p4/pool_k8.json",
        "sha256": "2b852fc1f2f41cc68e1869ce3f11f552ca176e63fd1121a528fa4361ade7e989",
        "task_id": "r17-b1-fmv-p4"
      },
      {
        "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-fmv-p8/pool_k8.json",
        "sha256": "945fde93b9812ceb750cace1140bb383eb59a2f1ae2fa966dc7723fe1ebd9d03",
        "task_id": "r17-b1-fmv-p8"
      },
      {
        "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-ioc-p2/pool_k8.json",
        "sha256": "5a5c6bc214b05fc807387cf32766aa6f0f42617af04ac24e0b9993d431169bdc",
        "task_id": "r17-b1-ioc-p2"
      },
      {
        "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-ioc-p5/pool_k8.json",
        "sha256": "7e5f613d500b2be2b40d42d4124b12213ee989619f0b6f464649522b194645df",
        "task_id": "r17-b1-ioc-p5"
      },
      {
        "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-msp-p0/pool_k8.json",
        "sha256": "10d950ffdad2dce1957c9bac73f5f4e4816db47cff40bc4177ab4f8930f8834e",
        "task_id": "r17-b1-msp-p0"
      },
      {
        "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-msp-p2/pool_k8.json",
        "sha256": "18ce3604f249ecbbddab21dd39b9f9db67861c41cb97cd7866dbf5c5e9d1355c",
        "task_id": "r17-b1-msp-p2"
      }
    ],
    "selection_rule": "Lexicographically first eight pool_k8.json paths, frozen before reading mixed/rescue/outcome fields for this Pilot.",
    "source": "E0 historical pools only"
  },
  "initial_skill": {
    "path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
    "sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
  },
  "mindmemos": {
    "bound_files": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py": "48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c",
      "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py": "771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e"
    },
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817"
  },
  "model_identity": {
    "path": "generated/e2-r17-v31-provider-pilot-v2-model-identity-adjudication-20260829.json",
    "qualification_path": "generated/e2-r17-v31-provider-pilot-v2-model-identity-qualification-20260829.json",
    "qualification_sha256": "8063a6d638b4bfa974c74ab8bbea023deec3958d497f4e78366222e0cd7a5634",
    "required_status": "PASS_CURRENT_REVIEW_TRANCHE",
    "sha256": "7c0874547387bb2c9a3aaf13f8fb1ac0dccd555caf78ec2d8e040740642957ea"
  },
  "parents": {
    "failure_registry": {
      "path": "generated/e2-r17-failure-differential-registry-v2-20260829.json",
      "sha256": "7850763eeeb3c08db0e1989d456ea21c03384fa46d559f78f802e9323b69f4c5"
    },
    "provider_runtime_adjudication": {
      "path": "generated/e2-r17-v31-provider-runtime-pilot-v2-adjudication-20260829.json",
      "sha256": "8be8a4596ffef8e3702f8e422ed4dd2c55b7fc1f97573b125f30096d64f60424"
    }
  },
  "purpose": "Runtime/measurability transition only: generate one receipt-bound WIN skill from eight historical E0 pools, then load that noninitial skill through the frozen actor path and execute exactly one K=1 development task. No E1 heldout data, no WIN-A/WIN-B equivalence inference, no MRW scientific comparison.",
  "renderer": {
    "arm_metadata_visible": false,
    "exact_final_retokenized_parity_required": true,
    "final_block_cap_tokens": 3072,
    "padding": false,
    "path": "research_pipeline/e2_r17_evidence_window_v2.py",
    "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7",
    "tokenizer_encoding": "cl100k_base",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0"
  },
  "required_checks": [
    "dedicated updater runtime exact-entrypoint qualification passes",
    "actor/evaluator runtime qualification passes independently",
    "one shared provider ledger claims before I/O and caps total at 20 / per-unit at 10",
    "WIN update uses V3.1 arm-blinded selected-evidence semantics from exact historical pools",
    "update receipt content-addresses skill_post and binds exact contract+authorization",
    "actor loads noninitial SKILL.md only through the matching updater receipt",
    "actor evaluation uses fixed development task r17-b0-agj-p4, K=1, same resolved model and verifier",
    "no E1 common heldout task is accessed",
    "development outcome is not used to promote/select method/model/runtime",
    "partial update/evaluation keeps stale lock and cannot auto-rerun"
  ],
  "run_root": "/data/wyt/e2-r17-search-projection/runtime-pilots/e1-b-transition-v1-20260829",
  "schema_version": "1.0",
  "status": "DRAFT_PENDING_DUAL_PREEXECUTION_REVIEW",
  "suite": {
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "updater": {
    "adapter_path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
    "adapter_sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8",
    "batch_size": 8,
    "first_party": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "max_parse_attempts": 1,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "score_semantics": "selected_evidence_trajectory",
    "temperature": 0.0,
    "thinking": "disabled",
    "transcript_max_chars": 100000,
    "wrapper_path": "research_pipeline/e2_r17_mindmemos_updater.py",
    "wrapper_sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
  },
  "updater_runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv.freeze.txt",
    "freeze_sha256": "80cd6fdd8eb672e41252c099766fd171a5a7a4b90c284d87da87d09f0d559731",
    "litellm_local_model_cost_map": true,
    "post_lock_compatibility_override": {
      "disclosed": true,
      "package": "tiktoken",
      "reason": "pre-frozen V3.1 ExactMatchedEvidenceBlockRenderer compatibility",
      "version": "0.11.0"
    },
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv/bin/python",
    "qualification_path": "generated/e2-r17-updater-runtime-qualification-20260829.json",
    "qualification_sha256": "f2319815cdcd7caf248c498c470720d4e3f6c9b5e579fad59914df687cdf5b6d",
    "required_entrypoint": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_UPDATER_RUNTIME",
    "role": "persistent_skill_updater",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv"
  }
}


===== BOUND ARTIFACT: transition_pilot_runner | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_e1_b_transition_runtime_pilot.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import run_projection_update
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, project_stream
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import (
    bind_mindmemos,
    evidence_units,
    load_selected_pools,
    validate_updater_runtime,
)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_contract_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == "FROZEN_E1_B_TRANSITION_RUNTIME_PILOT", "transition Pilot contract not frozen")
    require(auth.get("status") == "AUTHORIZED_E1", "transition Pilot authorization must use AUTHORIZED_E1")
    require(auth.get("contract_sha256") == sha_file(contract_path), "transition authorization/contract SHA mismatch")
    authority = auth.get("authority") or {}
    require(authority.get("scientific_experiment") is True, "actor runner requires scoped scientific execution authority")
    require(authority.get("e1_b") is True, "transition Pilot requires E1-B noninitial-skill loading authority")
    require(authority.get("e1_b_transition_runtime_pilot") is True, "transition runtime Pilot authority bit absent")
    require(authority.get("e1_b_negative_control") is False, "transition Pilot must not authorize negative-control inference")
    require(authority.get("mrw_causal_comparison") is False, "transition Pilot must not authorize MRW science")
    require(authority.get("paper_promotion") is False, "transition Pilot cannot promote paper")
    scope = auth.get("execution_scope") or {}
    require(scope.get("allowed_modes") == ["e1"], "transition Pilot mode scope drift")
    require(scope.get("allowed_task_ids") == [contract["development_evaluation"]["task_id"]], "transition Pilot task scope drift")
    require(int(scope.get("exact_k")) == 1, "transition Pilot must bind K=1 evaluation")
    require(scope.get("allow_noninitial_skill") is True, "transition Pilot must explicitly allow receipt-bound noninitial skill")
    budget_scope = scope.get("provider_budget") or {}
    require(budget_scope.get("required") is True, "transition Pilot must require provider budget ledger")
    require(int(budget_scope.get("total_limit")) == int(contract["budget"]["max_provider_calls"]), "transition total budget drift")
    require(int(budget_scope.get("per_unit_limit")) == int(contract["budget"]["max_provider_calls_per_unit"]), "transition per-unit budget drift")
    return contract, auth


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    contract, auth = validate_contract_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)

    updater_runtime_contract = {"runtime": contract["updater_runtime"], "mindmemos": contract["mindmemos"]}
    updater_python, updater_env = validate_updater_runtime(updater_runtime_contract)
    require(Path(sys.executable) == updater_python, "transition Pilot must itself run under dedicated updater runtime")
    actor_python, actor_env = validate_actor_runtime({"runtime": contract["actor_runtime"]})

    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]
        require(path.is_file() and sha_file(path) == item["sha256"], f"bound code drift: {label}")

    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.check_output(["git", "-C", str(mind_root), "rev-parse", "HEAD"], text=True).strip()
    require(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    require(not subprocess.check_output(["git", "-C", str(mind_root), "status", "--short"], text=True).strip(), "MindMemOS checkout dirty")
    bind_mindmemos(mind_root)

    identity_path = ROOT / contract["model_identity"]["path"]
    require(identity_path.is_file() and sha_file(identity_path) == contract["model_identity"]["sha256"], "transition model identity drift")
    identity = load_json(identity_path)
    require(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "transition model identity not qualified")
    model_row = identity["requested_and_resolved"][contract["updater"]["requested_model"]]
    requested = str(model_row["requested"])
    resolved = str(model_row["resolved"])
    require(resolved == contract["updater"]["resolved_model"], "transition resolved model drift")

    pools = load_selected_pools({"historical_inputs": contract["historical_inputs"]})
    initial_skill_path = Path(contract["initial_skill"]["path"])
    require(initial_skill_path.is_file() and sha_file(initial_skill_path) == contract["initial_skill"]["sha256"], "transition initial skill drift")
    initial_skill = initial_skill_path.read_text(encoding="utf-8")
    initial_sha = sha_file(initial_skill_path)
    win_units, _, evidence_receipts = evidence_units(
        pools,
        final_block_cap_tokens=int(contract["renderer"]["final_block_cap_tokens"]),
        transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
    )
    win_stream = project_stream(
        stream_id="e1-b-transition-runtime-pilot",
        initial_skill_sha256=initial_sha,
        pools=pools,
        projection=ProjectionName.WINNER_ONLY,
    )

    run_root = Path(contract["run_root"])
    run_root.mkdir(parents=True, exist_ok=True)
    lock_path = run_root / ".exclusive.lock"
    lock_handle = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise RuntimeError("transition Pilot lock already held; inspect before resume") from exc
    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(json.dumps({"pid": os.getpid(), "contract_sha256": contract_sha, "authorization_sha256": auth_sha}, sort_keys=True))
    lock_handle.flush(); os.fsync(lock_handle.fileno())

    ledger_path = run_root / "checkpoints/provider_budget.sqlite3"
    ledger = ProviderBudgetLedger(
        path=ledger_path,
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        total_limit=int(contract["budget"]["max_provider_calls"]),
        per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),
        allow_create=not ledger_path.exists(),
    )
    success = False
    try:
        update_dir = run_root / "update/win"
        update_receipt = update_dir / "update_receipt.json"
        skill_path = update_dir / "skill_post/SKILL.md"
        update_checkpoint = run_root / "checkpoints/update_completed.json"
        if update_checkpoint.exists():
            cp = load_json(update_checkpoint)
            require(update_receipt.is_file() and skill_path.is_file(), "transition completed update artifacts missing")
            require(sha_file(update_receipt) == cp["update_receipt_sha256"], "transition update receipt SHA drift")
            require(sha_file(skill_path) == cp["skill_post_sha256"], "transition skill SHA drift")
        else:
            if update_dir.exists() and any(update_dir.rglob("*")):
                raise RuntimeError("partial ambiguous transition update exists; do not auto-rerun")
            load_env_file(args.env_file)
            raw = ArkSettings.from_env(required=True)
            require(raw.base_url.rstrip("/") == PLAN_BASE_URL, "transition updater refuses non-Ark-Plan route")
            settings = ArkSettings(api_key=raw.api_key, base_url=raw.base_url, default_model=raw.default_model, timeout_seconds=300.0, max_retries=0)
            adapter = MindMemOSArkPlanChatAdapter(
                settings=settings,
                requested_model=requested,
                required_resolved_model=resolved,
                max_parse_attempts=int(contract["updater"]["max_parse_attempts"]),
                record_dir=update_dir / "provider_calls",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="e1-b-transition/update_win",
            )
            result = await run_projection_update(
                stream=win_stream,
                pools=pools,
                initial_skill_md=initial_skill,
                run_dir=update_dir,
                llm_adapter=adapter,
                mindmemos_commit=head,
                contract_sha256=contract_sha,
                authorization_sha256=auth_sha,
                transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
                blinded_evidence_units=win_units,
            )
            receipts = adapter.public_receipts()
            require(result.provider_calls == 10 and len(receipts) == 10, "transition updater must use exact nominal 10 calls")
            require(not any(row.get("parse_error") for row in receipts), "transition updater parse error")
            atomic_json(update_checkpoint, {
                "status": "COMPLETED",
                "update_receipt_path": result.update_receipt_path,
                "update_receipt_sha256": result.update_receipt_sha256,
                "skill_post_path": result.skill_post_path,
                "skill_post_sha256": result.skill_post_sha256,
                "provider_calls": result.provider_calls,
                "provider_tokens": result.provider_total_tokens,
            })

        eval_root = run_root / "evaluation"
        eval_summary = eval_root / "evaluation_summary.json"
        if eval_summary.exists():
            summary = load_json(eval_summary)
            require(summary.get("status") == "COMPLETED", "transition evaluation summary incomplete")
        else:
            if eval_root.exists() and any(eval_root.rglob("*")):
                raise RuntimeError("partial ambiguous transition evaluation exists; do not auto-rerun")
            command = [
                str(actor_python), str(ROOT / "scripts/run_e2_r17_actor_pool.py"),
                "--env-file", str(args.env_file),
                "--suite-root", contract["suite"]["root"],
                "--mindmemos-root", str(mind_root),
                "--run-root", str(eval_root),
                "--identity", str(identity_path),
                "--authorization", str(args.authorization),
                "--skill-source", str(skill_path.parent),
                "--updater-receipt", str(update_receipt),
                "--mode", "e1",
                "--model", contract["updater"]["requested_model"],
                "--task-id", contract["development_evaluation"]["task_id"],
                "--k", "1",
                "--prefix-ks", "1",
                "--max-turns", str(contract["actor"]["max_turns"]),
                "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
                "--concurrency", "1",
                "--provider-budget-ledger", str(ledger_path),
                "--provider-total-call-limit", str(contract["budget"]["max_provider_calls"]),
                "--provider-per-unit-call-limit", str(contract["budget"]["max_provider_calls_per_unit"]),
                "--output", str(eval_summary),
            ]
            env = actor_env.copy()
            env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
            completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
            if completed.returncode != 0:
                atomic_json(run_root / "checkpoints/evaluation_failure.json", {
                    "status": "TECHNICAL_FAILURE",
                    "returncode": completed.returncode,
                    "stdout_tail": completed.stdout[-3000:],
                    "stderr_tail": completed.stderr[-3000:],
                    "provider_relaunch_authorized": False,
                })
                raise RuntimeError("transition noninitial-skill evaluation failed; stale lock preserved")
            require(eval_summary.is_file(), "transition actor returned without evaluation summary")
            summary = load_json(eval_summary)
            require(summary.get("status") == "COMPLETED", "transition evaluation summary incomplete")

        budget = ledger.snapshot()
        require(budget.total_claimed <= int(contract["budget"]["max_provider_calls"]), "transition total provider budget exceeded")
        require(summary.get("skill_pre_sha256") == sha_file(skill_path), "transition actor did not load receipt-bound learned skill")
        require(summary.get("updater_receipt_sha256") == sha_file(update_receipt), "transition actor updater receipt binding drift")
        require(summary.get("k") == 1, "transition evaluation K drift")
        require([row["task_id"] for row in summary.get("tasks") or []] == [contract["development_evaluation"]["task_id"]], "transition development task drift")

        final = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-e1-b-transition-runtime-pilot-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "PASS_UPDATE_TO_NONINITIAL_SKILL_EVALUATION_HANDOFF",
            "contract_sha256": contract_sha,
            "authorization_sha256": auth_sha,
            "historical_update_pools": [pool.pool_id for pool in pools],
            "development_evaluation_task_id": contract["development_evaluation"]["task_id"],
            "development_task_outcome_used_for_promotion": False,
            "evidence_receipts": evidence_receipts,
            "update_receipt_sha256": sha_file(update_receipt),
            "skill_post_sha256": sha_file(skill_path),
            "evaluation_summary_sha256": sha_file(eval_summary),
            "provider_budget": budget.to_dict(),
            "heldout_evaluation_calls": 0,
            "e1_common_heldout_accessed": False,
            "mrw_executed": False,
            "negative_control_inference_performed": False,
            "scientific_effectiveness_evaluated": False,
            "authority": {"prepare_e1_b_negative_control_full_contract": True, "execute_e1_b_negative_control": False, "mrw_causal_comparison": False, "paper_promotion": False},
        }
        atomic_json(run_root / "summary/transition_runtime_pilot_summary.json", final)
        success = True
        return final
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()
        if success:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()
    payload = asyncio.run(main_async(args))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS_UPDATE_TO_NONINITIAL_SKILL_EVALUATION_HANDOFF" else 2


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: actor_runner | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_actor_pool.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import (
    ActorRolloutConfig,
    atomic_json,
    file_sha256,
    freeze_nested_pools,
    run_actor_rollout,
)
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, PLAN_BASE_URL
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger


def load_mindmemos(root: Path) -> tuple[Any, Any]:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    source_roots = [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    for source in reversed(source_roots):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    from mindmemos_eval.skills.agents import ReactAgentFactory
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv

    return ReactAgentFactory, SpreadsheetBenchEnv


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_ids_from_args(args: argparse.Namespace, split: dict[str, Any]) -> list[str]:
    if args.task_id:
        return [str(value) for value in args.task_id]
    if args.stream_id:
        for key in ("e1_update_streams", "e3_future_streams"):
            if args.stream_id in split.get(key, {}):
                return [str(value) for value in split[key][args.stream_id]]
        raise ValueError(f"unknown stream id: {args.stream_id}")
    if args.lane:
        value = split.get(args.lane)
        if not isinstance(value, list):
            raise ValueError(f"lane is not a task list: {args.lane}")
        return [str(item) for item in value]
    raise ValueError("one of --task-id, --stream-id, or --lane is required")


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
) -> tuple[dict[str, Any] | None, str | None]:
    development = {str(item) for item in split.get("development") or []}
    if mode == "protocol_smoke":
        if not set(task_ids).issubset(development):
            raise RuntimeError("protocol smoke may access development tasks only")
        if authorization is not None:
            raise RuntimeError("protocol smoke must not borrow scientific authorization")
        return None, None
    if authorization is None:
        raise RuntimeError("scientific actor execution requires --authorization")
    payload = json.loads(authorization.read_text(encoding="utf-8"))
    if payload.get("status") not in {"AUTHORIZED_E0", "AUTHORIZED_E1", "AUTHORIZED_PUBLIC_EXTERNALITY"}:
        raise RuntimeError("authorization artifact does not authorize actor execution")
    if not payload.get("authority", {}).get("scientific_experiment"):
        raise RuntimeError("authorization has zero scientific authority")

    # New scoped authorizations fail closed. Historical artifacts without an
    # execution_scope remain readable/replayable, but any E1-A/E1-B tranche
    # minted after this guard must bind the exact mode, task IDs and K it grants.
    scope = payload.get("execution_scope")
    if scope is not None:
        allowed_modes = {str(value) for value in scope.get("allowed_modes") or []}
        if not allowed_modes or mode not in allowed_modes:
            raise RuntimeError(f"authorization does not allow mode={mode}")
        allowed_tasks = {str(value) for value in scope.get("allowed_task_ids") or []}
        if not allowed_tasks or not set(task_ids).issubset(allowed_tasks):
            raise RuntimeError("authorization does not allow one or more requested task IDs")
        exact_k = scope.get("exact_k")
        if exact_k is not None and int(exact_k) != int(k):
            raise RuntimeError(f"authorization requires exact K={exact_k}, requested K={k}")
        if scope.get("allow_noninitial_skill") is False and payload.get("authority", {}).get("e1_b"):
            raise RuntimeError("authorization scope is internally inconsistent about non-initial skills")
    return payload, sha256(authorization)


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    ReactAgentFactory, SpreadsheetBenchEnv = load_mindmemos(args.mindmemos_root)
    load_env_file(args.env_file)
    settings = ArkSettings.from_env(required=True)
    if settings.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("E2-R17 actor refuses any non-Ark-Plan route")
    settings = ArkSettings(
        api_key=settings.api_key,
        base_url=settings.base_url,
        default_model=settings.default_model,
        timeout_seconds=300,
        max_retries=0,
    )
    identity = json.loads(args.identity.read_text(encoding="utf-8"))
    if identity.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("current model identity adjudication is not passing")
    model_row = identity["requested_and_resolved"][args.model]
    requested_model = str(model_row["requested"])
    required_resolved = str(model_row["resolved"])

    split_path = args.suite_root / "r17_split_manifest.json"
    split = json.loads(split_path.read_text(encoding="utf-8"))
    task_ids = task_ids_from_args(args, split)
    authorization_payload, authorization_sha = validate_authority(
        mode=args.mode,
        authorization=args.authorization,
        task_ids=task_ids,
        split=split,
        k=args.k,
    )
    contract_sha = (
        str(authorization_payload.get("contract_sha256") or "")
        if authorization_payload is not None
        else None
    )
    provider_budget_ledger: ProviderBudgetLedger | None = None
    budget_args_present = any(
        value is not None
        for value in (args.provider_budget_ledger, args.provider_total_call_limit, args.provider_per_unit_call_limit)
    )
    if budget_args_present:
        if authorization_payload is None or not authorization_sha or not contract_sha:
            raise RuntimeError("provider budget ledger is allowed only for a bound scientific authorization")
        if args.provider_budget_ledger is None or args.provider_total_call_limit is None or args.provider_per_unit_call_limit is None:
            raise RuntimeError("provider budget ledger path, total limit and per-unit limit must be supplied together")
        provider_budget_ledger = ProviderBudgetLedger(
            path=args.provider_budget_ledger,
            contract_sha256=contract_sha,
            authorization_sha256=authorization_sha,
            total_limit=int(args.provider_total_call_limit),
            per_unit_limit=int(args.provider_per_unit_call_limit),
            allow_create=not args.provider_budget_ledger.exists(),
        )
    if authorization_payload is not None:
        scope = authorization_payload.get("execution_scope") or {}
        provider_budget_scope = scope.get("provider_budget") or {}
        if provider_budget_scope.get("required") is True:
            if provider_budget_ledger is None:
                raise RuntimeError("authorization requires a fail-closed provider budget ledger")
            if int(provider_budget_scope.get("total_limit")) != int(args.provider_total_call_limit):
                raise RuntimeError("authorization provider total-call limit drift")
            if int(provider_budget_scope.get("per_unit_limit")) != int(args.provider_per_unit_call_limit):
                raise RuntimeError("authorization provider per-unit limit drift")
        expected_resolved = scope.get("required_resolved_model")
        if expected_resolved and str(expected_resolved) != required_resolved:
            raise RuntimeError("authorization resolved-model identity drift")
        expected_identity_sha = scope.get("identity_artifact_sha256")
        if expected_identity_sha and sha256(args.identity) != expected_identity_sha:
            raise RuntimeError("authorization model-identity artifact drift")
        if scope.get("max_turns") is not None and int(scope["max_turns"]) != int(args.max_turns):
            raise RuntimeError("authorization max_turns drift")
        if scope.get("max_output_tokens") is not None and int(scope["max_output_tokens"]) != int(args.max_output_tokens):
            raise RuntimeError("authorization max_output_tokens drift")
    metadata_rows = json.loads((args.suite_root / "r17_controlled_metadata.json").read_text(encoding="utf-8"))
    metadata = {str(row["id"]): row for row in metadata_rows}
    missing = [task_id for task_id in task_ids if task_id not in metadata]
    if missing:
        raise RuntimeError(f"tasks absent from controlled metadata: {missing}")

    env = SpreadsheetBenchEnv(args.suite_root, args.run_root)
    cases = {case.id: case for case in env.load_cases("all")}
    mindmemos_commit = __import__("subprocess").check_output(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if authorization_payload is not None and mindmemos_commit != authorization_payload.get("mindmemos_commit"):
        raise RuntimeError("MindMemOS commit drifted after scientific authorization")
    if authorization_payload is not None:
        scope = authorization_payload.get("execution_scope") or {}
        expected_suite_sha = scope.get("suite_manifest_sha256")
        expected_split_sha = scope.get("split_manifest_sha256")
        if expected_suite_sha and file_sha256(args.suite_root / "suite_manifest.json") != expected_suite_sha:
            raise RuntimeError("suite manifest drifted after scientific authorization")
        if expected_split_sha and file_sha256(split_path) != expected_split_sha:
            raise RuntimeError("split manifest drifted after scientific authorization")

    default_skill_source = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx"
    skill_source = (args.skill_source or default_skill_source).resolve()
    skill_md = skill_source / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError(f"skill source does not contain SKILL.md: {skill_source}")
    skill_sha = file_sha256(skill_md)
    if authorization_payload is not None:
        required_skill_sha = (authorization_payload.get("execution_scope") or {}).get("required_skill_pre_sha256")
        if required_skill_sha and skill_sha != required_skill_sha:
            raise RuntimeError("skill pre-state drifted after scientific authorization")
    updater_receipt_sha: str | None = None
    if skill_source != default_skill_source.resolve():
        if args.mode != "e1" or args.updater_receipt is None:
            raise RuntimeError("a non-initial skill is allowed only for E1 evaluation with --updater-receipt")
        updater_receipt = json.loads(args.updater_receipt.read_text(encoding="utf-8"))
        updater_receipt_sha = sha256(args.updater_receipt)
        if updater_receipt.get("status") != "COMPLETED":
            raise RuntimeError("updater receipt is not completed")
        if Path(updater_receipt.get("skill_post_path") or "").resolve() != skill_md.resolve():
            raise RuntimeError("updater receipt does not bind the supplied skill path")
        if updater_receipt.get("skill_post_sha256") != skill_sha:
            raise RuntimeError("updater receipt does not bind the supplied skill content")
        if updater_receipt.get("contract_sha256") != contract_sha:
            raise RuntimeError("updater receipt contract SHA differs from evaluation authorization")
        if updater_receipt.get("authorization_sha256") != authorization_sha:
            raise RuntimeError("updater receipt authorization SHA differs from evaluation authorization")
    elif args.updater_receipt is not None:
        raise RuntimeError("--updater-receipt must not be supplied for the frozen initial skill")
    evaluator_sources = [
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]
    semaphore = asyncio.Semaphore(max(1, args.concurrency))

    async def run_unit(task_id: str, rollout_index: int):
        async with semaphore:
            adapter = ArkPlanReactLLM(
                settings=settings,
                requested_model=requested_model,
                required_resolved_model=required_resolved,
                max_output_tokens=args.max_output_tokens,
                temperature=0,
                thinking="disabled",
                provider_budget_ledger=provider_budget_ledger,
                provider_budget_unit_id=(f"{task_id}/rollout_{rollout_index}" if provider_budget_ledger is not None else None),
            )
            factory = ReactAgentFactory(
                adapter,
                max_turns=args.max_turns,
                skill_sources=[skill_source],
                python_path=sys.executable,
            )
            config = ActorRolloutConfig(
                requested_model=requested_model,
                required_resolved_model=required_resolved,
                max_turns=args.max_turns,
                skill_source=str(skill_source),
                skill_pre_sha256=skill_sha,
                failure_family=str(metadata[task_id]["primary_failure_family"]),
                experiment_mode=args.mode,
                contract_sha256=contract_sha,
                authorization_sha256=authorization_sha,
            )
            return await run_actor_rollout(
                env=env,
                case=cases[task_id],
                rollout_index=rollout_index,
                agent_factory=factory,
                adapter=adapter,
                config=config,
                evaluator_sources=evaluator_sources,
            )

    task_rows: list[dict[str, Any]] = []
    prefix_ks = tuple(int(value) for value in args.prefix_ks.split(",") if value.strip())
    for task_id in task_ids:
        refs = await asyncio.gather(*(run_unit(task_id, index) for index in range(args.k)))
        task_dir = args.run_root / "cases" / task_id
        pools = freeze_nested_pools(task_dir=task_dir, trajectories=refs, prefix_ks=prefix_ks)
        task_rows.append(
            {
                "task_id": task_id,
                "failure_family": metadata[task_id]["primary_failure_family"],
                "scores": [ref.score for ref in refs],
                "provider_calls": sum(
                    len(json.loads(Path(ref.trajectory_path).read_text(encoding="utf-8"))["adapter_receipts"])
                    for ref in refs
                ),
                "pools": {
                    str(k): {
                        "pool_id": pool.pool_id,
                        "acting_success": pool.acting_success,
                        "precommitted_success": pool.precommitted_success,
                        "rescue_event": pool.rescue_event,
                        "winner_index": pool.winner.rollout_index,
                    }
                    for k, pool in pools.items()
                },
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-actor-pool-run-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED",
        "mode": args.mode,
        "suite_root": str(args.suite_root),
        "suite_manifest_sha256": file_sha256(args.suite_root / "suite_manifest.json"),
        "split_manifest_sha256": file_sha256(split_path),
        "mindmemos_root": str(args.mindmemos_root),
        "mindmemos_commit": mindmemos_commit,
        "identity_artifact": str(args.identity),
        "identity_artifact_sha256": sha256(args.identity),
        "requested_model": requested_model,
        "resolved_model": required_resolved,
        "provider_retry_limit": 0,
        "thinking": "disabled",
        "k": args.k,
        "prefix_ks": list(prefix_ks),
        "max_turns": args.max_turns,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "skill_source": str(skill_source),
        "skill_pre_sha256": skill_sha,
        "updater_receipt_path": str(args.updater_receipt) if args.updater_receipt else None,
        "updater_receipt_sha256": updater_receipt_sha,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "provider_budget": provider_budget_ledger.snapshot().to_dict() if provider_budget_ledger is not None else None,
        "tasks": task_rows,
        "scientific_outcome": args.mode != "protocol_smoke",
        "authority": {
            "paper_promotion": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--skill-source", type=Path)
    parser.add_argument("--updater-receipt", type=Path)
    parser.add_argument("--mode", choices=("protocol_smoke", "e0", "e1", "public_externality"), required=True)
    parser.add_argument("--model", choices=("deepseek-v4-pro",), default="deepseek-v4-pro")
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--lane")
    parser.add_argument("--stream-id")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--prefix-ks", default="1,2,4,8")
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--provider-budget-ledger", type=Path)
    parser.add_argument("--provider-total-call-limit", type=int)
    parser.add_argument("--provider-per-unit-call-limit", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.k < 1 or args.k > 8:
        raise SystemExit("K must be in 1..8")
    summary = asyncio.run(main_async(args))
    atomic_json(args.output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: provider_runtime_helpers | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_v31_provider_runtime_pilot.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_evidence_window_v2 import (
    ExactMatchedEvidenceBlockRenderer,
    canonical_trajectory_text,
)
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import BlindedEvidenceUnit, run_projection_update
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_search_projection_runner import (
    ProjectionName,
    SearchPool,
    project,
    project_stream,
    validate_mixed_cloned_pair,
)

PILOT_STREAM_ID = "v31-provider-runtime-pilot"
ARMS = ("win_a", "win_b", "mrw")
FORBIDDEN_VISIBLE_MARKERS = (
    "PROJECTION:",
    "ROLE:",
    "SOURCE_ROLLOUT_INDEX:",
    "SOURCE_TRAJECTORY_SHA256:",
    "ACTING_WINNER_INDEX:",
    "POOL_ID:",
)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_sha(payload: Any) -> str:
    return sha_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == "FROZEN_PROVIDER_RUNTIME_PILOT", "pilot contract not frozen")
    require(auth.get("status") == "AUTHORIZED_PROVIDER_RUNTIME_PILOT", "pilot authorization status invalid")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization/contract SHA mismatch")
    authority = auth.get("authority") or {}
    require(authority.get("provider_runtime_pilot") is True, "provider runtime pilot authority absent")
    require(authority.get("scientific_experiment") is False, "runtime pilot cannot have scientific-effect authority")
    require(authority.get("e1_b") is False, "runtime pilot cannot authorize E1-B")
    require(authority.get("paper_promotion") is False, "runtime pilot cannot authorize paper promotion")
    scope = auth.get("execution_scope") or {}
    require(scope.get("arms") == list(ARMS), "runtime pilot arm scope drift")
    require(scope.get("heldout_evaluation") is False, "runtime pilot must forbid held-out evaluation")
    require(scope.get("max_provider_calls") == int(contract["budget"]["max_provider_calls"]), "runtime pilot budget drift")
    require(scope.get("max_provider_calls_per_arm") == int(contract["budget"]["max_provider_calls_per_arm"]), "per-arm budget drift")
    runtime = contract["runtime"]
    require(scope.get("runtime_python_executable") == runtime["python_executable"], "runtime python authorization drift")
    require(scope.get("runtime_freeze_sha256") == runtime["freeze_sha256"], "runtime freeze authorization drift")
    return contract, auth


def validate_updater_runtime(contract: dict[str, Any]) -> tuple[Path, dict[str, str]]:
    runtime = contract["runtime"]
    venv = Path(runtime["venv_root"])
    runtime_python = Path(runtime["python_executable"])
    freeze_path = Path(runtime["freeze_path"])
    require(venv.is_dir(), "updater runtime venv missing")
    require(runtime_python.is_file(), "updater runtime python missing")
    require(runtime_python == venv / "bin/python", "updater runtime python is not exact venv/bin/python")
    require(freeze_path.is_file(), "updater runtime freeze missing")
    require(sha_file(freeze_path) == runtime["freeze_sha256"], "updater runtime freeze SHA drift")

    qualification_path = ROOT / runtime["qualification_path"]
    require(qualification_path.is_file(), "updater runtime qualification missing")
    require(sha_file(qualification_path) == runtime["qualification_sha256"], "updater runtime qualification SHA drift")
    qualification = load_json(qualification_path)
    require(qualification.get("status") == runtime["required_status"], "updater runtime qualification status drift")
    qualified_runtime = qualification.get("runtime") or {}
    require(qualified_runtime.get("venv_root") == str(venv), "updater runtime qualification venv drift")
    require(qualified_runtime.get("python_executable") == str(runtime_python), "updater runtime qualification python drift")
    require(qualified_runtime.get("freeze_sha256") == runtime["freeze_sha256"], "updater runtime qualification freeze drift")
    override = qualification.get("post_lock_compatibility_override") or {}
    require(override.get("present") is True, "updater runtime compatibility override declaration missing")
    require(override.get("package") == "tiktoken", "unexpected updater runtime compatibility override")
    require(override.get("qualified_runtime_version") == "0.11.0", "updater runtime tokenizer override drift")

    mind_root = Path(contract["mindmemos"]["root"])
    smoke = (
        "import sys, importlib.metadata; "
        f"root={str(mind_root)!r}; "
        "[sys.path.insert(0, root+'/'+p) for p in ['src/mindmemos','src/mindmemos_sdk','src/mindmemos_eval']]; "
        "from mindmemos.pipelines.skill.evolution import SkillEvolver; "
        "from qdrant_client import AsyncQdrantClient; "
        "import omegaconf, tiktoken; "
        "assert importlib.metadata.version('tiktoken') == '0.11.0'; "
        "print('UPDATER_RUNTIME_SMOKE_PASS')"
    )
    runtime_env = os.environ.copy()
    runtime_env["VIRTUAL_ENV"] = str(venv)
    runtime_env["PATH"] = str(venv / "bin") + os.pathsep + runtime_env.get("PATH", "")
    runtime_env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    checked = subprocess.run(
        [str(runtime_python), "-c", smoke],
        cwd=ROOT,
        env=runtime_env,
        capture_output=True,
        text=True,
        check=False,
    )
    require(checked.returncode == 0 and "UPDATER_RUNTIME_SMOKE_PASS" in checked.stdout, "dedicated updater runtime entrypoint smoke failed")
    return runtime_python, runtime_env


def bind_mindmemos(root: Path) -> None:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    for source in reversed([root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))


def load_selected_pools(contract: dict[str, Any]) -> list[SearchPool]:
    rows = contract["historical_inputs"]["selected_pools"]
    require(len(rows) == 8, "runtime pilot must bind exactly eight pools")
    pools: list[SearchPool] = []
    for row in rows:
        path = Path(row["path"])
        require(path.is_file(), f"historical pool missing: {path}")
        require(sha_file(path) == row["sha256"], f"historical pool SHA drift: {path}")
        pool = load_frozen_pool(path)
        require(pool.task_id == row["task_id"], "historical pool task binding drift")
        pools.append(pool)
    require([pool.task_id for pool in pools] == [row["task_id"] for row in rows], "historical pilot pool order drift")
    return pools


def evidence_units(
    pools: list[SearchPool],
    *,
    final_block_cap_tokens: int,
    transcript_max_chars: int,
) -> tuple[list[BlindedEvidenceUnit], list[BlindedEvidenceUnit], list[dict[str, Any]]]:
    renderer = ExactMatchedEvidenceBlockRenderer(final_block_cap_tokens=final_block_cap_tokens)
    wins: list[BlindedEvidenceUnit] = []
    mrws: list[BlindedEvidenceUnit] = []
    receipts: list[dict[str, Any]] = []
    for pool in pools:
        win_packet = project(pool, ProjectionName.WINNER_ONLY)
        mrw_packet = project(pool, ProjectionName.MIXED_REJECTED_WITNESS)
        validate_mixed_cloned_pair(pool, win_packet, mrw_packet)
        by_index = {row.rollout_index: row for row in pool.trajectories}
        win_index = win_packet.slots[0].rollout_index
        mrw_index = mrw_packet.slots[0].rollout_index
        win_ref = by_index[win_index]
        mrw_ref = by_index[mrw_index]
        win_payload = load_json(Path(win_ref.trajectory_path))
        mrw_payload = load_json(Path(mrw_ref.trajectory_path))
        require(sha_file(Path(win_ref.trajectory_path)) == win_ref.trajectory_sha256, "WIN trajectory SHA drift")
        require(sha_file(Path(mrw_ref.trajectory_path)) == mrw_ref.trajectory_sha256, "MRW trajectory SHA drift")
        win_text = canonical_trajectory_text(win_payload)
        mrw_text = canonical_trajectory_text(mrw_payload)
        win_block, mrw_block, matched = renderer.render_pair(win_text, mrw_text)
        win_tokens = len(renderer.encoding.encode(win_block))
        mrw_tokens = len(renderer.encoding.encode(mrw_block))
        require(win_tokens == mrw_tokens == matched.matched_final_block_tokens, "provider-visible token parity failed")
        require(len(f"[user] {win_block}") <= transcript_max_chars, "WIN evidence would be downstream-truncated")
        require(len(f"[user] {mrw_block}") <= transcript_max_chars, "MRW evidence would be downstream-truncated")
        for visible in (win_block, mrw_block):
            for marker in FORBIDDEN_VISIBLE_MARKERS:
                require(marker not in visible, f"arm/provenance marker leaked into model-visible evidence: {marker}")
        if not pool.mixed_pool:
            require(win_block == mrw_block, "nonmixed WIN/MRW evidence must be byte-identical")
        wins.append(
            BlindedEvidenceUnit(
                task_id=pool.task_id,
                pool_id=pool.pool_id,
                acting_winner_sha256=pool.winner.trajectory_sha256,
                source_rollout_index=win_index,
                source_trajectory_sha256=win_ref.trajectory_sha256,
                source_score=float(win_ref.score),
                evidence_text=win_block,
                evidence_sha256=sha_text(win_block),
                evidence_tokens=win_tokens,
            )
        )
        mrws.append(
            BlindedEvidenceUnit(
                task_id=pool.task_id,
                pool_id=pool.pool_id,
                acting_winner_sha256=pool.winner.trajectory_sha256,
                source_rollout_index=mrw_index,
                source_trajectory_sha256=mrw_ref.trajectory_sha256,
                source_score=float(mrw_ref.score),
                evidence_text=mrw_block,
                evidence_sha256=sha_text(mrw_block),
                evidence_tokens=mrw_tokens,
            )
        )
        receipts.append(
            {
                "task_id": pool.task_id,
                "pool_id": pool.pool_id,
                "mixed_pool": pool.mixed_pool,
                "win_source_index": win_index,
                "mrw_source_index": mrw_index,
                "win_evidence_sha256": sha_text(win_block),
                "mrw_evidence_sha256": sha_text(mrw_block),
                "matched_final_tokens": win_tokens,
                "matched_window": matched.to_dict(),
            }
        )
    return wins, mrws, receipts


def completed_manifest(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row["arm"])] = row
    return rows


def verify_completed(row: dict[str, Any], *, contract_sha: str, auth_sha: str) -> None:
    receipt_path = Path(row["update_receipt_path"])
    skill_path = Path(row["skill_post_path"])
    require(receipt_path.is_file() and skill_path.is_file(), f"completed arm artifact missing: {row['arm']}")
    require(sha_file(receipt_path) == row["update_receipt_sha256"], f"completed receipt SHA drift: {row['arm']}")
    require(sha_file(skill_path) == row["skill_post_sha256"], f"completed skill SHA drift: {row['arm']}")
    receipt = load_json(receipt_path)
    require(receipt.get("contract_sha256") == contract_sha, f"completed arm contract drift: {row['arm']}")
    require(receipt.get("authorization_sha256") == auth_sha, f"completed arm authorization drift: {row['arm']}")
    require(receipt.get("causal_purity_mode") == "arm_blinded_selected_evidence", f"completed arm not V3.1 blinded: {row['arm']}")
    require(receipt.get("arm_metadata_visible_in_transcript") is False, f"arm metadata visible: {row['arm']}")


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    contract, auth = validate_auth(args.contract, args.authorization)
    runtime_python, runtime_env = validate_updater_runtime(contract)
    require(Path(sys.executable) == runtime_python, "provider runtime pilot must itself run under contract venv python")
    os.environ.update({"VIRTUAL_ENV": runtime_env["VIRTUAL_ENV"], "PATH": runtime_env["PATH"]})

    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]
        require(path.is_file(), f"bound code missing: {label}")
        require(sha_file(path) == item["sha256"], f"bound code SHA drift: {label}")

    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.check_output(["git", "-C", str(mind_root), "rev-parse", "HEAD"], text=True).strip()
    require(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    require(not subprocess.check_output(["git", "-C", str(mind_root), "status", "--short"], text=True).strip(), "MindMemOS checkout dirty")
    bind_mindmemos(mind_root)

    identity_path = ROOT / contract["model_identity"]["path"]
    require(sha_file(identity_path) == contract["model_identity"]["sha256"], "pilot model identity SHA drift")
    identity = load_json(identity_path)
    require(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "pilot model identity not current-pass")
    model_row = identity["requested_and_resolved"][contract["updater"]["requested_model"]]
    requested = str(model_row["requested"])
    resolved = str(model_row["resolved"])
    require(resolved == contract["updater"]["resolved_model"], "pilot updater resolved-model drift")

    pools = load_selected_pools(contract)
    initial_skill_path = mind_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    require(sha_file(initial_skill_path) == contract["initial_skill"]["sha256"], "initial skill SHA drift")
    initial_skill = initial_skill_path.read_text(encoding="utf-8")
    initial_sha = sha_file(initial_skill_path)

    win_units, mrw_units, evidence_receipts = evidence_units(
        pools,
        final_block_cap_tokens=int(contract["renderer"]["final_block_cap_tokens"]),
        transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
    )
    win_unit_bundle_sha = canonical_sha([unit.__dict__ for unit in win_units])
    require(win_unit_bundle_sha == canonical_sha([unit.__dict__ for unit in win_units]), "WIN-A/WIN-B evidence bundle instability")

    win_stream = project_stream(
        stream_id=PILOT_STREAM_ID,
        initial_skill_sha256=initial_sha,
        pools=pools,
        projection=ProjectionName.WINNER_ONLY,
    )
    mrw_stream = project_stream(
        stream_id=PILOT_STREAM_ID,
        initial_skill_sha256=initial_sha,
        pools=pools,
        projection=ProjectionName.MIXED_REJECTED_WITNESS,
    )

    load_env_file(args.env_file)
    raw = ArkSettings.from_env(required=True)
    require(raw.base_url.rstrip("/") == PLAN_BASE_URL, "pilot refuses non-Ark-Plan route")
    settings = ArkSettings(
        api_key=raw.api_key,
        base_url=raw.base_url,
        default_model=raw.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )

    run_root = Path(contract["run_root"])
    run_root.mkdir(parents=True, exist_ok=True)
    lock_path = run_root / ".exclusive.lock"
    lock_handle = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        raise RuntimeError("provider runtime pilot exclusive lock already held; inspect state before any resume") from exc
    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(json.dumps({"pid": os.getpid(), "contract_sha256": sha_file(args.contract), "authorization_sha256": sha_file(args.authorization), "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}, sort_keys=True))
    lock_handle.flush()
    os.fsync(lock_handle.fileno())

    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)
    ledger_path = run_root / "checkpoints/provider_budget.sqlite3"
    ledger = ProviderBudgetLedger(
        path=ledger_path,
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        total_limit=int(contract["budget"]["max_provider_calls"]),
        per_unit_limit=int(contract["budget"]["max_provider_calls_per_arm"]),
        allow_create=not ledger_path.exists(),
    )
    manifest_path = run_root / "checkpoints/completed_arms.jsonl"
    completed = completed_manifest(manifest_path)
    for row in completed.values():
        verify_completed(row, contract_sha=contract_sha, auth_sha=auth_sha)

    arms = {
        "win_a": (win_stream, win_units),
        "win_b": (win_stream, win_units),
        "mrw": (mrw_stream, mrw_units),
    }
    rows: list[dict[str, Any]] = []
    run_success = False
    try:
        for arm in ARMS:
            if arm in completed:
                rows.append(completed[arm])
                continue
            stream, units = arms[arm]
            arm_dir = run_root / "arms" / arm
            if arm_dir.exists() and any(arm_dir.rglob("*")):
                raise RuntimeError(f"partial ambiguous arm exists without completed manifest: {arm}; do not auto-rerun")
            adapter = MindMemOSArkPlanChatAdapter(
                settings=settings,
                requested_model=requested,
                required_resolved_model=resolved,
                max_parse_attempts=int(contract["updater"]["max_parse_attempts"]),
                record_dir=arm_dir / "provider_calls",
                provider_budget_ledger=ledger,
                provider_budget_unit_id=f"{PILOT_STREAM_ID}/{arm}",
            )
            result = await run_projection_update(
                stream=stream,
                pools=pools,
                initial_skill_md=initial_skill,
                run_dir=arm_dir,
                llm_adapter=adapter,
                mindmemos_commit=head,
                contract_sha256=contract_sha,
                authorization_sha256=auth_sha,
                transcript_max_chars=int(contract["updater"]["transcript_max_chars"]),
                blinded_evidence_units=units,
            )
            receipts = adapter.public_receipts()
            claims = adapter.public_budget_claims()
            require(len(receipts) == len(claims) == result.provider_calls, f"provider claim/receipt mismatch: {arm}")
            require(all(row["provider_retry_limit"] == 0 for row in receipts), f"hidden retry limit drift: {arm}")
            require(all(float(row["temperature_requested"]) == 0.0 for row in receipts), f"temperature drift: {arm}")
            require(all((row["thinking_requested"] or "disabled") == "disabled" for row in receipts), f"thinking drift: {arm}")
            row = {
                "arm": arm,
                "status": "COMPLETED",
                "update_receipt_path": result.update_receipt_path,
                "update_receipt_sha256": result.update_receipt_sha256,
                "skill_post_path": result.skill_post_path,
                "skill_post_sha256": result.skill_post_sha256,
                "provider_calls": result.provider_calls,
                "provider_total_tokens": result.provider_total_tokens,
                "parse_error_calls": sum(int(bool(item.get("parse_error"))) for item in receipts),
                "wall_time_seconds_sum": sum(float(item.get("wall_time_seconds") or 0.0) for item in receipts),
                "prompt_sha256": [item["prompt_sha256"] for item in receipts],
                "budget_claim_count": len(claims),
                "budget_claim_bundle_sha256": canonical_sha(claims),
            }
            verify_completed(row, contract_sha=contract_sha, auth_sha=auth_sha)
            append_jsonl(manifest_path, row)
            completed[arm] = row
            rows.append(row)

        require(set(completed) == set(ARMS), "runtime pilot did not complete all three arms")
        win_a = completed["win_a"]
        win_b = completed["win_b"]
        # The initial evidence treatment is exactly identical. Hosted stochasticity may
        # make later prompts differ, so only evidence bundle identity is a hard pre-call invariant.
        budget_snapshot = ledger.snapshot()
        require(budget_snapshot.total_claimed <= int(contract["budget"]["max_provider_calls"]), "runtime pilot provider budget exceeded")
        summary = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-v31-provider-runtime-pilot-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "PASS_RUNTIME_MEASURABILITY",
            "contract_sha256": contract_sha,
            "authorization_sha256": auth_sha,
            "historical_only": True,
            "scientific_effectiveness_evaluated": False,
            "heldout_evaluation_calls": 0,
            "new_actor_rollouts": 0,
            "updater_arms": list(ARMS),
            "win_a_win_b_pre_provider_evidence_byte_identical": True,
            "win_evidence_bundle_sha256": win_unit_bundle_sha,
            "evidence_receipts": evidence_receipts,
            "arms": [completed[arm] for arm in ARMS],
            "provider_budget": budget_snapshot.to_dict(),
            "total_provider_calls": sum(int(completed[arm]["provider_calls"]) for arm in ARMS),
            "total_provider_tokens": sum(int(completed[arm]["provider_total_tokens"]) for arm in ARMS),
            "total_parse_error_calls": sum(int(completed[arm]["parse_error_calls"]) for arm in ARMS),
            "runtime_python": str(runtime_python),
            "runtime_freeze_sha256": contract["runtime"]["freeze_sha256"],
            "model_identity_sha256": contract["model_identity"]["sha256"],
            "authority": {"execute_e1_b": False, "paper_promotion": False, "submission": False},
        }
        summary_path = run_root / "summary/provider_runtime_pilot_summary.json"
        atomic_json(summary_path, summary)
        run_success = True
        return summary
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()
        if run_success:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()
    payload = asyncio.run(main_async(args))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS_RUNTIME_MEASURABILITY" else 2


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: updater_adapter | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_mindmemos_ark_adapter.py =====
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.e2_r17_provider_budget import ProviderBudgetClaim, ProviderBudgetLedger

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
REQUESTED_MODEL = "deepseek-v4-pro"
# Historical default retained only for backward-compatible callers. Every new
# E2-R17 execution tranche must pass its freshly qualified resolved identity.
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-260425"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _flatten_messages(messages: list[dict[str, Any]]) -> str:
    """Render MindMemOS chat messages into a deterministic Responses prompt.

    This adapter changes transport only. Role boundaries and content are preserved
    explicitly; SkillEvolver prompts, parsers, and update semantics remain first-party.
    """

    parts: list[str] = []
    for message in messages:
        role = str(message.get("role") or "user").upper()
        content = message.get("content")
        text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, sort_keys=True)
        parts.append(f"<{role}>\n{text}\n</{role}>")
    return "\n".join(parts)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _safe_task_name(task: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", task).strip("-")
    return cleaned or "call"


@dataclass
class AdapterUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass
class AdapterChatResponse:
    finish_reason: str
    content: str
    model: str
    usage: AdapterUsage = field(default_factory=AdapterUsage)
    parsed: Any = None
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class CallReceipt:
    call_index: int
    created_at_utc: str
    task: str
    attempt: int
    requested_model: str
    resolved_model: str
    prompt_sha256: str
    response_sha256: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    response_id_sha256: str
    provider_status: str
    thinking_requested: str | None
    temperature_requested: float
    provider_retry_limit: int
    message_count: int
    wall_time_seconds: float
    parse_error: str = ""
    record_path: str | None = None
    hidden_provider_retry_used: bool = False
    provider_budget_claim_id: int | None = None
    provider_budget_unit_call_index: int | None = None
    provider_budget_total_claimed_after: int | None = None


class MindMemOSArkPlanChatAdapter:
    """Async MindMemOS ``LLMClient.chat`` adapter over Ark Plan Responses.

    Provider retries are disabled. Parse-correction attempts are explicit and are
    counted separately because they are part of the frozen SkillEvolver updater
    policy, not part of acting compute K. When ``record_dir`` is supplied, every
    updater call is written atomically with the full prompt and response text;
    raw provider response identifiers are never persisted.
    """

    def __init__(
        self,
        *,
        settings: ArkSettings | None = None,
        requested_model: str = REQUESTED_MODEL,
        required_resolved_model: str = REQUIRED_RESOLVED_MODEL,
        max_parse_attempts: int = 3,
        record_dir: Path | str | None = None,
        provider_budget_ledger: ProviderBudgetLedger | None = None,
        provider_budget_unit_id: str | None = None,
    ) -> None:
        raw = settings or ArkSettings.from_env(required=True)
        if raw.base_url.rstrip("/") != PLAN_BASE_URL:
            raise RuntimeError("R17 adapter refuses non-Plan Ark route")
        self.settings = ArkSettings(
            api_key=raw.api_key,
            base_url=raw.base_url,
            default_model=raw.default_model,
            timeout_seconds=max(180.0, raw.timeout_seconds),
            max_retries=0,
        )
        self.client = ArkResponsesClient(self.settings)
        self.requested_model = requested_model
        self.required_resolved_model = required_resolved_model
        self.max_parse_attempts = max(1, int(max_parse_attempts))
        self.record_dir = Path(record_dir) if record_dir is not None else None
        if (provider_budget_ledger is None) != (provider_budget_unit_id is None):
            raise ValueError("provider budget ledger and unit id must be supplied together")
        self.provider_budget_ledger = provider_budget_ledger
        self.provider_budget_unit_id = str(provider_budget_unit_id) if provider_budget_unit_id is not None else None
        self.provider_budget_claims: list[ProviderBudgetClaim] = []
        self.receipts: list[CallReceipt] = []

    async def chat(
        self,
        task: str,
        messages: list[dict[str, Any]],
        format_parser: Callable[[str], Any] | None = None,
        *,
        model: str | None = None,
        feedback_on_parse_error: bool = False,
        **kwargs: Any,
    ) -> AdapterChatResponse:
        target = model or self.requested_model
        convo = list(messages)
        max_attempts = self.max_parse_attempts if format_parser is not None else 1
        last_error: Exception | None = None
        for attempt in range(max_attempts):
            prompt = _flatten_messages(convo)
            started = time.monotonic()
            result = self._respond(prompt, target=target, kwargs=kwargs)
            wall_time_seconds = time.monotonic() - started
            content = str(result.get("text") or "")
            resolved = str(result.get("resolved_model") or "")
            usage = result.get("usage") or {}
            receipt = CallReceipt(
                call_index=len(self.receipts),
                created_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                task=task,
                attempt=attempt,
                requested_model=target,
                resolved_model=resolved,
                prompt_sha256=_sha(prompt),
                response_sha256=_sha(content),
                prompt_tokens=usage.get("input_tokens"),
                completion_tokens=usage.get("output_tokens"),
                total_tokens=usage.get("total_tokens"),
                response_id_sha256=_sha(str(result.get("response_id") or "")),
                provider_status=str(result.get("status") or ""),
                thinking_requested=result.get("thinking_requested") or kwargs.get("thinking") or "disabled",
                temperature_requested=float(result.get("temperature_requested", 0.0)),
                provider_retry_limit=self.settings.max_retries,
                message_count=len(convo),
                wall_time_seconds=wall_time_seconds,
                provider_budget_claim_id=result.get("provider_budget_claim_id"),
                provider_budget_unit_call_index=result.get("provider_budget_unit_call_index"),
                provider_budget_total_claimed_after=result.get("provider_budget_total_claimed_after"),
            )
            parsed: Any = None
            if format_parser is not None:
                try:
                    parsed = format_parser(content)
                except Exception as exc:
                    last_error = exc
                    receipt.parse_error = f"{type(exc).__name__}: {exc}"
                    self._persist_call(
                        receipt=receipt,
                        messages=convo,
                        prompt=prompt,
                        content=content,
                        result=result,
                        parser_applied=True,
                        parsed=None,
                    )
                    self.receipts.append(receipt)
                    if feedback_on_parse_error and attempt + 1 < max_attempts:
                        convo.append({"role": "assistant", "content": content})
                        convo.append(
                            {
                                "role": "user",
                                "content": (
                                    "Your previous reply could not be applied:\n"
                                    f"{exc}\n\nFix exactly that problem and resend the COMPLETE corrected output "
                                    "in the same format as before. Do not apologize or add commentary."
                                ),
                            }
                        )
                    continue
            self._persist_call(
                receipt=receipt,
                messages=convo,
                prompt=prompt,
                content=content,
                result=result,
                parser_applied=format_parser is not None,
                parsed=parsed,
            )
            self.receipts.append(receipt)
            if resolved != self.required_resolved_model:
                raise RuntimeError(
                    f"resolved-model-drift:requested={target};required={self.required_resolved_model};observed={resolved}"
                )
            return AdapterChatResponse(
                finish_reason=str(result.get("status") or "completed"),
                content=content,
                model=resolved,
                usage=AdapterUsage(
                    prompt_tokens=usage.get("input_tokens"),
                    completion_tokens=usage.get("output_tokens"),
                    total_tokens=usage.get("total_tokens"),
                ),
                parsed=parsed,
                raw_response={
                    "response_id_sha256": receipt.response_id_sha256,
                    "prompt_sha256": receipt.prompt_sha256,
                    "response_sha256": receipt.response_sha256,
                    "status": result.get("status"),
                    "thinking_requested": result.get("thinking_requested"),
                    "thinking_effective": result.get("thinking_effective"),
                    "record_path": receipt.record_path,
                },
            )
        assert last_error is not None
        raise last_error

    def _persist_call(
        self,
        *,
        receipt: CallReceipt,
        messages: list[dict[str, Any]],
        prompt: str,
        content: str,
        result: dict[str, Any],
        parser_applied: bool,
        parsed: Any,
    ) -> None:
        if self.record_dir is None:
            return
        filename = f"{receipt.call_index:03d}-{_safe_task_name(receipt.task)}-attempt{receipt.attempt}.json"
        path = self.record_dir / filename
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-mindmemos-updater-provider-call",
            "created_at_utc": receipt.created_at_utc,
            "task": receipt.task,
            "attempt": receipt.attempt,
            "messages": messages,
            "prompt": prompt,
            "prompt_sha256": receipt.prompt_sha256,
            "response_text": content,
            "response_sha256": receipt.response_sha256,
            "requested_model": receipt.requested_model,
            "resolved_model": receipt.resolved_model,
            "usage": result.get("usage") or {},
            "provider_status": result.get("status"),
            "response_id_sha256": receipt.response_id_sha256,
            "thinking_requested": result.get("thinking_requested") or receipt.thinking_requested,
            "thinking_effective": result.get("thinking_effective"),
            "temperature_requested": receipt.temperature_requested,
            "provider_retry_limit": self.settings.max_retries,
            "hidden_provider_retry_used": False,
            "wall_time_seconds": receipt.wall_time_seconds,
            "provider_budget_claim_id": receipt.provider_budget_claim_id,
            "provider_budget_unit_call_index": receipt.provider_budget_unit_call_index,
            "provider_budget_total_claimed_after": receipt.provider_budget_total_claimed_after,
            "parser_applied": parser_applied,
            "parse_error": receipt.parse_error,
            "parsed_type": type(parsed).__name__ if parsed is not None else None,
            "parsed_sha256": _sha(str(parsed)) if parsed is not None else None,
            "private_credentials_included": False,
            "raw_response_id_included": False,
        }
        _atomic_json(path, payload)
        receipt.record_path = str(path.resolve())

    def _respond(self, prompt: str, *, target: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        budget_claim: ProviderBudgetClaim | None = None
        if self.provider_budget_ledger is not None:
            assert self.provider_budget_unit_id is not None
            budget_claim = self.provider_budget_ledger.claim(self.provider_budget_unit_id)
            self.provider_budget_claims.append(budget_claim)
        max_output_tokens = int(kwargs.get("max_tokens") or kwargs.get("max_completion_tokens") or 4096)
        temperature = kwargs.get("temperature")
        if temperature is None:
            # SkillEvolver's first-party summary/patch calls do not currently pass
            # an explicit temperature. Future E2-R17 causal tranches freeze that
            # otherwise provider-defined default to zero; historical receipts are
            # never regenerated under this rule.
            temperature = 0.0
        thinking = kwargs.get("thinking") or "disabled"
        try:
            result = self.client.respond(
                prompt,
                model=target,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                thinking=thinking,
                allow_thinking_compatibility_fallback=False,
            )
            result["thinking_requested"] = thinking
            result["temperature_requested"] = float(temperature)
            result.setdefault("thinking_effective", thinking)
            if budget_claim is not None:
                result["provider_budget_claim_id"] = budget_claim.claim_id
                result["provider_budget_unit_call_index"] = budget_claim.unit_call_index
                result["provider_budget_total_claimed_after"] = budget_claim.total_claimed_after
            return result
        except ArkResponseStateError as exc:
            if not exc.response_id:
                raise
            polled = self.client.poll_response(exc.response_id, max_polls=3, interval_seconds=1.0)
            if not polled.get("text"):
                raise
            result = {
                "requested_model": target,
                "resolved_model": polled.get("resolved_model"),
                "text": polled.get("text"),
                "usage": polled.get("usage") or {},
                "response_id": polled.get("response_id") or exc.response_id,
                "status": polled.get("status"),
                "thinking_requested": thinking,
                "thinking_effective": thinking,
                "get_poll_recovery": True,
            }
            if budget_claim is not None:
                result["provider_budget_claim_id"] = budget_claim.claim_id
                result["provider_budget_unit_call_index"] = budget_claim.unit_call_index
                result["provider_budget_total_claimed_after"] = budget_claim.total_claimed_after
            return result

    def public_receipts(self) -> list[dict[str, Any]]:
        return [asdict(receipt) for receipt in self.receipts]

    def public_budget_claims(self) -> list[dict[str, Any]]:
        return [claim.to_dict() for claim in self.provider_budget_claims]

    @property
    def receipt_bundle_sha256(self) -> str:
        raw = json.dumps(self.public_receipts(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return _sha(raw)


===== BOUND ARTIFACT: updater_wrapper | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_mindmemos_updater.py =====
from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_search_projection_runner import ProjectionPacket, SearchPool, StreamProjection

_ID_NAMESPACE = uuid.UUID("8a1cab2c-aef8-4eb6-bcdf-21a88b4e2f17")


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha(payload: Any) -> str:
    return sha_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _truncate_middle(text: str, limit: int) -> str:
    if limit <= 0 or len(text) <= limit:
        return text
    marker = f"\n...[{len(text) - limit} chars deterministically elided]...\n"
    usable = max(0, limit - len(marker))
    head = usable // 2
    tail = usable - head
    return text[:head] + marker + text[-tail:]


def render_trajectory_evidence(path: Path, expected_sha256: str, *, char_budget: int = 6000) -> str:
    if sha_file(path) != expected_sha256:
        raise RuntimeError(f"trajectory SHA mismatch: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    lines = [
        f"TASK_ID: {payload['case_id']}",
        f"ROLLOUT_INDEX: {payload['rollout_index']}",
        f"VERIFIER_SCORE: {payload['score']}",
        f"VERIFIER_MESSAGE: {payload.get('score_message', '')}",
        "TRAJECTORY:",
    ]
    for message in payload.get("messages") or []:
        role = str(message.get("role") or "unknown").upper()
        content = message.get("content")
        if content:
            lines.append(f"[{role}] {content}")
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            lines.append(
                f"[ASSISTANT_TOOL_CALL name={function.get('name', '')}] {function.get('arguments', '{}')}"
            )
        if role == "TOOL":
            lines.append(
                f"[TOOL_BINDING id={message.get('tool_call_id', '')} name={message.get('name', '')}]"
            )
    return _truncate_middle("\n".join(lines), char_budget)


def render_projection_packet(
    pool: SearchPool,
    packet: ProjectionPacket,
    *,
    slot_char_budget: int = 6000,
) -> tuple[str, dict[str, Any]]:
    pool.validate()
    sections = [
        "E2-R17 LEARNING PROJECTION PACKET",
        f"PROJECTION: {packet.projection}",
        f"TASK_ID: {packet.task_id}",
        f"POOL_ID: {packet.pool_id}",
        f"ACTING_WINNER_INDEX: {packet.acting_winner_index}",
        f"ACTING_WINNER_SHA256: {packet.acting_winner_sha256}",
        f"RESCUE_EVENT: {str(packet.rescue_event).lower()}",
        "The user-facing acting outcome is fixed by the acting winner above. The following slots are the only evidence exposed to the persistent updater.",
    ]
    slot_rows: list[dict[str, Any]] = []
    for slot_index, slot in enumerate(packet.slots):
        evidence = render_trajectory_evidence(
            Path(slot.trajectory_path), slot.trajectory_sha256, char_budget=slot_char_budget
        )
        sections.extend(
            [
                f"\n--- EVIDENCE SLOT {slot_index} ---",
                f"ROLE: {slot.role}",
                f"SOURCE_ROLLOUT_INDEX: {slot.rollout_index}",
                f"SOURCE_TRAJECTORY_SHA256: {slot.trajectory_sha256}",
                f"SOURCE_VERIFIER_SCORE: {slot.score}",
                evidence,
            ]
        )
        slot_rows.append(
            {
                "slot_index": slot_index,
                "role": slot.role,
                "rollout_index": slot.rollout_index,
                "trajectory_sha256": slot.trajectory_sha256,
                "score": slot.score,
                "rendered_chars": len(evidence),
                "rendered_sha256": sha_text(evidence),
            }
        )
    text = "\n".join(sections)
    metadata = {
        "packet_sha256": packet.packet_sha256,
        "projection": str(packet.projection),
        "pool_id": packet.pool_id,
        "task_id": packet.task_id,
        "acting_score": pool.acting_success,
        "rescue_event": packet.rescue_event,
        "rendered_packet_sha256": sha_text(text),
        "rendered_packet_chars": len(text),
        "slots": slot_rows,
    }
    return text, metadata


@dataclass(frozen=True)
class BlindedEvidenceUnit:
    """One pre-rendered learner-visible evidence unit for the V3.1 causal path.

    Projection/arm identity and source provenance remain available to the experiment
    receipt, but ``evidence_text`` is the only trajectory text placed in the
    first-party MindMemOS add-record ``messages`` field. ``source_score`` is the
    verifier score of that selected evidence trajectory, not the served acting
    winner score.
    """

    task_id: str
    pool_id: str
    acting_winner_sha256: str
    source_rollout_index: int
    source_trajectory_sha256: str
    source_score: float
    evidence_text: str
    evidence_sha256: str
    evidence_tokens: int

    def validate(self) -> None:
        if not self.task_id or not self.pool_id:
            raise ValueError("blinded evidence must bind task_id and pool_id")
        if self.source_rollout_index < 0:
            raise ValueError("source_rollout_index must be nonnegative")
        if sha_text(self.evidence_text) != self.evidence_sha256:
            raise ValueError("blinded evidence SHA mismatch")
        if self.evidence_tokens <= 0:
            raise ValueError("blinded evidence token count must be positive")


def build_blinded_add_record_payload(
    *,
    unit: BlindedEvidenceUnit,
    pool: SearchPool,
    project_id: str,
    task_completed_at: str,
    initial_skill_sha256: str,
    root_version_id: str,
    projection_label: str,
) -> dict[str, Any]:
    """Build the first-party add-record payload for V3.1 without treatment-label leakage.

    At pinned MindMemOS commit 9049182..., ``SkillEvolver`` constructs the LLM
    transcript from ``payload['messages']`` and obtains the scored-patch label from
    ``payload['score']``. The ``r17_*`` fields below are provenance-only and are
    intentionally absent from model-visible messages.
    """
    unit.validate()
    pool.validate()
    if unit.task_id != pool.task_id or unit.pool_id != pool.pool_id:
        raise ValueError("blinded evidence task/pool binding mismatch")
    if unit.acting_winner_sha256 != pool.winner.trajectory_sha256:
        raise ValueError("blinded evidence acting-winner provenance mismatch")
    return {
        "project_id": project_id,
        "task_completed_at": task_completed_at,
        "messages": [{"role": "user", "content": unit.evidence_text}],
        "score": float(unit.source_score),
        "task_id": pool.task_id,
        "skill_bindings": [
            {
                "name": "xlsx",
                "content_hash": initial_skill_sha256,
                "version_id": root_version_id,
                "usage": "injected",
            }
        ],
        "r17_projection": projection_label,
        "r17_rendered_packet_sha256": unit.evidence_sha256,
        "r17_pool_id": pool.pool_id,
        "r17_rescue_event": pool.rescue_event,
        "r17_acting_score": pool.acting_success,
        "r17_acting_winner_sha256": unit.acting_winner_sha256,
        "r17_source_rollout_index": unit.source_rollout_index,
        "r17_source_trajectory_sha256": unit.source_trajectory_sha256,
        "r17_selected_evidence_score": float(unit.source_score),
        "r17_evidence_tokens": int(unit.evidence_tokens),
    }


@dataclass(frozen=True)
class ProjectionUpdateResult:
    stream_id: str
    projection: str
    update_receipt_path: str
    update_receipt_sha256: str
    skill_post_path: str
    skill_post_sha256: str
    evolved: bool
    new_version_ids: tuple[str, ...]
    provider_calls: int
    provider_total_tokens: int


def _trace_uuid(stream_id: str, projection: str, task_id: str) -> str:
    return str(uuid.uuid5(_ID_NAMESPACE, f"{stream_id}|{projection}|{task_id}"))


async def run_projection_update(
    *,
    stream: StreamProjection,
    pools: Sequence[SearchPool],
    initial_skill_md: str,
    run_dir: Path,
    llm_adapter: Any,
    mindmemos_commit: str,
    contract_sha256: str,
    authorization_sha256: str,
    slot_char_budget: int = 6000,
    transcript_max_chars: int = 16000,
    blinded_evidence_units: Sequence[BlindedEvidenceUnit] | None = None,
) -> ProjectionUpdateResult:
    """Run one cloned MindMemOS SkillEvolver update from eight projected task packets.

    ``blinded_evidence_units`` activates the V3.1 causal-purity path. In that mode
    the first-party updater receives only the pre-rendered arm-blinded evidence
    text plus the selected evidence trajectory's verifier score. Acting winner,
    projection label, rollout index and SHA provenance remain database/receipt
    metadata and are not placed in the model-visible transcript.
    """

    if len(stream.packets) != 8 or len(pools) != 8:
        raise ValueError("one E2-R17 update unit must contain exactly eight task pools")
    if [pool.pool_id for pool in pools] != [pool.pool_id for pool in stream.pools]:
        raise ValueError("stream pools differ from supplied exact pools")
    run_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = run_dir / "update_receipt.json"
    skill_path = run_dir / "skill_post" / "SKILL.md"
    if receipt_path.exists() and skill_path.exists():
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        if sha_file(skill_path) != payload.get("skill_post_sha256"):
            raise RuntimeError("existing updater receipt failed skill content-address check")
        return ProjectionUpdateResult(
            stream_id=stream.stream_id,
            projection=str(stream.projection),
            update_receipt_path=str(receipt_path.resolve()),
            update_receipt_sha256=sha_file(receipt_path),
            skill_post_path=str(skill_path.resolve()),
            skill_post_sha256=sha_file(skill_path),
            evolved=bool(payload.get("evolved")),
            new_version_ids=tuple(payload.get("new_version_ids") or []),
            provider_calls=len(payload.get("adapter_receipts") or []),
            provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in payload.get("adapter_receipts") or []),
        )

    # Imports remain inside the function so the caller can bind the exact
    # MindMemOS source tree before loading this module.
    from mindmemos.components.skill import deserialize_bundle, serialize_bundle
    from mindmemos.config import QdrantConfig, SkillEvolutionConfig
    from mindmemos.infra.db import SkillVersionRepository
    from mindmemos.infra.db.models import AddRecordPoint
    from mindmemos.infra.db.qdrant import QdrantStore
    from mindmemos.pipelines.skill import SkillVersionStore
    from mindmemos.pipelines.skill import evolution as evolution_module
    from mindmemos.pipelines.skill.evolution import SkillEvolver
    from qdrant_client import AsyncQdrantClient

    packet_rows: list[dict[str, Any]] = []
    rendered_packets: list[tuple[str, dict[str, Any]]] = []
    blinded_rows: list[BlindedEvidenceUnit] | None = None
    if blinded_evidence_units is not None:
        blinded_rows = list(blinded_evidence_units)
        if len(blinded_rows) != len(pools):
            raise ValueError("blinded evidence cardinality must match the eight exact pools")
        for pool, unit in zip(pools, blinded_rows):
            unit.validate()
            if unit.task_id != pool.task_id or unit.pool_id != pool.pool_id:
                raise ValueError("blinded evidence task/pool binding mismatch")
            if unit.acting_winner_sha256 != pool.winner.trajectory_sha256:
                raise ValueError("blinded evidence acting-winner provenance mismatch")
            if len(f"[user] {unit.evidence_text}") > transcript_max_chars:
                raise ValueError("blinded evidence would be silently truncated by first-party transcript renderer")
            metadata = {
                "packet_sha256": sha_text(unit.evidence_text),
                "projection": str(stream.projection),
                "pool_id": unit.pool_id,
                "task_id": unit.task_id,
                "acting_score": pool.acting_success,
                "acting_winner_sha256": unit.acting_winner_sha256,
                "source_rollout_index": unit.source_rollout_index,
                "source_trajectory_sha256": unit.source_trajectory_sha256,
                "source_score": unit.source_score,
                "rendered_packet_sha256": unit.evidence_sha256,
                "rendered_packet_chars": len(unit.evidence_text),
                "rendered_packet_tokens": unit.evidence_tokens,
                "arm_metadata_visible": False,
                "score_semantics": "selected_evidence_trajectory",
            }
            rendered_packets.append((unit.evidence_text, metadata))
            packet_rows.append(metadata)
    else:
        for pool, packet in zip(pools, stream.packets):
            text, metadata = render_projection_packet(pool, packet, slot_char_budget=slot_char_budget)
            rendered_packets.append((text, metadata))
            packet_rows.append(metadata)

    client = AsyncQdrantClient(":memory:")
    qdrant_cfg = QdrantConfig(
        url="http://unused",
        add_record_collection="r17_add_record",
        skill_version_collection="r17_skill_version",
        skill_blob_collection="r17_skill_blob",
        skill_trace_pending_collection="r17_skill_trace_pending",
        skill_trace_summary_collection="r17_skill_trace_summary",
        vector_size=2,
    )
    qdrant = QdrantStore(qdrant_cfg, client=client)
    await qdrant.ensure_schema()
    skill_repo = SkillVersionRepository(qdrant_cfg, engine=qdrant.engine)
    await skill_repo.ensure_schema()
    store = SkillVersionStore(skill_repo=skill_repo, add_record_repo=qdrant.add_record)
    evolver = SkillEvolver(
        store=store,
        skill_repo=skill_repo,
        add_record_repo=qdrant.add_record,
        llm_client=llm_adapter,
    )
    project_id = f"e2-r17-{stream.stream_id}-{stream.projection}"
    root = await store.register(
        project_id=project_id,
        name="xlsx",
        content=serialize_bundle({"SKILL.md": initial_skill_md}),
    )
    base_time = datetime(2026, 8, 28, tzinfo=UTC)
    for index, ((packet_text, packet_meta), pool) in enumerate(zip(rendered_packets, pools)):
        selected_score = (
            float(blinded_rows[index].source_score)
            if blinded_rows is not None
            else float(pool.acting_success)
        )
        if blinded_rows is not None:
            payload = build_blinded_add_record_payload(
                unit=blinded_rows[index],
                pool=pool,
                project_id=project_id,
                task_completed_at=(base_time + timedelta(minutes=index)).isoformat(),
                initial_skill_sha256=stream.initial_skill_sha256,
                root_version_id=root.version_id,
                projection_label=str(stream.projection),
            )
            if float(payload["score"]) != selected_score:
                raise AssertionError("V3.1 selected-evidence score serialization drift")
        else:
            payload = {
                "project_id": project_id,
                "task_completed_at": (base_time + timedelta(minutes=index)).isoformat(),
                "messages": [{"role": "user", "content": packet_text}],
                "score": selected_score,
                "task_id": pool.task_id,
                "skill_bindings": [
                    {
                        "name": "xlsx",
                        "content_hash": stream.initial_skill_sha256,
                        "version_id": root.version_id,
                        "usage": "injected",
                    }
                ],
                "r17_projection": str(stream.projection),
                "r17_projection_packet_sha256": packet_meta["packet_sha256"],
                "r17_rendered_packet_sha256": packet_meta["rendered_packet_sha256"],
                "r17_pool_id": pool.pool_id,
                "r17_rescue_event": pool.rescue_event,
            }
        await qdrant.upsert_add_record(
            AddRecordPoint(
                add_record_id=_trace_uuid(stream.stream_id, str(stream.projection), pool.task_id),
                payload=payload,
            )
        )

    frozen_cfg = SkillEvolutionConfig(
        min_aggregate=8,
        max_aggregate=8,
        summary_concurrency=4,
        rewrite_skill=False,
        use_trajectory_score=True,
        evolved_status="draft",
        transcript_max_chars=transcript_max_chars,
        max_trace_scan=100,
    )

    class _Algo:
        skill_evolution = frozen_cfg

    class _Config:
        algo_config = _Algo()

    original_get_config = evolution_module.get_config
    evolution_module.get_config = lambda: _Config()
    try:
        update = await evolver.evolve(project_id=project_id, cloud_skill_id=root.cloud_skill_id)
        summaries = await evolver._existing_summaries(project_id, root.cloud_skill_id)
    finally:
        evolution_module.get_config = original_get_config

    try:
        if not update.evolved or not update.new_version_id:
            raise RuntimeError(
                f"first-party SkillEvolver did not mint a version: pending={update.pending_count}; "
                f"summarized={update.summarized_count}"
            )
        if len(update.new_version_ids) != 1 or update.consumed_count != 8:
            raise RuntimeError("R17 frozen updater must mint exactly one version from eight task packets")
        post = await store.get_content(
            project_id=project_id,
            cloud_skill_id=root.cloud_skill_id,
            version_id=update.new_version_id,
        )
        skill_post_md = deserialize_bundle(post.content)["SKILL.md"]
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        temp_skill = skill_path.with_suffix(".md.tmp")
        temp_skill.write_text(skill_post_md, encoding="utf-8")
        os.replace(temp_skill, skill_path)
        adapter_receipts = llm_adapter.public_receipts()
        summary_rows = [
            {
                "summary_id": item.summary_id,
                "add_record_id": item.add_record_id,
                "task_id": item.task_id,
                "score": item.score,
                "summary": item.summary,
                "summary_sha256": sha_text(item.summary),
                "consumed_version_id": item.consumed_version_id,
            }
            for item in sorted(summaries.values(), key=lambda row: (str(row.task_id), row.summary_id))
        ]
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-cloned-state-mindmemos-update",
            "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "status": "COMPLETED",
            "stream_id": stream.stream_id,
            "stream_sha256": stream.stream_sha256,
            "projection": str(stream.projection),
            "initial_skill_sha256": stream.initial_skill_sha256,
            "skill_post_path": str(skill_path.resolve()),
            "skill_post_sha256": sha_file(skill_path),
            "mindmemos_commit": mindmemos_commit,
            "first_party_updater": "mindmemos.pipelines.skill.evolution.SkillEvolver",
            "updater_config": asdict(frozen_cfg),
            "project_id": project_id,
            "root_version_id": root.version_id,
            "cloud_skill_id": root.cloud_skill_id,
            "evolved": update.evolved,
            "new_version_id": update.new_version_id,
            "new_version_ids": update.new_version_ids,
            "summarized_count": update.summarized_count,
            "consumed_count": update.consumed_count,
            "pending_count": update.pending_count,
            "packets": packet_rows,
            "summaries": summary_rows,
            "adapter_receipts": adapter_receipts,
            "adapter_receipt_bundle_sha256": llm_adapter.receipt_bundle_sha256,
            "contract_sha256": contract_sha256,
            "authorization_sha256": authorization_sha256,
            "provider_retry_limit": 0,
            "hidden_provider_retry_used": False,
            "causal_purity_mode": "arm_blinded_selected_evidence" if blinded_rows is not None else "legacy_projection_packet",
            "updater_visible_score_semantics": "selected_evidence_trajectory" if blinded_rows is not None else "served_acting_outcome_legacy",
            "arm_metadata_visible_in_transcript": False if blinded_rows is not None else True,
            "private_credentials_included": False,
            "raw_response_ids_included": False,
        }
        atomic_json(receipt_path, payload)
    finally:
        await client.close()

    return ProjectionUpdateResult(
        stream_id=stream.stream_id,
        projection=str(stream.projection),
        update_receipt_path=str(receipt_path.resolve()),
        update_receipt_sha256=sha_file(receipt_path),
        skill_post_path=str(skill_path.resolve()),
        skill_post_sha256=sha_file(skill_path),
        evolved=True,
        new_version_ids=tuple(update.new_version_ids),
        provider_calls=len(adapter_receipts),
        provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in adapter_receipts),
    )


__all__ = [
    "BlindedEvidenceUnit",
    "build_blinded_add_record_payload",
    "ProjectionUpdateResult",
    "render_projection_packet",
    "render_trajectory_evidence",
    "run_projection_update",
]


===== BOUND ARTIFACT: renderer | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_evidence_window_v2.py =====
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
from typing import Any, Mapping, Sequence


TOKENIZER_PACKAGE = "tiktoken"
TOKENIZER_VERSION = "0.11.0"
TOKENIZER_ENCODING = "cl100k_base"
FINAL_BLOCK_CAP_TOKENS = 3072
HEAD_FRACTION = 1.0 / 3.0
MIN_SELECTED_SOURCE_TOKENS = 64
BLOCK_HEADER = "E2-R17 SELECTED EXPERIENCE\n<EVIDENCE_HEAD>\n"
BLOCK_BOUNDARY = "\n</EVIDENCE_HEAD>\n<EVIDENCE_TAIL>\n"
BLOCK_FOOTER = "\n</EVIDENCE_TAIL>"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_trajectory_text(payload: Mapping[str, Any]) -> str:
    """Canonical branch evidence shown to the updater.

    Arm/projection identity, rollout index, provider metadata, paths, receipts and
    the common system prompt are deliberately absent.  The verifier score/message
    remain because whether the selected experience succeeded or failed is part of
    the scientific evidence treatment itself.
    """
    messages: list[dict[str, Any]] = []
    for message in payload.get("messages") or []:
        if not isinstance(message, Mapping):
            continue
        if str(message.get("role") or "") == "system":
            continue
        messages.append(dict(message))
    return json.dumps(
        {
            "messages": messages,
            "score": payload.get("score"),
            "score_message": payload.get("score_message"),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _safe_decode(encoding: Any, tokens: Sequence[int]) -> str:
    """Decode a token slice without inserting Unicode replacement characters."""
    if hasattr(encoding, "decode_bytes"):
        return encoding.decode_bytes(list(tokens)).decode("utf-8", errors="ignore")
    return encoding.decode(list(tokens))


def _candidate_block(encoding: Any, raw_tokens: Sequence[int], selected_budget: int) -> tuple[str, int]:
    if selected_budget < 2:
        raise ValueError("selected_budget must be at least two tokens")
    tokens = list(raw_tokens)
    selected_budget = min(int(selected_budget), len(tokens))
    head = max(1, int(selected_budget * HEAD_FRACTION))
    tail = selected_budget - head
    if tail < 1:
        tail = 1
        head = selected_budget - 1

    if selected_budget >= len(tokens):
        # Preserve all source tokens in order; the explicit boundary marker is
        # inserted at the deterministic one-third point for both arms.
        head_tokens = tokens[:head]
        tail_tokens = tokens[head:]
    else:
        head_tokens = tokens[:head]
        tail_tokens = tokens[-tail:]

    text = (
        BLOCK_HEADER
        + _safe_decode(encoding, head_tokens)
        + BLOCK_BOUNDARY
        + _safe_decode(encoding, tail_tokens)
        + BLOCK_FOOTER
    )
    actual = len(encoding.encode(text))
    return text, actual


@dataclass(frozen=True)
class ExactMatchedBlockReceipt:
    tokenizer_package: str
    tokenizer_version: str
    tokenizer_encoding: str
    final_block_cap_tokens: int
    head_fraction: float
    min_selected_source_tokens: int
    left_raw_source_tokens: int
    right_raw_source_tokens: int
    left_selected_source_tokens: int
    right_selected_source_tokens: int
    matched_final_block_tokens: int
    left_block_sha256: str
    right_block_sha256: str
    search_lower_bound: int
    search_candidates_left: int
    search_candidates_right: int
    padding_used: bool
    arm_metadata_visible: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExactMatchedEvidenceBlockRenderer:
    """Render two evidence blocks to the same *actual re-tokenized* length.

    V3's nominal token slicing failed because decoding and concatenating head/tail
    slices can create a fresh BPE merge at the splice.  V3.1 therefore searches
    deterministic source-token budgets for each arm and accepts only a pair whose
    final rendered UTF-8 texts re-encode to exactly the same token count under the
    frozen tokenizer.  No padding is used.  The largest common reachable final
    token count not exceeding `final_block_cap_tokens` is selected.

    The updater-visible wrapper is identical and arm-blinded.  Projection name,
    role, rollout index and provenance remain in receipts rather than the text the
    updater reasons over.
    """

    def __init__(self, *, final_block_cap_tokens: int = FINAL_BLOCK_CAP_TOKENS) -> None:
        if final_block_cap_tokens < MIN_SELECTED_SOURCE_TOKENS:
            raise ValueError("final block cap is too small")
        try:
            observed = importlib.metadata.version(TOKENIZER_PACKAGE)
        except importlib.metadata.PackageNotFoundError as exc:
            raise RuntimeError(
                f"{TOKENIZER_PACKAGE}=={TOKENIZER_VERSION} is required for the frozen E2-R17 V3.1 renderer"
            ) from exc
        if observed != TOKENIZER_VERSION:
            raise RuntimeError(
                f"frozen E2-R17 V3.1 renderer requires {TOKENIZER_PACKAGE}=={TOKENIZER_VERSION}, observed {observed}"
            )
        import tiktoken  # type: ignore

        self.encoding = tiktoken.get_encoding(TOKENIZER_ENCODING)
        self.final_block_cap_tokens = int(final_block_cap_tokens)

    def _reachable(
        self,
        raw_tokens: Sequence[int],
        *,
        start_budget: int,
        lower_bound: int,
    ) -> dict[int, tuple[int, str]]:
        reachable: dict[int, tuple[int, str]] = {}
        for budget in range(start_budget, lower_bound - 1, -1):
            text, actual = _candidate_block(self.encoding, raw_tokens, budget)
            if actual > self.final_block_cap_tokens:
                continue
            # For a given actual provider-visible length, keep the largest source
            # budget so the deterministic rule retains maximal evidence.
            reachable.setdefault(actual, (budget, text))
        return reachable

    def render_pair(self, left_text: str, right_text: str) -> tuple[str, str, ExactMatchedBlockReceipt]:
        left_raw = self.encoding.encode(left_text)
        right_raw = self.encoding.encode(right_text)
        if len(left_raw) < MIN_SELECTED_SOURCE_TOKENS or len(right_raw) < MIN_SELECTED_SOURCE_TOKENS:
            raise ValueError("both source evidences must contain at least 64 tokens")

        start = min(len(left_raw), len(right_raw), self.final_block_cap_tokens)
        # Search progressively wider deterministic windows.  The result is the
        # maximum common actual re-tokenized length, never a first-hit dependent
        # on arm order.
        lower_bounds = []
        for width in (32, 128, 512, 1024, start):
            lower = max(MIN_SELECTED_SOURCE_TOKENS, start - int(width))
            if not lower_bounds or lower != lower_bounds[-1]:
                lower_bounds.append(lower)
        if lower_bounds[-1] != MIN_SELECTED_SOURCE_TOKENS:
            lower_bounds.append(MIN_SELECTED_SOURCE_TOKENS)

        chosen: tuple[int, int, str, str, int, int, int] | None = None
        for lower in lower_bounds:
            left_map = self._reachable(left_raw, start_budget=start, lower_bound=lower)
            right_map = self._reachable(right_raw, start_budget=start, lower_bound=lower)
            common = set(left_map).intersection(right_map)
            if common:
                matched = max(common)
                left_budget, left_block = left_map[matched]
                right_budget, right_block = right_map[matched]
                chosen = (
                    left_budget,
                    right_budget,
                    left_block,
                    right_block,
                    matched,
                    len(left_map),
                    len(right_map),
                )
                search_lower_bound = lower
                break
        if chosen is None:
            raise RuntimeError("no exact common re-tokenized evidence-block length is reachable without padding")

        left_budget, right_budget, left_block, right_block, matched, left_n, right_n = chosen
        left_actual = len(self.encoding.encode(left_block))
        right_actual = len(self.encoding.encode(right_block))
        if left_actual != right_actual or left_actual != matched:
            raise AssertionError("V3.1 exact re-tokenized parity invariant failed")
        if matched > self.final_block_cap_tokens:
            raise AssertionError("V3.1 final block exceeded frozen cap")

        receipt = ExactMatchedBlockReceipt(
            tokenizer_package=TOKENIZER_PACKAGE,
            tokenizer_version=TOKENIZER_VERSION,
            tokenizer_encoding=TOKENIZER_ENCODING,
            final_block_cap_tokens=self.final_block_cap_tokens,
            head_fraction=HEAD_FRACTION,
            min_selected_source_tokens=MIN_SELECTED_SOURCE_TOKENS,
            left_raw_source_tokens=len(left_raw),
            right_raw_source_tokens=len(right_raw),
            left_selected_source_tokens=left_budget,
            right_selected_source_tokens=right_budget,
            matched_final_block_tokens=matched,
            left_block_sha256=sha256_text(left_block),
            right_block_sha256=sha256_text(right_block),
            search_lower_bound=search_lower_bound,
            search_candidates_left=left_n,
            search_candidates_right=right_n,
            padding_used=False,
            arm_metadata_visible=False,
        )
        return left_block, right_block, receipt


===== BOUND ARTIFACT: provider_budget | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_provider_budget.py =====
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any


SCHEMA_VERSION = "1.0"


class ProviderBudgetExceeded(RuntimeError):
    """Raised before provider I/O when a frozen call ceiling would be exceeded."""


class ProviderBudgetBindingError(RuntimeError):
    """Raised when a persisted ledger does not match the frozen execution binding."""


@dataclass(frozen=True)
class ProviderBudgetClaim:
    claim_id: int
    unit_id: str
    unit_call_index: int
    total_claimed_after: int
    per_unit_limit: int
    total_limit: int
    claimed_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderBudgetSnapshot:
    ledger_path: str
    contract_sha256: str
    authorization_sha256: str
    total_limit: int
    per_unit_limit: int
    total_claimed: int
    unit_claimed: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProviderBudgetLedger:
    """SQLite-backed fail-closed provider-call budget ledger.

    A claim is committed transactionally *before* provider I/O. Claims are never
    released, even when the subsequent provider request errors or the process
    crashes. This deliberately over-counts ambiguous calls so a resume cannot
    reset or reuse budget that may already have reached the provider.

    SQLite ``BEGIN IMMEDIATE`` serializes concurrent claims from the per-stream
    actor workers. The ledger is bound to one exact contract/authorization pair
    and fixed global/per-unit limits; any drift fails closed.
    """

    def __init__(
        self,
        *,
        path: Path,
        contract_sha256: str,
        authorization_sha256: str,
        total_limit: int,
        per_unit_limit: int,
        allow_create: bool,
    ) -> None:
        if total_limit <= 0 or per_unit_limit <= 0:
            raise ValueError("provider budget limits must be positive")
        self.path = Path(path)
        self.contract_sha256 = str(contract_sha256)
        self.authorization_sha256 = str(authorization_sha256)
        self.total_limit = int(total_limit)
        self.per_unit_limit = int(per_unit_limit)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existed = self.path.exists()
        if not existed and not allow_create:
            raise ProviderBudgetBindingError(f"provider budget ledger does not exist: {self.path}")
        self._initialize_or_validate(allow_create=allow_create)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.path), timeout=30.0, isolation_level=None)
        connection.execute("PRAGMA busy_timeout=30000")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize_or_validate(self, *, allow_create: bool) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS claims (
                    claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id TEXT NOT NULL,
                    unit_call_index INTEGER NOT NULL,
                    claimed_at_utc TEXT NOT NULL,
                    UNIQUE(unit_id, unit_call_index)
                )
                """
            )
            current = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if not current:
                if not allow_create:
                    connection.execute("ROLLBACK")
                    raise ProviderBudgetBindingError("refusing to initialize missing provider budget metadata on resume")
                connection.executemany(
                    "INSERT INTO metadata(key, value) VALUES (?, ?)", expected.items()
                )
            elif current != expected:
                connection.execute("ROLLBACK")
                raise ProviderBudgetBindingError(
                    f"provider budget binding drift: observed={current!r}; expected={expected!r}"
                )
            connection.execute("COMMIT")

    def claim(self, unit_id: str) -> ProviderBudgetClaim:
        unit_id = str(unit_id)
        if not unit_id:
            raise ValueError("provider budget unit_id is required")
        claimed_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            metadata = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if metadata != expected:
                connection.execute("ROLLBACK")
                raise ProviderBudgetBindingError("provider budget metadata drift before claim")
            total_claimed = int(connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            unit_claimed = int(
                connection.execute("SELECT COUNT(*) FROM claims WHERE unit_id=?", (unit_id,)).fetchone()[0]
            )
            if total_claimed >= self.total_limit:
                connection.execute("ROLLBACK")
                raise ProviderBudgetExceeded(
                    f"provider total call budget exhausted before I/O: {total_claimed}/{self.total_limit}"
                )
            if unit_claimed >= self.per_unit_limit:
                connection.execute("ROLLBACK")
                raise ProviderBudgetExceeded(
                    f"provider per-unit call budget exhausted before I/O: unit={unit_id}; "
                    f"{unit_claimed}/{self.per_unit_limit}"
                )
            unit_call_index = unit_claimed + 1
            cursor = connection.execute(
                "INSERT INTO claims(unit_id, unit_call_index, claimed_at_utc) VALUES (?, ?, ?)",
                (unit_id, unit_call_index, claimed_at),
            )
            claim_id = int(cursor.lastrowid)
            connection.execute("COMMIT")
        return ProviderBudgetClaim(
            claim_id=claim_id,
            unit_id=unit_id,
            unit_call_index=unit_call_index,
            total_claimed_after=total_claimed + 1,
            per_unit_limit=self.per_unit_limit,
            total_limit=self.total_limit,
            claimed_at_utc=claimed_at,
        )

    def snapshot(self) -> ProviderBudgetSnapshot:
        with self._connect() as connection:
            metadata = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if metadata != expected:
                raise ProviderBudgetBindingError("provider budget metadata drift while reading snapshot")
            total_claimed = int(connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            unit_rows = connection.execute(
                "SELECT unit_id, COUNT(*) FROM claims GROUP BY unit_id ORDER BY unit_id"
            ).fetchall()
        return ProviderBudgetSnapshot(
            ledger_path=str(self.path),
            contract_sha256=self.contract_sha256,
            authorization_sha256=self.authorization_sha256,
            total_limit=self.total_limit,
            per_unit_limit=self.per_unit_limit,
            total_claimed=total_claimed,
            unit_claimed={str(unit_id): int(count) for unit_id, count in unit_rows},
        )

    def assert_completed_receipts_covered(self, completed_receipt_counts: dict[str, int]) -> None:
        snapshot = self.snapshot()
        for unit_id, observed_receipts in completed_receipt_counts.items():
            claimed = int(snapshot.unit_claimed.get(str(unit_id), 0))
            if claimed < int(observed_receipts):
                raise ProviderBudgetBindingError(
                    f"persisted provider receipts exceed budget claims: unit={unit_id}; "
                    f"receipts={observed_receipts}; claims={claimed}"
                )


__all__ = [
    "ProviderBudgetBindingError",
    "ProviderBudgetClaim",
    "ProviderBudgetExceeded",
    "ProviderBudgetLedger",
    "ProviderBudgetSnapshot",
    "SCHEMA_VERSION",
]


===== BOUND ARTIFACT: actor_runtime_validator | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_e1_a_pool_support.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger

ACTOR = ROOT / "scripts/run_e2_r17_actor_pool.py"
EXPECTED_AUTH_STATUS = "AUTHORIZED_E1"
EXPECTED_CONTRACT_STATUS = "FROZEN_E1_A_POOL_SUPPORT"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def manifest_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[str(row["stream_id"])] = row
    return rows


def verify_stream_receipt(
    row: dict[str, Any],
    run_root: Path,
    provider_budget_ledger: ProviderBudgetLedger | None = None,
) -> None:
    summary_path = Path(row["summary_path"])
    require(summary_path.exists(), f"missing completed stream summary: {summary_path}")
    require(sha_file(summary_path) == row["summary_sha256"], f"completed stream summary SHA drift: {row['stream_id']}")
    summary = load_json(summary_path)
    require(summary.get("status") == "COMPLETED", f"stream summary not completed: {row['stream_id']}")
    tasks = summary.get("tasks") or []
    require(len(tasks) == 8, f"completed stream does not contain eight tasks: {row['stream_id']}")
    for task in tasks:
        task_id = str(task["task_id"])
        task_dir = run_root / "cases" / task_id
        for k in (1, 2, 4, 8):
            pool = task_dir / f"pool_k{k}.json"
            require(pool.exists(), f"missing frozen K={k} pool for {task_id}")
        for rollout in range(8):
            ref = task_dir / f"rollout_{rollout}" / "r17_trajectory_ref.json"
            require(ref.exists(), f"missing trajectory ref {task_id}/{rollout}")
            ref_payload = load_json(ref)
            trajectory = Path(ref_payload["trajectory_path"])
            require(trajectory.exists(), f"missing trajectory bound by {ref}")
            require(sha_file(trajectory) == ref_payload["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{rollout}")
            if provider_budget_ledger is not None:
                unit_id = f"{task_id}/rollout_{rollout}"
                require(ref_payload.get("provider_budget_unit_id") == unit_id, f"provider budget unit id drift: {unit_id}")
                claim_count = int(ref_payload.get("provider_budget_claim_count") or 0)
                require(claim_count >= 1, f"completed E1-A rollout lacks provider budget claims: {unit_id}")
                raw = load_json(trajectory)
                claims = raw.get("provider_budget_claims") or []
                require(len(claims) == claim_count, f"provider budget claim count drift: {unit_id}")
                claim_sha = hashlib.sha256(
                    json.dumps(claims, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest()
                require(claim_sha == ref_payload.get("provider_budget_claim_bundle_sha256"), f"provider budget claim SHA drift: {unit_id}")
                snapshot = provider_budget_ledger.snapshot()
                unit_claimed = int(snapshot.unit_claimed.get(unit_id, 0))
                require(
                    unit_claimed == int(ref_payload.get("provider_budget_unit_claimed_after") or -1),
                    f"provider budget ledger/ref unit count drift: {unit_id}",
                )
                require(
                    snapshot.total_claimed >= int(ref_payload.get("provider_budget_total_claimed_after") or -1),
                    f"provider budget total counter regressed: {unit_id}",
                )


def acquire_lock(path: Path, *, contract_sha: str, authorization_sha: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(
            f"exclusive lock already exists: {path}; inspect process/checkpoints before any resume"
        ) from exc
    payload = {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
    }
    os.write(fd, (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))
    os.fsync(fd)
    return fd


def validate_runtime(contract: dict[str, Any]) -> tuple[Path, dict[str, str]]:
    runtime = contract.get("runtime") or {}
    venv = Path(str(runtime.get("venv_root") or ""))
    python = Path(str(runtime.get("python_executable") or ""))
    freeze = Path(str(runtime.get("freeze_path") or ""))
    qualification = Path(str(runtime.get("qualification_path") or ""))
    require(venv.is_dir(), f"frozen runtime venv missing: {venv}")
    require(python.is_file(), f"frozen runtime python missing: {python}")
    require(python == venv / "bin/python", "runtime python must be exact venv/bin/python")
    require(freeze.is_file(), f"runtime freeze missing: {freeze}")
    require(sha_file(freeze) == runtime.get("freeze_sha256"), "runtime freeze SHA drift")
    require(qualification.is_file(), f"runtime qualification artifact missing: {qualification}")
    require(sha_file(qualification) == runtime.get("qualification_sha256"), "runtime qualification SHA drift")
    q = load_json(qualification)
    require(q.get("status") == "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2", "runtime qualification status invalid")
    require(q.get("venv_root") == str(venv), "runtime qualification venv drift")
    require(q.get("freeze_sha256") == runtime.get("freeze_sha256"), "runtime qualification freeze drift")
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv)
    env["PATH"] = str(venv / "bin") + os.pathsep + env.get("PATH", "")
    smoke = subprocess.run(
        [
            str(python),
            "-c",
            (
                "import openpyxl,pydantic; "
                "assert openpyxl.__version__ == '3.1.5'; "
                "from mindmemos_eval.skills.agents import ReactAgentFactory; "
                "from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv"
            ),
        ],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    require(smoke.returncode == 0, "frozen full MindMemOS runtime import smoke failed")
    return python, env


def validate_contract_and_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == EXPECTED_CONTRACT_STATUS, "E1-A contract is not frozen")
    require(auth.get("status") == EXPECTED_AUTH_STATUS, "E1-A authorization status invalid")
    require(auth.get("authority", {}).get("scientific_experiment") is True, "E1-A scientific authority false")
    require(auth.get("authority", {}).get("e1_a") is True, "E1-A authority bit false")
    require(auth.get("authority", {}).get("e1_b") is False, "E1-A authorization must not inherit E1-B")
    require(auth.get("authority", {}).get("paper_promotion") is False, "E1-A authorization must not promote paper")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization does not bind exact E1-A contract")
    return contract, auth


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()

    contract, auth = validate_contract_and_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)

    for label, item in (contract.get("bound_code") or {}).items():
        path = ROOT / item["path"]
        require(path.exists() and sha_file(path) == item["sha256"], f"bound code drift: {label}")
    identity = ROOT / contract["model_identity"]["path"]
    require(identity.exists() and sha_file(identity) == contract["model_identity"]["sha256"], "model identity artifact drift")
    identity_payload = load_json(identity)
    require(identity_payload.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "actor model identity adjudication not passing")

    suite_root = Path(contract["suite"]["root"])
    split_path = suite_root / "r17_split_manifest.json"
    require(sha_file(suite_root / "suite_manifest.json") == contract["suite"]["suite_manifest_sha256"], "suite manifest drift")
    require(sha_file(split_path) == contract["suite"]["split_manifest_sha256"], "split manifest drift")
    require(sha_file(suite_root / "r17_controlled_metadata.json") == contract["suite"]["metadata_sha256"], "controlled metadata drift")
    split = load_json(split_path)
    streams = split["e1_update_streams"]
    frozen_stream_ids = list(contract["streams"])
    require(list(streams.keys()) == frozen_stream_ids, "stream ordering/content drift from frozen contract")
    all_tasks = [str(task) for stream_id in frozen_stream_ids for task in streams[stream_id]]
    require(len(all_tasks) == 96 and len(set(all_tasks)) == 96, "E1-A must bind 96 unique update tasks")
    scope = auth.get("execution_scope") or {}
    require(set(scope.get("allowed_task_ids") or []) == set(all_tasks), "authorization task scope does not equal frozen 96 tasks")
    require(scope.get("allowed_modes") == ["e1"], "authorization mode scope must be exactly e1")
    require(int(scope.get("exact_k")) == 8, "authorization must bind exact K=8")
    runtime = contract.get("runtime") or {}
    require(
        scope.get("runtime_python_executable") == runtime.get("python_executable"),
        "authorization runtime python drift",
    )
    require(scope.get("runtime_freeze_sha256") == runtime.get("freeze_sha256"), "authorization runtime freeze drift")
    require(
        scope.get("runtime_qualification_sha256") == runtime.get("qualification_sha256"),
        "authorization runtime qualification drift",
    )

    runtime_python, runtime_env = validate_runtime(contract)

    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.run(["git", "-C", str(mind_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    initial_skill = mind_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    require(sha_file(initial_skill) == contract["mindmemos"]["initial_skill_sha256"], "initial skill drift")

    run_root = Path(contract["run_root"])
    lock_path = run_root / ".exclusive.lock"
    manifest_path = run_root / "checkpoints/completed_streams.jsonl"
    summary_root = run_root / "summary/streams"
    failure_root = run_root / "checkpoints/failures"
    budget_ledger_path = run_root / "checkpoints/provider_budget.sqlite3"
    lock_fd = acquire_lock(lock_path, contract_sha=contract_sha, authorization_sha=auth_sha)
    provider_budget_ledger = ProviderBudgetLedger(
        path=budget_ledger_path,
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        total_limit=int(contract["budget"]["max_provider_calls"]),
        per_unit_limit=int(contract["actor"]["max_turns"]),
        allow_create=not budget_ledger_path.exists(),
    )
    success = False
    try:
        completed = manifest_rows(manifest_path)
        for row in completed.values():
            verify_stream_receipt(row, run_root, provider_budget_ledger)

        for stream_id in frozen_stream_ids:
            if stream_id in completed:
                continue
            output = summary_root / f"{stream_id}.json"
            command = [
                str(runtime_python),
                str(ACTOR),
                "--env-file", str(args.env_file),
                "--suite-root", str(suite_root),
                "--mindmemos-root", str(mind_root),
                "--run-root", str(run_root),
                "--identity", str(identity),
                "--authorization", str(args.authorization),
                "--mode", "e1",
                "--model", contract["actor"]["requested_model"],
                "--stream-id", stream_id,
                "--k", "8",
                "--prefix-ks", "1,2,4,8",
                "--max-turns", str(contract["actor"]["max_turns"]),
                "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
                "--concurrency", str(contract["actor"]["concurrency"]),
                "--provider-budget-ledger", str(budget_ledger_path),
                "--provider-total-call-limit", str(contract["budget"]["max_provider_calls"]),
                "--provider-per-unit-call-limit", str(contract["actor"]["max_turns"]),
                "--output", str(output),
            ]
            result = subprocess.run(command, cwd=ROOT, env=runtime_env, capture_output=True, text=True)
            if result.returncode != 0:
                failure = {
                    "schema_version": "1.0",
                    "artifact_type": "e2-r17-e1-a-stream-technical-failure",
                    "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "stream_id": stream_id,
                    "returncode": result.returncode,
                    "stdout_tail": result.stdout[-4000:],
                    "stderr_tail": result.stderr[-4000:],
                    "provider_relaunch_authorized": False,
                    "instruction": "Inspect process, lock, rollout refs, technical failures and completed manifests before any resume. Do not blindly relaunch.",
                }
                atomic_json(failure_root / f"{stream_id}.json", failure)
                raise RuntimeError(f"E1-A stream failed: {stream_id}; stale lock intentionally preserved")
            require(output.exists(), f"actor stream returned success without summary: {stream_id}")
            summary = load_json(output)
            require(summary.get("status") == "COMPLETED", f"actor stream summary not completed: {stream_id}")
            require(summary.get("authorization_sha256") == auth_sha, "actor stream authorization SHA drift")
            require(summary.get("contract_sha256") == contract_sha, "actor stream contract SHA drift")
            row = {
                "stream_id": stream_id,
                "summary_path": str(output),
                "summary_sha256": sha_file(output),
                "task_ids": [str(v) for v in streams[stream_id]],
                "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            verify_stream_receipt(row, run_root, provider_budget_ledger)
            append_jsonl(manifest_path, row)
            completed[stream_id] = row

        require(len(completed) == 12, "E1-A did not complete all 12 streams")
        for row in completed.values():
            verify_stream_receipt(row, run_root, provider_budget_ledger)

        mixed = 0
        exposed_streams = 0
        family_mixed: dict[str, int] = {}
        stream_rows: list[dict[str, Any]] = []
        metadata = {str(r["id"]): r for r in load_json(suite_root / "r17_controlled_metadata.json")}
        total_provider_calls = 0
        total_rollouts = 0
        for stream_id in frozen_stream_ids:
            stream_mixed = 0
            stream_calls = 0
            for task_id in streams[stream_id]:
                pool = load_json(run_root / "cases" / task_id / "pool_k8.json")
                scores = [float(row["score"]) for row in pool["trajectories"]]
                is_mixed = min(scores) < 1.0 and max(scores) >= 1.0
                stream_mixed += int(is_mixed)
                mixed += int(is_mixed)
                family = str(metadata[task_id]["primary_failure_family"])
                family_mixed[family] = family_mixed.get(family, 0) + int(is_mixed)
                total_rollouts += len(scores)
                for trajectory in pool["trajectories"]:
                    raw = load_json(Path(trajectory["trajectory_path"]))
                    stream_calls += len(raw.get("adapter_receipts") or [])
            total_provider_calls += stream_calls
            qualifies = stream_mixed >= int(contract["support_gate"]["mixed_pools_per_exposed_stream_minimum"])
            exposed_streams += int(qualifies)
            stream_rows.append({
                "stream_id": stream_id,
                "mixed_pools": stream_mixed,
                "qualifies_as_exposed_stream": qualifies,
                "provider_calls": stream_calls,
            })

        require(total_rollouts == 768, f"unexpected frozen rollout count: {total_rollouts}")
        require(total_provider_calls <= int(contract["budget"]["max_provider_calls"]), "provider receipt count hard ceiling exceeded")
        provider_budget_snapshot = provider_budget_ledger.snapshot()
        require(
            provider_budget_snapshot.total_claimed <= int(contract["budget"]["max_provider_calls"]),
            "provider budget claim hard ceiling exceeded",
        )
        require(
            provider_budget_snapshot.total_claimed >= total_provider_calls,
            "provider receipts exceed fail-closed pre-I/O budget claims",
        )
        supported_families = sum(int(value > 0) for value in family_mixed.values())
        support = {
            "mixed_pool_count": mixed,
            "mixed_pool_total": 96,
            "exposed_stream_count": exposed_streams,
            "stream_total": 12,
            "stream_rows": stream_rows,
            "family_mixed_counts": dict(sorted(family_mixed.items())),
            "supported_families": supported_families,
            "primary_hard_gate_pass": (
                mixed >= int(contract["support_gate"]["mixed_pool_count_minimum"])
                and exposed_streams >= int(contract["support_gate"]["exposed_stream_minimum"])
            ),
            "family_generalization_gate_pass": supported_families >= int(contract["support_gate"]["supported_families_minimum"]),
        }
        final = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-e1-a-pool-freeze-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION",
            "contract_sha256": contract_sha,
            "authorization_sha256": auth_sha,
            "model_identity_sha256": sha_file(identity),
            "mindmemos_commit": head,
            "runtime_python": str(runtime_python),
            "runtime_freeze_sha256": contract["runtime"]["freeze_sha256"],
            "runtime_qualification_sha256": contract["runtime"]["qualification_sha256"],
            "streams": 12,
            "tasks": 96,
            "actor_rollouts": total_rollouts,
            "provider_calls": total_provider_calls,
            "provider_budget": provider_budget_snapshot.to_dict(),
            "support": support,
            "updater_calls": 0,
            "e1_b_authority": False,
            "paper_promotion_authority": False,
        }
        atomic_json(run_root / "summary/e1_a_pool_freeze_summary.json", final)
        success = True
        print(json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    finally:
        os.close(lock_fd)
        if success:
            lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: updater_runtime_qualification | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-updater-runtime-qualification-20260829.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-updater-runtime-qualification",
  "date": "2026-08-29",
  "status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_UPDATER_RUNTIME",
  "scientific_role": "PERSISTENT_SKILL_UPDATER_ONLY",
  "runtime": {
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv/bin/python",
    "python_version": "3.12.3",
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv.freeze.txt",
    "freeze_sha256": "80cd6fdd8eb672e41252c099766fd171a5a7a4b90c284d87da87d09f0d559731",
    "source_binding": [
      "/data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos",
      "/data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos_sdk",
      "/data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos_eval"
    ],
    "environment_requirements": {
      "LITELLM_LOCAL_MODEL_COST_MAP": "True"
    }
  },
  "mindmemos": {
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "checkout_clean": true,
    "uv_lock_path": "/data/wyt/evidence-substrates/MindMemOS-20260817/uv.lock",
    "uv_lock_sha256": "867495f270aa3c44d7f0409feb03a8838642f7f1eb6b3552ae79e837ec164cae",
    "sync_semantics": "UV_PROJECT_ENVIRONMENT=<updater-venv> uv sync --project <MindMemOS> --package mindmemos --frozen --no-dev --python /usr/bin/python3.12"
  },
  "post_lock_compatibility_override": {
    "present": true,
    "package": "tiktoken",
    "locked_environment_version_before_override": "0.13.0",
    "qualified_runtime_version": "0.11.0",
    "reason": "E2-R17 V3.1 ExactMatchedEvidenceBlockRenderer was independently pre-frozen and mechanically qualified with tiktoken==0.11.0 / cl100k_base before provider-runtime execution. The updater runtime therefore applies this explicit compatibility override after the frozen MindMemOS sync instead of silently changing the renderer tokenizer.",
    "claim_boundary": "This runtime is not described as a pure uv.lock environment; the override is explicit and content-addressed by the final freeze SHA."
  },
  "package_versions": {
    "mindmemos": "0.1.3",
    "omegaconf": "2.3.1",
    "qdrant-client": "1.18.0",
    "pydantic": "2.13.4",
    "tiktoken": "0.11.0"
  },
  "exact_entrypoint_qualification": {
    "first_party_entrypoint": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "import_status": "PASS",
    "supporting_entrypoints": [
      "qdrant_client.AsyncQdrantClient",
      "research_pipeline.e2_r17_mindmemos_updater.run_projection_update",
      "research_pipeline.e2_r17_evidence_window_v2.ExactMatchedEvidenceBlockRenderer"
    ]
  },
  "zero_provider_first_party_updater_qualification": {
    "path": "/data/wyt/e2-r17-search-projection/runtime-qualifications/updater-runtime-zero-provider-20260829.json",
    "sha256": "9d2f4e3525a04a55128e3592f44531226962084613adf1bca17f0f96f7d521a9",
    "status": "PASS_ZERO_PROVIDER",
    "provider_calls": 0,
    "all_six_updater_arms_pass": true
  },
  "regression_tests": {
    "status": "PASS",
    "ran": 16,
    "skipped": 2,
    "failed": 0,
    "errors": 0,
    "suites": [
      "research_pipeline.test_e2_r17_mindmemos_updater_v31",
      "research_pipeline.test_e2_r17_evidence_window_v2",
      "research_pipeline.test_e2_r17_mindmemos_ark_adapter",
      "research_pipeline.test_e2_r17_provider_budget"
    ]
  },
  "scope_separation": {
    "actor_evaluator_runtime_qualification_inherited": false,
    "updater_runtime_qualification_is_role_specific": true,
    "public_baseline_runtime_authority": false
  },
  "failure_that_triggered_this_qualification": {
    "failure_id": "R17-F008-UPDATER-RUNTIME-COVERAGE",
    "classification": "RUNTIME_INFRA/IMPLEMENTATION",
    "scientific_belief_update": "NONE"
  },
  "provider_calls": 0,
  "scientific_outcome": false,
  "authority": {
    "prepare_provider_runtime_pilot_v2_contract": true,
    "execute_provider_runtime_pilot": false,
    "e1_b": false,
    "paper_promotion": false,
    "submission": false
  },
  "private_credentials_included": false,
  "raw_response_ids_included": false
}


===== BOUND ARTIFACT: actor_runtime_qualification | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-runtime-dependency-qualification-r2-20260828.json =====
{
  "artifact_type": "e2-r17-runtime-dependency-qualification",
  "authority": {
    "e0_full": false,
    "e0_pilot": false,
    "e1": false,
    "front_end_claim": false,
    "paper_promotion": false,
    "public_externality": false,
    "scientific_experiment": false,
    "submission": false
  },
  "created_at_utc": "2026-08-28T04:13:26+00:00",
  "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
  "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
  "import_smoke": {
    "imports": [
      "mindmemos_eval.skills.agents.ReactAgentFactory",
      "mindmemos_eval.skills.envs.spreadsheetbench.env.SpreadsheetBenchEnv"
    ],
    "status": "PASS"
  },
  "installed_distribution_count": 69,
  "mindmemos_uv_lock_path": "/data/wyt/evidence-substrates/MindMemOS-20260817/uv.lock",
  "mindmemos_uv_lock_sha256": "867495f270aa3c44d7f0409feb03a8838642f7f1eb6b3552ae79e837ec164cae",
  "pilot_case_preflight": {
    "pilot_manifest_path": "generated/e2-r17-e0-pilot-manifest-20260828.json",
    "pilot_manifest_sha256": "e6653ee7cd2d7391b555086adb1a9d2bf660a7df25455f8c0215b35fa85b893f",
    "provider_calls": 0,
    "status": "PASS",
    "task_count": 12,
    "task_execution": false
  },
  "private_credentials_included": false,
  "provider_calls": 0,
  "python_executable": "/usr/bin/python3.12",
  "python_version": "3.12.3",
  "raw_response_ids_included": false,
  "repair_trigger_path": "generated/e2-r17-e0-pilot-launch-failure-r1-20260828.json",
  "schema_version": "2.0",
  "scientific_outcome": false,
  "status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2",
  "supersedes": "generated/e2-r17-runtime-dependency-qualification-20260828.json",
  "tests": {
    "errors": 0,
    "failed": 0,
    "passed": 28,
    "status": "PASS",
    "suites": [
      "search_projection_theory",
      "search_projection_runner",
      "controlled_spreadsheet_suite",
      "ark_plan_react",
      "mindmemos_ark_adapter"
    ]
  },
  "uv_executable": "/data/wyt/e2-r17-search-projection/uv-bootstrap/bin/uv",
  "uv_sync_command": "UV_PROJECT_ENVIRONMENT=<venv> uv sync --project <MindMemOS> --package mindmemos-eval --frozen --no-dev --python /usr/bin/python3.12",
  "uv_version": "0.12.7",
  "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
}


===== BOUND ARTIFACT: provider_runtime_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v31-provider-runtime-pilot-v2-adjudication-20260829.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-v31-provider-runtime-pilot-adjudication",
  "date": "2026-08-29",
  "status": "PASS_PROVIDER_RUNTIME_MEASURABILITY_ONLY_E1B_STILL_UNAUTHORIZED",
  "contract": {
    "path": "generated/e2-r17-v31-provider-runtime-pilot-v2-contract-20260829.json",
    "sha256": "98467e1a22fa5fabb0947c83b5295085f4866424993190fa4af2f4f5d91b99aa"
  },
  "authorization": {
    "path": "generated/e2-r17-v31-provider-runtime-pilot-v2-authorization-20260829.json",
    "sha256": "a32e80976b7eb037582c36f3768bd0b37a5977c29e4b5da1d972953ea696d559"
  },
  "run": {
    "root": "/data/wyt/e2-r17-search-projection/runtime-pilots/v31-provider-updater-v2-20260829",
    "summary": "/data/wyt/e2-r17-search-projection/runtime-pilots/v31-provider-updater-v2-20260829/summary/provider_runtime_pilot_summary.json",
    "summary_sha256": "e1903beb48d9ede6447f92dad6a68d1e4f9b169cd570f09d73f069373014ee28",
    "completed_arms": 3,
    "provider_call_receipts": 30,
    "exclusive_lock_released_only_after_full_success": true
  },
  "scientific_boundary": {
    "new_actor_rollouts": 0,
    "heldout_evaluation_calls": 0,
    "scientific_effectiveness_evaluated": false,
    "learned_skill_quality_compared": false,
    "e1_b_effect_authority": false,
    "paper_claim_authority": false
  },
  "runtime_measurability": {
    "win_a_win_b_pre_provider_evidence_byte_identical": true,
    "causal_purity_mode_all_arms": "arm_blinded_selected_evidence",
    "arm_metadata_visible_in_transcript_all_arms": false,
    "updater_visible_score_semantics_all_arms": "selected_evidence_trajectory",
    "summaries_per_arm": 8,
    "consumed_records_per_arm": 8,
    "provider_retry_limit": 0,
    "thinking": "disabled",
    "temperature": 0.0,
    "parse_error_calls": 0,
    "provider_calls": 30,
    "provider_calls_per_arm": {
      "win_a": 10,
      "win_b": 10,
      "mrw": 10
    },
    "provider_call_task_structure_per_arm": {
      "skill_trajectory_summary": 8,
      "skill_patch_propose": 1,
      "skill_patch_apply": 1
    },
    "provider_tokens": {
      "total": 90608,
      "win_a": 30187,
      "win_b": 29851,
      "mrw": 30570
    },
    "provider_input_tokens": {
      "win_a": 26677,
      "win_b": 26509,
      "mrw": 26711
    },
    "provider_output_tokens": {
      "win_a": 3510,
      "win_b": 3342,
      "mrw": 3859
    },
    "provider_wall_time_seconds_sum": {
      "win_a": 54.043,
      "win_b": 51.747,
      "mrw": 55.779
    },
    "provider_call_latency_median_seconds": {
      "win_a": 5.819,
      "win_b": 5.745,
      "mrw": 5.544
    },
    "provider_call_latency_max_seconds": {
      "win_a": 6.794,
      "win_b": 6.184,
      "mrw": 8.094
    }
  },
  "budget": {
    "pre_io_claiming": true,
    "claims_never_released": true,
    "total_claimed": 30,
    "total_limit": 30,
    "per_arm_claimed": {
      "win_a": 10,
      "win_b": 10,
      "mrw": 10
    },
    "per_arm_limit": 10,
    "interpretation": "The nominal first-party SkillEvolver path uses exactly 10 generations per eight-task update under max_parse_attempts=1. The Pilot consumed the exact frozen ceiling without overflow. Any additional generation would have failed before provider I/O."
  },
  "failure_learning": {
    "trigger_failure_id": "R17-F008-UPDATER-RUNTIME-COVERAGE",
    "repair_validated": true,
    "lesson": "A role-specific updater runtime bound to the exact SkillEvolver entrypoint is sufficient; actor/evaluator runtime qualification must not be inherited for updater execution.",
    "post_lock_override": "tiktoken==0.11.0 remained compatible with the pinned first-party updater in a real hosted 30-call Pilot after zero-provider qualification."
  },
  "interpretation": "The V3.1 causal-purity path is operational with the real hosted first-party SkillEvolver: exact historical pools can be rendered into arm-blinded evidence, consumed by three independent updater arms, checkpointed, budget-accounted and completed without parse/runtime failure. This does NOT show that MRW improves future skill and does NOT test WIN-A/WIN-B behavioral equivalence.",
  "next_gate": "PREPARE_AND_INDEPENDENTLY_REVIEW_E1_B_WIN_A_WIN_B_NEGATIVE_CONTROL_ONLY_CONTRACT",
  "authority": {
    "prepare_e1_b_negative_control_contract": true,
    "execute_e1_b_negative_control": false,
    "execute_mrw_causal_comparison": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: failure_registry | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-failure-differential-registry-v2-20260829.json =====
{
  "artifact_type": "e2-r17-failure-differential-registry",
  "current_scientific_state": {
    "central_mechanism": "OPEN_NOT_YET_ADJUDICATED",
    "e0_censoring_existence": "SUPPORTED_ON_CONTROLLED_PILOT",
    "e1_a_treatment_support": "PASS_STRONG_SUPPORT_78_OF_96_MIXED_12_OF_12_STREAMS_6_OF_6_FAMILIES",
    "e1_b_mrw_causal_effect": "UNKNOWN",
    "e1_b_negative_control": "READY_FOR_SEPARATE_CONTRACT_REVIEW_NOT_AUTHORIZED",
    "provider_runtime_pilot": "PASS_RUNTIME_MEASURABILITY_ONLY"
  },
  "date": "2026-08-29",
  "entries": [
    {
      "classification": [
        "MEASUREMENT_ANALYSIS",
        "PROTOCOL_CAUSAL_PURITY"
      ],
      "contamination": "NONE",
      "failure_id": "R17-F001-V3-BPE-PARITY",
      "preserved_artifacts": [
        {
          "path": "generated/e2-r17-v3-runtime-pilot-failure-adjudication-20260828.json",
          "sha256": "fec66715370144f4b8c72c7afd32520f9f990ef466f988c0d77cf3a954aefcef"
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "New V3.1 ExactMatchedEvidenceBlockRenderer matches the actual final re-tokenized evidence block, uses deterministic no-padding search, and preserves old failed V3 root/contract.",
      "rerun_policy": "PERMITTED_ONLY_UNDER_NEW_V3_1_CONTRACT_AND_FRESH_ROOT",
      "reusable_rule": "Fairness budgets must bind the exact model-visible representation after all rendering/transformation steps, not an upstream proxy count.",
      "root_cause": "BPE can create a new merge at the splice boundary; equal selected source-token counts do not imply equal final rendered token counts.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "V3 mechanical runtime pilot",
      "symptom": "Nominally equal source-token slices re-tokenized to unequal final provider-visible lengths after head/tail decoding and concatenation.",
      "terminal_status": "FAIL_MECHANICAL_TOKEN_PARITY"
    },
    {
      "classification": [
        "PROTOCOL_CAUSAL_PURITY"
      ],
      "contamination": "Legacy path is disqualified from causal interpretation; historical artifacts remain non-authoritative for E1.",
      "failure_id": "R17-F002-LEGACY-PROJECTION-LEAK",
      "preserved_artifacts": [
        {
          "path": "consultations/e2-r17-v3-1-causal-purity-repair-20260828.md",
          "sha256": "94490232790ec78cdcb5773b49bb9fcb509ca18b8cc5cc2842216d0becb25521"
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "V3.1 BlindedEvidenceUnit exposes only selected evidence text in messages, stores selected trajectory verifier score as the learner outcome, and keeps acting/projection provenance in audit-only r17_* fields.",
      "rerun_policy": "PERMITTED_ONLY_ON_V3_1_BLINDED_PATH",
      "reusable_rule": "For same-pool causal interventions, provenance required for audit must be kept out of model-visible treatment unless it is itself a predeclared treatment variable.",
      "root_cause": "Acting provenance and learner-visible evidence semantics were not separated in the original wrapper.",
      "scientific_belief_update": "NONE; old path was causally invalid.",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "V3 causal-purity audit",
      "symptom": "Legacy updater packet exposed PROJECTION/ROLE/rollout/provenance labels and could attach the served winner score to a failed MRW transcript.",
      "terminal_status": "LEGACY_PATH_INVALID_FOR_CAUSAL_E1"
    },
    {
      "classification": [
        "IMPLEMENTATION"
      ],
      "contamination": "NONE",
      "failure_id": "R17-F003-E1A-BUDGET-POSTHOC",
      "preserved_artifacts": [
        {
          "path": "research_pipeline/e2_r17_provider_budget.py",
          "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "SQLite BEGIN IMMEDIATE ledger claims budget before provider I/O, binds contract+authorization, never releases ambiguous claims, and fail-closes before the 11th per-unit or 7681st total call.",
      "rerun_policy": "PERMITTED_AFTER_BOUND_GUARD_TESTS_AND_NEW_AUTHORIZATION",
      "reusable_rule": "A scientific provider-call ceiling is a pre-I/O safety invariant, not a post-hoc statistic.",
      "root_cause": "Budget accounting was observational instead of transactional.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "E1-A pre-execution review",
      "symptom": "The declared 10-call per-rollout / 7680-call total ceiling was checked after execution or delegated to an unbound runtime rather than enforced before provider I/O.",
      "terminal_status": "HOLD_PRECALL_BUDGET_GUARD_MISSING"
    },
    {
      "classification": [
        "RUNTIME_INFRA",
        "IMPLEMENTATION"
      ],
      "contamination": "NONE; zero budget claims and zero completed rollout refs.",
      "failure_id": "R17-F004-E1A-AMBIENT-PYTHON",
      "preserved_artifacts": [
        {
          "path": "generated/e2-r17-e1-a-v2-runtime-failure-adjudication-20260828.json",
          "sha256": "3ad8b73ce13f8b5bc0e51f109a8e910e0894656d3bdd94f10290126a3388a399"
        },
        {
          "path": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-20260828/.exclusive.lock",
          "sha256": null
        },
        {
          "path": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-20260828/checkpoints/failures/e1-agj-00.json",
          "sha256": null
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "V2.1 binds exact actor venv/bin/python, VIRTUAL_ENV/PATH, runtime freeze SHA and qualification SHA before spawning any actor.",
      "rerun_policy": "PERMITTED_UNDER_NEW_V2_1_CONTRACT_AND_FRESH_ROOT; FAILED_V2_ROOT_NOT_REUSED",
      "reusable_rule": "Runtime qualification must be executable-binding, not merely package-list provenance.",
      "root_cause": "E1-A orchestrator launched the actor with ambient /usr/bin/python3 instead of the previously qualified frozen actor/evaluator venv.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "E1-A V2 pool-support execution",
      "symptom": "MindMemOS import failed with ModuleNotFoundError: pydantic before any rollout/provider call.",
      "terminal_status": "TECHNICAL_FAILURE_BEFORE_FIRST_ROLLOUT"
    },
    {
      "classification": [
        "MEASUREMENT_ANALYSIS",
        "IMPLEMENTATION"
      ],
      "contamination": "Frozen 96 pools remained intact; thresholds/data were not changed.",
      "failure_id": "R17-F005-SUPPORT-ZERO-FALSY",
      "preserved_artifacts": [
        {
          "path": "generated/e2-r17-e1-a-support-adjudicator-zero-parse-repair-20260828.json",
          "sha256": "e632988b3ebf39588caaaa7b9b425b869e6d06656353506ef0c8782b5ca33d50"
        },
        {
          "path": "scripts/adjudicate_e2_r17_e1_a_pool_support_v2.py",
          "sha256": "cc5d43828179bbdcc932a3194140cb798ccfb9b6d60bda6a44090ae4983601a6"
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "Versioned adjudicator v2 changes only zero/missing parsing; the repair was independently reviewed before adjudicating the same frozen 96-pool artifact.",
      "rerun_policy": "REPARSE_SAME_FROZEN_ARTIFACT_ONLY; NO_NEW_ROLLOUTS",
      "reusable_rule": "Scientific counters where zero is meaningful must distinguish absent/null from zero explicitly; never use truthiness as missingness.",
      "root_cause": "Python falsy semantics incorrectly treated a meaningful zero as missing.",
      "scientific_belief_update": "NONE until repaired adjudicator reached the support endpoint.",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "E1-A post-run support adjudication",
      "symptom": "A valid updater_calls=0 summary was parsed as -1 by int(summary.get('updater_calls') or -1).",
      "terminal_status": "ADJUDICATOR_MECHANICAL_FAILURE"
    },
    {
      "classification": [
        "IMPLEMENTATION"
      ],
      "contamination": "NONE; exact raw reviewer outputs were preserved and reparsed.",
      "failure_id": "R17-F006-REVIEW-ACK-SCHEMA",
      "preserved_artifacts": [
        {
          "path": "generated/e2-r17-v31-provider-runtime-pilot-review-reparsed-20260829.json",
          "sha256": "c7ae640e240975da32d50b1e63322ed49c481ed20f8735b71da67f7366728656"
        },
        {
          "path": "research_pipeline/test_e2_r17_review_harness_ack.py",
          "sha256": "3a985b963402f53137051aafa8007df44c6cc736dedf1e45cdd6ee8c2e901f78"
        },
        {
          "path": "scripts/adjudicate_e2_r17_v31_provider_runtime_pilot_review_reparse.py",
          "sha256": "618a2610281492b20c7ec0c763c255413a5f1f1bbd21463ed5085118f18a5cd0"
        }
      ],
      "provider_calls": "2 original reviewer generations; 0 additional calls for repair/re-adjudication",
      "repair_or_stop": "Shared validator now discovers active schema fields ending in _sha256_acknowledged, validates each exact SHA, remains backward-compatible, and fail-closes on wrong/missing acknowledgements. Existing model outputs were zero-provider reparsed.",
      "rerun_policy": "NO_NEW_REVIEWER_CALL_REQUIRED_WHEN_RAW_OUTPUT_IS_SEMANTICALLY_COMPLETE",
      "reusable_rule": "Keep model generation and local schema adjudication as separate evidence layers; a parser failure does not erase a valid raw review.",
      "root_cause": "Review-harness validation hard-coded one historical acknowledgement field name instead of validating the acknowledgement field declared by the active schema.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "V3.1 provider-runtime Pilot independent review",
      "symptom": "Both Kimi and DeepSeek returned complete PASS reviews, but the shared local validator required the historical repair_sha256_acknowledged field while the new schema defined draft_contract_sha256_acknowledged.",
      "terminal_status": "LOCAL_FAIL_SCHEMA_WITH_VALID_MODEL_CONTENT"
    },
    {
      "classification": [
        "IMPLEMENTATION"
      ],
      "contamination": "NONE",
      "failure_id": "R17-F007-REPARSE-IMPORT-PATH",
      "preserved_artifacts": [
        {
          "path": "scripts/adjudicate_e2_r17_v31_provider_runtime_pilot_review_reparse.py",
          "sha256": "618a2610281492b20c7ec0c763c255413a5f1f1bbd21463ed5085118f18a5cd0"
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "Added explicit ROOT insertion before importing sibling scripts; successful second invocation reused the same raw reviews.",
      "rerun_policy": "PERMITTED_ZERO_PROVIDER_REPARSE",
      "reusable_rule": "Standalone adjudication scripts must prove their own import-path reproducibility before being treated as evidence processors.",
      "root_cause": "Launcher omitted the standard repository-root import binding used by other R17 scripts.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "Zero-provider review re-adjudication utility",
      "symptom": "Direct execution of the new reparse script initially failed before reading review data because repo root was not inserted into sys.path.",
      "terminal_status": "SCRIPT_IMPORT_FAILURE_THEN_REPAIRED"
    },
    {
      "classification": [
        "RUNTIME_INFRA",
        "IMPLEMENTATION"
      ],
      "contamination": "NONE; provider Pilot run root remained fresh.",
      "failure_id": "R17-F008-UPDATER-RUNTIME-COVERAGE",
      "preserved_artifacts": [
        {
          "path": "/data/wyt/e2-r17-search-projection/runtime-qualifications/updater-runtime-zero-provider-20260829.json",
          "sha256": "9d2f4e3525a04a55128e3592f44531226962084613adf1bca17f0f96f7d521a9"
        },
        {
          "path": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv.freeze.txt",
          "sha256": "80cd6fdd8eb672e41252c099766fd171a5a7a4b90c284d87da87d09f0d559731"
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "Created a dedicated updater runtime from pinned MindMemOS uv.lock/package, then explicitly applied the predeclared R17 renderer compatibility override tiktoken==0.11.0; first-party SkillEvolver import and zero-provider six-arm updater qualification pass under this dedicated runtime.",
      "rerun_policy": "PROVIDER_RUNTIME_PILOT_MAY_BE_REDESIGNED_ONLY_WITH_DEDICATED_UPDATER_RUNTIME_BOUND_IN_NEW_CONTRACT",
      "reusable_rule": "Runtime qualification is role-specific and must import/exercise the exact scientific entrypoint; actor/evaluator qualification never authorizes updater execution.",
      "root_cause": "The existing runtime qualification covered the actor/evaluator entrypoints, not the persistent-updater dependency closure. The provider-runtime Pilot inherited a role-inappropriate runtime assumption.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "V3.1 provider-runtime Pilot preflight",
      "symptom": "The actor/evaluator venv could import mindmemos_eval but failed importing first-party mindmemos.pipelines.skill.evolution.SkillEvolver because omegaconf was absent.",
      "terminal_status": "HOLD_PROVIDER_RUNTIME_PILOT_BEFORE_PROVIDER_CALL"
    },
    {
      "classification": [
        "IMPLEMENTATION"
      ],
      "contamination": "NONE",
      "failure_id": "R17-F009-PREFLIGHT-SOURCE-BINDING",
      "preserved_artifacts": [],
      "provider_calls": 0,
      "repair_or_stop": "Repeated the check with the exact three source roots bound; that authoritative preflight then exposed the real missing omegaconf dependency in the actor venv.",
      "rerun_policy": "DIAGNOSTIC_RECHECK_PERMITTED_WITH_EXECUTION-FAITHFUL_BINDING",
      "reusable_rule": "A preflight that does not reproduce the execution binding is diagnostic noise and must not authorize or block science by itself.",
      "root_cause": "The diagnostic preflight did not mirror the actual execution environment/source binding.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "Updater runtime diagnosis",
      "symptom": "An initial manual updater import check could not find mindmemos because it did not reproduce the runner's source-tree sys.path binding.",
      "terminal_status": "NONAUTHORITATIVE_PREFLIGHT_MISMATCH"
    },
    {
      "classification": [
        "IMPLEMENTATION"
      ],
      "contamination": "NONE; explicit follow-up showed no runner process, no run root and no lock.",
      "failure_id": "R17-F010-PROCESS-GUARD-SELF-MATCH",
      "preserved_artifacts": [
        {
          "path": "generated/e2-r17-v31-provider-runtime-pilot-v2-launch-guard-failure-20260829.json",
          "sha256": "6ffea48d9fb8cd660cc96b3f213c7a515f2b1bb0e3b8a241dae5092e05b7167a"
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "Use separate process inspection plus run-root/lock/checkpoint state; after zero-state verification the exact same frozen contract was launched once.",
      "rerun_policy": "SINGLE_LAUNCH_PERMITTED_AFTER_ZERO_STATE_VERIFICATION",
      "reusable_rule": "Duplicate-launch guards must be resistant to self-match; content-addressed run-root/lock/checkpoint state is stronger than naive full-command pgrep.",
      "root_cause": "The search pattern was present in the guard process command line itself.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "V3.1 provider-runtime Pilot V2 launch preflight",
      "symptom": "A naive pgrep -af duplicate-launch guard matched the current shell command and falsely reported ALREADY_RUNNING.",
      "terminal_status": "LAUNCH_NOT_ATTEMPTED_FALSE_ALREADY_RUNNING"
    }
  ],
  "permanent_rules": [
    "A technical, runtime, protocol, or measurement failure that occurs before a valid scientific endpoint produces no scientific belief update about the mechanism.",
    "The failed artifact, failed run root, stale lock, raw model response, and negative result are preserved when available; repair occurs under a new version/contract/root rather than overwriting history.",
    "A protocol-invalid result cannot be counted as a scientific negative or positive.",
    "A valid primary scientific negative cannot later be relabeled as implementation failure without new concrete evidence showing protocol invalidity that existed at execution time.",
    "A SCIENTIFIC_MECHANISM failure triggers the predeclared STOP/HOLD rule; additional benchmarks, models, task substitution, threshold changes, or favorable subsets cannot rescue the central causal claim.",
    "Every rerun must state the failure classification, exact repair delta, why rerun is scientifically permissible, and which scientific variables remain unchanged.",
    "Reviewer/parser/harness failures preserve exact raw model output separately from local validation status; reparsing existing output is preferred to paying for a new model call when semantics were already complete.",
    "Runtime qualification is role-specific: actor/evaluator, updater, and public-baseline harnesses must each import and exercise the exact execution entrypoint under their exact frozen runtime. Qualification of one role never implies qualification of another.",
    "A preflight is authoritative only if it reproduces the actual source-path binding, environment variables, executable, and entrypoint used by the scientific runner.",
    "Any dependency override applied after a lockfile-derived environment is explicit, versioned, hash-bound, justified, and requalified; it must never be described as lock-native.",
    "Success is also terminal evidence: completed runs must record protocol integrity, endpoint reached, scientific interpretation authority, and next gate rather than merely disappearing into a summary file."
  ],
  "purpose": "Every R17 execution attempt must terminate as a valid success or as an explicitly classified failure. Technical/protocol/measurement failures are separated from qualified scientific-mechanism failures so that repairs cannot silently rewrite scientific evidence and scientific negatives cannot be laundered into engineering bugs.",
  "qualified_successes": [
    {
      "evidence": {
        "path": "generated/e2-r17-v31-provider-runtime-pilot-v2-adjudication-20260829.json",
        "sha256": "8be8a4596ffef8e3702f8e422ed4dd2c55b7fc1f97573b125f30096d64f60424"
      },
      "heldout_evaluation_calls": 0,
      "lesson": "Dedicated role-specific updater runtime repaired R17-F008; real first-party SkillEvolver consumed WIN-A/WIN-B/MRW under V3.1 blinding and exact budget accounting without runtime/parse failure.",
      "parse_error_calls": 0,
      "provider_calls": 30,
      "scientific_effectiveness_evaluated": false,
      "stage": "V3.1 hosted provider-runtime Pilot V2",
      "status": "PASS_PROVIDER_RUNTIME_MEASURABILITY_ONLY_E1B_STILL_UNAUTHORIZED",
      "success_id": "R17-S001-PROVIDER-RUNTIME-V2"
    }
  ],
  "schema_version": "1.1",
  "status": "ACTIVE_CANONICAL_FAILURE_LEDGER_FOR_R17_WORKTREE",
  "supersedes": {
    "path": "generated/e2-r17-failure-differential-registry-20260829.json",
    "sha256": "5aeb331a759e0b681512e4fafab6907cbf191bdd4d3d6d4402cf423fc0592676"
  },
  "taxonomy": {
    "IMPLEMENTATION": "Local code, launcher, parser, review harness, checkpoint, or accounting defect before a valid scientific endpoint.",
    "MEASUREMENT_ANALYSIS": "Estimator, renderer, token/accounting, or adjudicator failure that invalidates the intended measurement without establishing a scientific negative.",
    "PROTOCOL_CAUSAL_PURITY": "A design or dataflow defect that changes or leaks treatment, invalidating causal interpretation even if code runs.",
    "RUNTIME_INFRA": "Environment/dependency/role-runtime or provider-route failure that prevents the frozen scientific procedure from reaching its endpoint.",
    "SCIENTIFIC_MECHANISM": "A protocol-valid, fully qualified primary experiment reaches its endpoint and rejects/equates/harms the central mechanism under the frozen decision rule. This class triggers scientific STOP unless a predeclared scope limitation applies."
  }
}


===== BOUND ARTIFACT: fresh_model_identity_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v31-provider-pilot-v2-model-identity-adjudication-20260829.json =====
{
  "adjudication": "The initial Kimi Auto/default-thinking smokes are retained as explicit incomplete-length protocol failures. The passing Kimi qualification is a separately declared compatibility call with thinking disabled. DeepSeek resolves to the current GA release rather than the historical 260425 suffix. These observed identities are frozen only for the current pre-execution review tranche and must be requalified before any later scientific tranche.",
  "artifact_type": "e2-r17-current-plan-model-identity-adjudication",
  "authority": {
    "gpu": false,
    "paper_promotion": false,
    "preexecution_consultation": true,
    "scientific_experiment": false,
    "submission": false
  },
  "checks": {
    "deepseek_pass": true,
    "kimi_pass": true,
    "no_hidden_provider_retry": true,
    "provider_retry_zero": true,
    "resolved_identities_distinct": true,
    "route_is_ark_plan": true
  },
  "compatibility_history": [
    {
      "path": "generated/e2-r17-v31-provider-pilot-v2-model-identity-qualification-20260829.json",
      "sha256": "8063a6d638b4bfa974c74ab8bbea023deec3958d497f4e78366222e0cd7a5634",
      "status": "PASS"
    }
  ],
  "created_at_utc": "2026-08-29T10:54:01+00:00",
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "requested_and_resolved": {
    "deepseek-v4-pro": {
      "requested": "deepseek-v4-pro",
      "resolved": "deepseek-v4-pro-ga-260813",
      "source_artifact": "generated/e2-r17-v31-provider-pilot-v2-model-identity-qualification-20260829.json",
      "source_artifact_sha256": "8063a6d638b4bfa974c74ab8bbea023deec3958d497f4e78366222e0cd7a5634",
      "thinking_requested": "disabled"
    },
    "kimi-k3": {
      "requested": "kimi-k3",
      "resolved": "kimi-k3",
      "source_artifact": "generated/e2-r17-v31-provider-pilot-v2-model-identity-qualification-20260829.json",
      "source_artifact_sha256": "8063a6d638b4bfa974c74ab8bbea023deec3958d497f4e78366222e0cd7a5634",
      "thinking_requested": "disabled"
    }
  },
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS_CURRENT_REVIEW_TRANCHE"
}


===== BOUND ARTIFACT: fresh_model_identity_qualification | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v31-provider-pilot-v2-model-identity-qualification-20260829.json =====
{
  "artifact_type": "e2-r17-current-ark-plan-model-identity-qualification",
  "authority": {
    "gpu": false,
    "paper_promotion": false,
    "preexecution_consultation": true,
    "scientific_experiment": false,
    "submission": false
  },
  "checks": {
    "all_protocol_calls_pass": true,
    "provider_retry_zero": true,
    "resolved_identities_distinct": true,
    "route_is_ark_plan": true
  },
  "compatibility_parent": null,
  "created_at_utc": "2026-08-29T10:54:01+00:00",
  "default_model": "ark-code-latest",
  "models": [
    {
      "benchmark_data_accessed": false,
      "checks": {
        "resolved_model_matches_requested_family": true,
        "resolved_model_present": true,
        "text_exact": true
      },
      "get_poll_recovery": false,
      "hidden_provider_retry_used": false,
      "max_output_tokens": 256,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "deepseek-v4-pro",
      "resolved_model": "deepseek-v4-pro-ga-260813",
      "response_id_sha256": "d9b22d560a155e798c3368c06ffc01d5fac2a037b6b7a89109d2f259ec201ff5",
      "scientific_outcome": false,
      "status": "PASS",
      "thinking_requested": "disabled",
      "usage": {
        "input_tokens": 27,
        "input_tokens_details": {
          "cached_tokens": 0
        },
        "output_tokens": 3,
        "output_tokens_details": {
          "reasoning_tokens": 0
        },
        "total_tokens": 30
      }
    },
    {
      "benchmark_data_accessed": false,
      "checks": {
        "resolved_model_matches_requested_family": true,
        "resolved_model_present": true,
        "text_exact": true
      },
      "get_poll_recovery": false,
      "hidden_provider_retry_used": false,
      "max_output_tokens": 256,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "kimi-k3",
      "resolved_model": "kimi-k3",
      "response_id_sha256": "8807139da5a8ba82ce0c72fa8ede4eb0a41e6cbf63ee641884dee4a18d6effda",
      "scientific_outcome": false,
      "status": "PASS",
      "thinking_requested": "disabled",
      "usage": {
        "input_tokens": 41,
        "input_tokens_details": {
          "cached_tokens": 0
        },
        "output_tokens": 13,
        "output_tokens_details": {
          "reasoning_tokens": 0
        },
        "total_tokens": 54
      }
    }
  ],
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "release_drift_policy": "Observed resolved identities are frozen for this review tranche. Historical exact suffixes are not reused as authority. Any later execution tranche must requalify and bind its own observed identities.",
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS"
}


===== BOUND ARTIFACT: split_manifest | /data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_split_manifest.json =====
{
  "development": [
    "r17-b0-agj-p4",
    "r17-b0-agj-p6",
    "r17-b0-fmv-p1",
    "r17-b0-fmv-p5",
    "r17-b0-ioc-p3",
    "r17-b0-ioc-p7",
    "r17-b0-msp-p3",
    "r17-b0-msp-p5",
    "r17-b0-ska-p3",
    "r17-b0-ska-p7",
    "r17-b0-tsr-p3",
    "r17-b0-tsr-p7"
  ],
  "e0_calibration": [
    "r17-b1-agj-p0",
    "r17-b1-agj-p1",
    "r17-b1-agj-p2",
    "r17-b1-agj-p3",
    "r17-b1-agj-p4",
    "r17-b1-agj-p5",
    "r17-b1-agj-p6",
    "r17-b1-agj-p7",
    "r17-b1-agj-p8",
    "r17-b1-fmv-p0",
    "r17-b1-fmv-p1",
    "r17-b1-fmv-p2",
    "r17-b1-fmv-p3",
    "r17-b1-fmv-p4",
    "r17-b1-fmv-p5",
    "r17-b1-fmv-p6",
    "r17-b1-fmv-p7",
    "r17-b1-fmv-p8",
    "r17-b1-ioc-p0",
    "r17-b1-ioc-p1",
    "r17-b1-ioc-p2",
    "r17-b1-ioc-p3",
    "r17-b1-ioc-p4",
    "r17-b1-ioc-p5",
    "r17-b1-ioc-p6",
    "r17-b1-ioc-p7",
    "r17-b1-ioc-p8",
    "r17-b1-msp-p0",
    "r17-b1-msp-p1",
    "r17-b1-msp-p2",
    "r17-b1-msp-p3",
    "r17-b1-msp-p4",
    "r17-b1-msp-p5",
    "r17-b1-msp-p6",
    "r17-b1-msp-p7",
    "r17-b1-msp-p8",
    "r17-b1-ska-p0",
    "r17-b1-ska-p1",
    "r17-b1-ska-p2",
    "r17-b1-ska-p3",
    "r17-b1-ska-p4",
    "r17-b1-ska-p5",
    "r17-b1-ska-p6",
    "r17-b1-ska-p7",
    "r17-b1-ska-p8",
    "r17-b1-tsr-p0",
    "r17-b1-tsr-p1",
    "r17-b1-tsr-p2",
    "r17-b1-tsr-p3",
    "r17-b1-tsr-p4",
    "r17-b1-tsr-p5",
    "r17-b1-tsr-p6",
    "r17-b1-tsr-p7",
    "r17-b1-tsr-p8"
  ],
  "e1_common_heldout_probe": [
    "r17-b4-agj-p2",
    "r17-b4-agj-p3",
    "r17-b4-agj-p8",
    "r17-b4-fmv-p1",
    "r17-b4-fmv-p2",
    "r17-b4-fmv-p8",
    "r17-b4-ioc-p1",
    "r17-b4-ioc-p4",
    "r17-b4-ioc-p6",
    "r17-b4-msp-p0",
    "r17-b4-msp-p7",
    "r17-b4-msp-p8",
    "r17-b4-ska-p4",
    "r17-b4-ska-p5",
    "r17-b4-ska-p8",
    "r17-b4-tsr-p0",
    "r17-b4-tsr-p6",
    "r17-b4-tsr-p8"
  ],
  "e1_update_reserve_integrity_only": [
    "r17-b2-agj-p1",
    "r17-b2-fmv-p4",
    "r17-b2-ioc-p4",
    "r17-b2-msp-p0",
    "r17-b2-msp-p3",
    "r17-b2-ska-p2",
    "r17-b2-tsr-p7",
    "r17-b3-agj-p4",
    "r17-b3-fmv-p6",
    "r17-b3-ioc-p2",
    "r17-b3-ska-p4",
    "r17-b3-tsr-p2"
  ],
  "e1_update_streams": {
    "e1-agj-00": [
      "r17-b2-agj-p2",
      "r17-b2-agj-p5",
      "r17-b2-agj-p7",
      "r17-b3-agj-p0",
      "r17-b2-agj-p3",
      "r17-b3-agj-p3",
      "r17-b2-agj-p8",
      "r17-b3-agj-p8"
    ],
    "e1-agj-01": [
      "r17-b2-agj-p0",
      "r17-b3-agj-p6",
      "r17-b3-agj-p2",
      "r17-b3-agj-p5",
      "r17-b2-agj-p6",
      "r17-b3-agj-p7",
      "r17-b3-agj-p1",
      "r17-b2-agj-p4"
    ],
    "e1-fmv-00": [
      "r17-b3-fmv-p4",
      "r17-b2-fmv-p8",
      "r17-b2-fmv-p1",
      "r17-b2-fmv-p0",
      "r17-b3-fmv-p5",
      "r17-b2-fmv-p5",
      "r17-b3-fmv-p7",
      "r17-b2-fmv-p6"
    ],
    "e1-fmv-01": [
      "r17-b3-fmv-p0",
      "r17-b2-fmv-p7",
      "r17-b2-fmv-p2",
      "r17-b3-fmv-p2",
      "r17-b3-fmv-p1",
      "r17-b3-fmv-p8",
      "r17-b3-fmv-p3",
      "r17-b2-fmv-p3"
    ],
    "e1-ioc-00": [
      "r17-b3-ioc-p3",
      "r17-b2-ioc-p2",
      "r17-b2-ioc-p5",
      "r17-b2-ioc-p8",
      "r17-b2-ioc-p0",
      "r17-b3-ioc-p6",
      "r17-b3-ioc-p7",
      "r17-b2-ioc-p3"
    ],
    "e1-ioc-01": [
      "r17-b3-ioc-p0",
      "r17-b3-ioc-p5",
      "r17-b2-ioc-p6",
      "r17-b2-ioc-p7",
      "r17-b3-ioc-p4",
      "r17-b2-ioc-p1",
      "r17-b3-ioc-p1",
      "r17-b3-ioc-p8"
    ],
    "e1-msp-00": [
      "r17-b2-msp-p4",
      "r17-b3-msp-p4",
      "r17-b2-msp-p8",
      "r17-b3-msp-p3",
      "r17-b3-msp-p2",
      "r17-b2-msp-p6",
      "r17-b3-msp-p0",
      "r17-b3-msp-p8"
    ],
    "e1-msp-01": [
      "r17-b3-msp-p5",
      "r17-b2-msp-p1",
      "r17-b3-msp-p1",
      "r17-b2-msp-p2",
      "r17-b2-msp-p7",
      "r17-b3-msp-p7",
      "r17-b2-msp-p5",
      "r17-b3-msp-p6"
    ],
    "e1-ska-00": [
      "r17-b2-ska-p3",
      "r17-b2-ska-p1",
      "r17-b2-ska-p4",
      "r17-b3-ska-p8",
      "r17-b3-ska-p2",
      "r17-b3-ska-p6",
      "r17-b2-ska-p6",
      "r17-b2-ska-p7"
    ],
    "e1-ska-01": [
      "r17-b2-ska-p8",
      "r17-b3-ska-p1",
      "r17-b3-ska-p7",
      "r17-b3-ska-p0",
      "r17-b2-ska-p5",
      "r17-b3-ska-p5",
      "r17-b3-ska-p3",
      "r17-b2-ska-p0"
    ],
    "e1-tsr-00": [
      "r17-b3-tsr-p7",
      "r17-b3-tsr-p0",
      "r17-b2-tsr-p3",
      "r17-b2-tsr-p8",
      "r17-b2-tsr-p2",
      "r17-b2-tsr-p5",
      "r17-b2-tsr-p4",
      "r17-b3-tsr-p8"
    ],
    "e1-tsr-01": [
      "r17-b2-tsr-p0",
      "r17-b2-tsr-p6",
      "r17-b2-tsr-p1",
      "r17-b3-tsr-p3",
      "r17-b3-tsr-p1",
      "r17-b3-tsr-p4",
      "r17-b3-tsr-p6",
      "r17-b3-tsr-p5"
    ]
  },
  "e3_future_reserve_integrity_only": [
    "r17-b5-agj-p8",
    "r17-b5-msp-p3",
    "r17-b5-ska-p7",
    "r17-b5-tsr-p8",
    "r17-b6-agj-p7",
    "r17-b6-fmv-p0",
    "r17-b6-fmv-p7",
    "r17-b6-ioc-p2",
    "r17-b6-ioc-p7",
    "r17-b6-msp-p8",
    "r17-b6-ska-p3",
    "r17-b6-tsr-p3"
  ],
  "e3_future_streams": {
    "e3-agj-00": [
      "r17-b5-agj-p4",
      "r17-b5-agj-p6",
      "r17-b5-agj-p3",
      "r17-b5-agj-p7",
      "r17-b6-agj-p5",
      "r17-b6-agj-p1",
      "r17-b6-agj-p3",
      "r17-b6-agj-p0"
    ],
    "e3-agj-01": [
      "r17-b5-agj-p0",
      "r17-b5-agj-p1",
      "r17-b5-agj-p5",
      "r17-b6-agj-p6",
      "r17-b6-agj-p8",
      "r17-b5-agj-p2",
      "r17-b6-agj-p4",
      "r17-b6-agj-p2"
    ],
    "e3-fmv-00": [
      "r17-b5-fmv-p6",
      "r17-b5-fmv-p3",
      "r17-b5-fmv-p5",
      "r17-b6-fmv-p1",
      "r17-b6-fmv-p5",
      "r17-b5-fmv-p0",
      "r17-b5-fmv-p1",
      "r17-b6-fmv-p6"
    ],
    "e3-fmv-01": [
      "r17-b6-fmv-p3",
      "r17-b5-fmv-p8",
      "r17-b5-fmv-p4",
      "r17-b5-fmv-p2",
      "r17-b6-fmv-p2",
      "r17-b5-fmv-p7",
      "r17-b6-fmv-p8",
      "r17-b6-fmv-p4"
    ],
    "e3-ioc-00": [
      "r17-b5-ioc-p5",
      "r17-b6-ioc-p1",
      "r17-b5-ioc-p3",
      "r17-b6-ioc-p4",
      "r17-b6-ioc-p3",
      "r17-b5-ioc-p0",
      "r17-b6-ioc-p5",
      "r17-b6-ioc-p0"
    ],
    "e3-ioc-01": [
      "r17-b5-ioc-p4",
      "r17-b5-ioc-p2",
      "r17-b5-ioc-p6",
      "r17-b5-ioc-p8",
      "r17-b6-ioc-p8",
      "r17-b5-ioc-p1",
      "r17-b6-ioc-p6",
      "r17-b5-ioc-p7"
    ],
    "e3-msp-00": [
      "r17-b6-msp-p6",
      "r17-b5-msp-p6",
      "r17-b6-msp-p4",
      "r17-b5-msp-p0",
      "r17-b5-msp-p5",
      "r17-b6-msp-p3",
      "r17-b5-msp-p8",
      "r17-b6-msp-p0"
    ],
    "e3-msp-01": [
      "r17-b6-msp-p1",
      "r17-b6-msp-p7",
      "r17-b6-msp-p2",
      "r17-b5-msp-p4",
      "r17-b5-msp-p1",
      "r17-b6-msp-p5",
      "r17-b5-msp-p2",
      "r17-b5-msp-p7"
    ],
    "e3-ska-00": [
      "r17-b5-ska-p2",
      "r17-b6-ska-p8",
      "r17-b5-ska-p8",
      "r17-b6-ska-p7",
      "r17-b5-ska-p5",
      "r17-b6-ska-p5",
      "r17-b5-ska-p6",
      "r17-b6-ska-p4"
    ],
    "e3-ska-01": [
      "r17-b6-ska-p2",
      "r17-b6-ska-p0",
      "r17-b5-ska-p0",
      "r17-b6-ska-p1",
      "r17-b5-ska-p3",
      "r17-b5-ska-p4",
      "r17-b5-ska-p1",
      "r17-b6-ska-p6"
    ],
    "e3-tsr-00": [
      "r17-b5-tsr-p7",
      "r17-b6-tsr-p6",
      "r17-b6-tsr-p4",
      "r17-b5-tsr-p2",
      "r17-b6-tsr-p2",
      "r17-b6-tsr-p1",
      "r17-b5-tsr-p4",
      "r17-b6-tsr-p7"
    ],
    "e3-tsr-01": [
      "r17-b5-tsr-p1",
      "r17-b5-tsr-p5",
      "r17-b6-tsr-p0",
      "r17-b5-tsr-p0",
      "r17-b6-tsr-p5",
      "r17-b6-tsr-p8",
      "r17-b5-tsr-p3",
      "r17-b5-tsr-p6"
    ]
  },
  "rules": {
    "development_never_promoted": true,
    "e1_probe_never_fed_to_updater": true,
    "e1_streams_are_single_family": true,
    "e3_future_unseen_until_prediction_freeze": true,
    "e3_streams_are_single_family": true,
    "reserve_never_replaces_model_failure_or_bad_outcome": true,
    "reserve_only_for_preexecution_file_integrity_failure": true
  },
  "schema_version": "1.0",
  "selection_algorithm": "SHA256(salt|task_id); family-balanced where stated",
  "selection_is_outcome_blind": true,
  "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
}


BOUND DOSSIER END
