You are an independent adversarial pre-execution reviewer for E2-R17 V3.1 provider-runtime Pilot. You are blind to the other reviewer. This review is runtime/measurability only and cannot authorize E1-B scientific execution, held-out future-skill evaluation, paper claims, frontend promotion, or submission.

Reviewer endpoint: deepseek-v4-pro
Exact draft contract SHA-256: eb1d24fd400faede9868dcd0a046bc392dd816538ebfec401e8ea454c6181f38

Context: E1-A has already frozen 96 exact K=8 pools and independently passed its pre-treatment support gate. This new Pilot is NOT allowed to inspect E1 held-out future-skill outcomes. It uses the exact same eight historical E0 pools, WIN-A/WIN-B/MRW arms, renderer, updater semantics and 10-per-arm/30-total provider budgets as the previously reviewed V1 draft. V1 was never executed because an execution-faithful preflight found R17-F008: the actor/evaluator venv did not contain the first-party SkillEvolver dependency closure (`omegaconf` missing). V2 changes only the role-specific runtime binding: a dedicated updater venv created from the pinned MindMemOS `uv.lock`/`mindmemos` package and then explicitly overridden to `tiktoken==0.11.0`, because the already frozen V3.1 renderer was independently qualified under exactly that tokenizer. The override is disclosed and hash-bound; it must not be treated as uv.lock-native.

Audit the exact contract and source code. Answer:

1. OUTCOME-BLIND SELECTION: Is the eight-pool selection rule fixed by path order rather than mixed/rescue/effect outcome? Does the Pilot avoid using any E1 held-out probe or learned-skill quality to select pools/model/renderer?

2. WIN-A / WIN-B IDENTICAL TREATMENT: Before provider calls, do WIN-A and WIN-B reuse the same pre-rendered winner BlindedEvidenceUnit list and same winner StreamProjection from the same initial skill and exact eight pools? Is the initial evidence byte-identical and score-identical? Hosted stochasticity may change later generated prompts; that is precisely what the later negative control measures and must not be confused with pre-provider treatment drift.

3. ARM BLINDING: Trace the actual first-party SkillEvolver path. Are updater-visible messages restricted to BlindedEvidenceUnit.evidence_text, with arm/projection/rollout/path/provider/provenance metadata outside model-visible messages? Does selected-evidence score, not served acting score, enter the updater's score field?

4. TOKEN PARITY: Is ExactMatchedEvidenceBlockRenderer used to match actual final re-tokenized WIN/MRW evidence length under frozen tiktoken 0.11.0 cl100k_base, with no padding? On nonmixed pools, does MRW equal WIN byte-for-byte? Is transcript_max_chars=100000 nonbinding and explicitly checked?

5. UPDATER SEMANTICS: Does the Pilot exercise real first-party MindMemOS SkillEvolver at pinned commit 9049182..., batch=8, temperature=0, retry=0, thinking disabled, max_parse_attempts=1, while measuring calls/tokens/latency/parse errors only? No learned-skill quality comparison may be performed.

6. PROVIDER BUDGET: Inspect the updater adapter and shared ProviderBudgetLedger. Does every hosted generation claim budget transactionally before provider I/O? Are limits 10 per arm / 30 total, contract+authorization bound, and claims never released after ambiguous failures? Are claims reflected in receipts? Could any parse-correction or poll recovery bypass the claim ceiling?

7. CHECKPOINT/RESUME: Is each completed arm persisted/content-addressed and placed in completed_arms.jsonl? On resume are completed receipt/skill SHAs and contract/auth/causal-purity mode revalidated? Most importantly, if a provider-call directory exists for an incomplete arm, does the Pilot STOP instead of automatically rerunning that arm?

8. ROLE-SPECIFIC RUNTIME / IDENTITY: Is V2 correct to refuse inheritance from the actor/evaluator runtime and instead bind a dedicated persistent-updater runtime? Does `validate_updater_runtime` verify exact venv/bin/python, final freeze SHA, updater-runtime qualification SHA/status, MindMemOS source binding, and a fresh exact-entrypoint smoke importing `mindmemos.pipelines.skill.evolution.SkillEvolver`, qdrant, omegaconf and tiktoken==0.11.0 before provider I/O? Is fresh DeepSeek resolved identity also requalified and bound?

9. POST-LOCK OVERRIDE: MindMemOS's frozen core environment initially resolves tiktoken 0.13.0, while the already pre-frozen V3.1 renderer requires tiktoken 0.11.0/cl100k_base. V2 explicitly installs 0.11.0 after the frozen MindMemOS sync, freezes the final environment, records the override and reruns first-party updater + renderer/adapter/budget zero-provider qualifications. Is this transparent, reproducible and scientifically acceptable for this Pilot? Flag it if it creates an untested incompatibility or hidden change in updater semantics.

10. FAILURE PRESERVATION / RESUME: V2 preserves the old unexecuted V1 draft as superseded due R17-F008. During V2 execution, does any exception/partial arm keep the exclusive lock, preserve provider-call artifacts and refuse automatic rerun, while a fully successful Pilot alone removes the lock? Is this preferable to silently retrying ambiguous hosted calls?

11. SCIENTIFIC INVARIANCE: Verify that the exact historical eight pool SHAs, pool order, three arms, evidence renderer, selected-evidence score semantics, updater configuration, and provider budget are unchanged from V1; only the runtime qualification/binding and fail-safe lock behavior changed. If a scientific treatment changed, this is blocking.

12. SCIENTIFIC BOUNDARY: Confirm zero new actor rollouts, zero E1 held-out evaluation, zero learned-skill quality comparison, zero method-effect GO/HOLD/STOP, and zero E1-B authority. A PASS may recommend only minting a separate SHA-bound provider-runtime Pilot authorization.

13. DECISION: PASS only if there is no P0/P1 blocker. Keep E1-B HOLD and paper_claim_authority=false regardless of Pilot readiness.

Return exactly one JSON object and no markdown using this schema:
{
  "draft_contract_sha256_acknowledged": "",
  "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_PROVIDER_RUNTIME_PILOT|REVISE_PROVIDER_RUNTIME_PILOT|STOP_PROVIDER_RUNTIME_PILOT",
  "outcome_blind_selection_assessment": "",
  "win_clone_identity_assessment": "",
  "arm_blinding_assessment": "",
  "token_parity_assessment": "",
  "updater_semantics_assessment": "",
  "provider_budget_assessment": "",
  "checkpoint_resume_assessment": "",
  "runtime_and_model_identity_assessment": "",
  "scientific_boundary_assessment": "",
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
  "provider_runtime_pilot_recommendation": "ALLOW_SEPARATE_FROZEN_PROVIDER_RUNTIME_PILOT_AUTHORIZATION|HOLD|STOP",
  "e1_b_recommendation": "HOLD|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}

Set `draft_contract_sha256_acknowledged` exactly to the SHA above. For PASS use verdict `PASS_TO_SEPARATELY_AUTHORIZED_PROVIDER_RUNTIME_PILOT` and recommendation `ALLOW_SEPARATE_FROZEN_PROVIDER_RUNTIME_PILOT_AUTHORIZATION`. Keep e1_b_recommendation=HOLD and paper_claim_authority=false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: provider_runtime_pilot_draft | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v31-provider-runtime-pilot-v2-draft-contract-20260829.json =====
{
  "arm_semantics": {
    "mrw": "V3.1 arm-blinded mixed-rejected-witness evidence for runtime/measurability only; no future-skill comparison is permitted in this Pilot.",
    "win_a": "V3.1 arm-blinded winner evidence from the eight exact historical pools.",
    "win_b": "Independent hosted-updater call sequence from a fresh cloned state receiving the exact same pre-provider winner evidence bytes as WIN-A."
  },
  "arms": [
    "win_a",
    "win_b",
    "mrw"
  ],
  "artifact_type": "e2-r17-v31-provider-runtime-pilot-contract",
  "authority": {
    "e1_b": false,
    "frontend_promotion": false,
    "independent_review": true,
    "paper_promotion": false,
    "provider_runtime_pilot": false,
    "scientific_experiment": false,
    "submission": false
  },
  "bound_code": {
    "adapter_tests": {
      "path": "research_pipeline/test_e2_r17_mindmemos_ark_adapter.py",
      "sha256": "29a0dc539fddc33a710876efd33931b091f75fa68fd239a396e4e6f5fa182f8c"
    },
    "provider_budget": {
      "path": "research_pipeline/e2_r17_provider_budget.py",
      "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
    },
    "provider_budget_tests": {
      "path": "research_pipeline/test_e2_r17_provider_budget.py",
      "sha256": "443b0377941a4fbba1a6eaf7fa5af8e33615511b43890bd73da19a8ec94b61eb"
    },
    "renderer": {
      "path": "research_pipeline/e2_r17_evidence_window_v2.py",
      "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7"
    },
    "renderer_tests": {
      "path": "research_pipeline/test_e2_r17_evidence_window_v2.py",
      "sha256": "4a217180b9711ed829e5d1e7be952d48698ca5572980f9c887457b28b5c84611"
    },
    "review_harness_ack_tests": {
      "path": "research_pipeline/test_e2_r17_review_harness_ack.py",
      "sha256": "3a985b963402f53137051aafa8007df44c6cc736dedf1e45cdd6ee8c2e901f78"
    },
    "runner": {
      "path": "scripts/run_e2_r17_v31_provider_runtime_pilot.py",
      "sha256": "533f11ba2bfc85aa6fcea8bc1b9502a039cd7770055010a8838b78bb8b6041d5"
    },
    "updater_adapter": {
      "path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
      "sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8"
    },
    "updater_tests": {
      "path": "research_pipeline/test_e2_r17_mindmemos_updater_v31.py",
      "sha256": "874fc99106e2f85f67180f4962f50b50ad2d921c8ba5ad8fad54fb12f62ded9f"
    },
    "updater_wrapper": {
      "path": "research_pipeline/e2_r17_mindmemos_updater.py",
      "sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
    }
  },
  "budget": {
    "claim_before_provider_io": true,
    "claims_never_released": true,
    "ledger_relative_path": "checkpoints/provider_budget.sqlite3",
    "max_provider_calls": 30,
    "max_provider_calls_per_arm": 10
  },
  "checkpoint": {
    "completed_manifest": "checkpoints/completed_arms.jsonl",
    "partial_ambiguous_arm": "STOP_AND_ADJUDICATE; never auto-rerun a directory containing provider-call artifacts without a complete manifest",
    "persist_immediately": true,
    "resume": "revalidate completed arm receipt and skill SHA; execute missing arms only",
    "unit": "complete updater arm"
  },
  "date": "2026-08-29",
  "failure_registry": {
    "path": "generated/e2-r17-failure-differential-registry-20260829.json",
    "sha256": "5aeb331a759e0b681512e4fafab6907cbf191bdd4d3d6d4402cf423fc0592676",
    "trigger_failure_id": "R17-F008-UPDATER-RUNTIME-COVERAGE"
  },
  "forbidden": [
    "new actor rollouts",
    "E1 held-out probe evaluation",
    "comparison of learned skill quality",
    "scientific-effect GO/HOLD/STOP",
    "task/model/renderer selection based on learned-skill outcome",
    "E1-B scientific execution",
    "paper promotion",
    "frontend promotion",
    "submission"
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
  "measurements_allowed": [
    "provider calls per arm",
    "provider input/output/total tokens",
    "provider call wall time",
    "parse-error/correction frequency",
    "resolved model identity",
    "temperature/retry/thinking receipts",
    "provider-budget claims",
    "content-addressed update receipt and skill artifact integrity"
  ],
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
  "purpose": "Outcome-blind real-provider runtime/measurability qualification for the V3.1 MindMemOS updater path before any E1-B scientific authorization. V2 changes only the role-specific updater runtime binding after R17-F008; the historical pools, three arms, renderer, updater semantics, and provider budgets are unchanged.",
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
    "contract-bound frozen venv is active before any provider call",
    "fresh DeepSeek resolved identity matches deepseek-v4-pro-ga-260813",
    "all eight historical pool and trajectory SHAs revalidate",
    "WIN-A and WIN-B share exact pre-provider winner evidence bytes and selected-evidence scores",
    "MRW differs from WIN only according to the frozen mixed-pool rule",
    "WIN/MRW final provider-visible evidence token counts match exactly within each pool",
    "no projection/role/rollout/path/provider/provenance labels enter model-visible evidence",
    "provider retries zero; temperature zero; thinking disabled",
    "provider budget claimed transactionally before I/O with 10-call per-arm and 30-call global hard ceilings",
    "each complete updater arm is content-addressed and checkpointed immediately",
    "ambiguous partial arm is never automatically rerun",
    "no held-out probe evaluation and no method-effectiveness comparison occurs",
    "dedicated updater runtime freeze and qualification SHA revalidate before any provider call",
    "runner is itself executed by the exact dedicated updater venv/bin/python",
    "fresh exact-entrypoint smoke imports MindMemOS SkillEvolver, qdrant client, omegaconf and tiktoken==0.11.0 before provider I/O",
    "post-lock tiktoken==0.11.0 compatibility override is explicit and not described as uv.lock-native",
    "failed/partial provider arm preserves stale exclusive lock and cannot auto-rerun"
  ],
  "run_root": "/data/wyt/e2-r17-search-projection/runtime-pilots/v31-provider-updater-v2-20260829",
  "runtime": {
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
  },
  "schema_version": "1.0",
  "status": "DRAFT_V2_PENDING_DUAL_PREEXECUTION_REVIEW",
  "supersedes": {
    "path": "generated/e2-r17-v31-provider-runtime-pilot-draft-contract-20260828.json",
    "reason": "R17-F008: the V1 draft inherited an actor/evaluator runtime that did not contain the first-party SkillEvolver dependency closure. No provider-runtime Pilot call was executed under V1.",
    "sha256": "b7340add5392667551ab6838f6acf32876bec8b3d75bcd1a82fdfdcacb7254a1"
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
  "upstream_e1_a_support": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
    "required_status": "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT",
    "sha256": "b2c611285c20377d77af7ea62448c6fee0d5973cd657687f6dde7f7fce6be6d7"
  }
}


===== BOUND ARTIFACT: provider_runtime_pilot_runner | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_v31_provider_runtime_pilot.py =====
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


===== BOUND ARTIFACT: failure_differential_registry | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-failure-differential-registry-20260829.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-failure-differential-registry",
  "date": "2026-08-29",
  "status": "ACTIVE_CANONICAL_FAILURE_LEDGER_FOR_R17_WORKTREE",
  "purpose": "Every R17 execution attempt must terminate as a valid success or as an explicitly classified failure. Technical/protocol/measurement failures are separated from qualified scientific-mechanism failures so that repairs cannot silently rewrite scientific evidence and scientific negatives cannot be laundered into engineering bugs.",
  "taxonomy": {
    "IMPLEMENTATION": "Local code, launcher, parser, review harness, checkpoint, or accounting defect before a valid scientific endpoint.",
    "RUNTIME_INFRA": "Environment/dependency/role-runtime or provider-route failure that prevents the frozen scientific procedure from reaching its endpoint.",
    "PROTOCOL_CAUSAL_PURITY": "A design or dataflow defect that changes or leaks treatment, invalidating causal interpretation even if code runs.",
    "MEASUREMENT_ANALYSIS": "Estimator, renderer, token/accounting, or adjudicator failure that invalidates the intended measurement without establishing a scientific negative.",
    "SCIENTIFIC_MECHANISM": "A protocol-valid, fully qualified primary experiment reaches its endpoint and rejects/equates/harms the central mechanism under the frozen decision rule. This class triggers scientific STOP unless a predeclared scope limitation applies."
  },
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
  "entries": [
    {
      "failure_id": "R17-F001-V3-BPE-PARITY",
      "stage": "V3 mechanical runtime pilot",
      "terminal_status": "FAIL_MECHANICAL_TOKEN_PARITY",
      "classification": ["MEASUREMENT_ANALYSIS", "PROTOCOL_CAUSAL_PURITY"],
      "symptom": "Nominally equal source-token slices re-tokenized to unequal final provider-visible lengths after head/tail decoding and concatenation.",
      "root_cause": "BPE can create a new merge at the splice boundary; equal selected source-token counts do not imply equal final rendered token counts.",
      "provider_calls": 0,
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "NONE",
      "preserved_artifacts": [
        {"path": "generated/e2-r17-v3-runtime-pilot-failure-adjudication-20260828.json", "sha256": "fec66715370144f4b8c72c7afd32520f9f990ef466f988c0d77cf3a954aefcef"}
      ],
      "repair_or_stop": "New V3.1 ExactMatchedEvidenceBlockRenderer matches the actual final re-tokenized evidence block, uses deterministic no-padding search, and preserves old failed V3 root/contract.",
      "rerun_policy": "PERMITTED_ONLY_UNDER_NEW_V3_1_CONTRACT_AND_FRESH_ROOT",
      "scientific_belief_update": "NONE",
      "reusable_rule": "Fairness budgets must bind the exact model-visible representation after all rendering/transformation steps, not an upstream proxy count."
    },
    {
      "failure_id": "R17-F002-LEGACY-PROJECTION-LEAK",
      "stage": "V3 causal-purity audit",
      "terminal_status": "LEGACY_PATH_INVALID_FOR_CAUSAL_E1",
      "classification": ["PROTOCOL_CAUSAL_PURITY"],
      "symptom": "Legacy updater packet exposed PROJECTION/ROLE/rollout/provenance labels and could attach the served winner score to a failed MRW transcript.",
      "root_cause": "Acting provenance and learner-visible evidence semantics were not separated in the original wrapper.",
      "provider_calls": 0,
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "Legacy path is disqualified from causal interpretation; historical artifacts remain non-authoritative for E1.",
      "preserved_artifacts": [
        {"path": "consultations/e2-r17-v3-1-causal-purity-repair-20260828.md", "sha256": "94490232790ec78cdcb5773b49bb9fcb509ca18b8cc5cc2842216d0becb25521"}
      ],
      "repair_or_stop": "V3.1 BlindedEvidenceUnit exposes only selected evidence text in messages, stores selected trajectory verifier score as the learner outcome, and keeps acting/projection provenance in audit-only r17_* fields.",
      "rerun_policy": "PERMITTED_ONLY_ON_V3_1_BLINDED_PATH",
      "scientific_belief_update": "NONE; old path was causally invalid.",
      "reusable_rule": "For same-pool causal interventions, provenance required for audit must be kept out of model-visible treatment unless it is itself a predeclared treatment variable."
    },
    {
      "failure_id": "R17-F003-E1A-BUDGET-POSTHOC",
      "stage": "E1-A pre-execution review",
      "terminal_status": "HOLD_PRECALL_BUDGET_GUARD_MISSING",
      "classification": ["IMPLEMENTATION"],
      "symptom": "The declared 10-call per-rollout / 7680-call total ceiling was checked after execution or delegated to an unbound runtime rather than enforced before provider I/O.",
      "root_cause": "Budget accounting was observational instead of transactional.",
      "provider_calls": 0,
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "NONE",
      "preserved_artifacts": [
        {"path": "research_pipeline/e2_r17_provider_budget.py", "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"}
      ],
      "repair_or_stop": "SQLite BEGIN IMMEDIATE ledger claims budget before provider I/O, binds contract+authorization, never releases ambiguous claims, and fail-closes before the 11th per-unit or 7681st total call.",
      "rerun_policy": "PERMITTED_AFTER_BOUND_GUARD_TESTS_AND_NEW_AUTHORIZATION",
      "scientific_belief_update": "NONE",
      "reusable_rule": "A scientific provider-call ceiling is a pre-I/O safety invariant, not a post-hoc statistic."
    },
    {
      "failure_id": "R17-F004-E1A-AMBIENT-PYTHON",
      "stage": "E1-A V2 pool-support execution",
      "terminal_status": "TECHNICAL_FAILURE_BEFORE_FIRST_ROLLOUT",
      "classification": ["RUNTIME_INFRA", "IMPLEMENTATION"],
      "symptom": "MindMemOS import failed with ModuleNotFoundError: pydantic before any rollout/provider call.",
      "root_cause": "E1-A orchestrator launched the actor with ambient /usr/bin/python3 instead of the previously qualified frozen actor/evaluator venv.",
      "provider_calls": 0,
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "NONE; zero budget claims and zero completed rollout refs.",
      "preserved_artifacts": [
        {"path": "generated/e2-r17-e1-a-v2-runtime-failure-adjudication-20260828.json", "sha256": "3ad8b73ce13f8b5bc0e51f109a8e910e0894656d3bdd94f10290126a3388a399"},
        {"path": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-20260828/.exclusive.lock", "sha256": null},
        {"path": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-20260828/checkpoints/failures/e1-agj-00.json", "sha256": null}
      ],
      "repair_or_stop": "V2.1 binds exact actor venv/bin/python, VIRTUAL_ENV/PATH, runtime freeze SHA and qualification SHA before spawning any actor.",
      "rerun_policy": "PERMITTED_UNDER_NEW_V2_1_CONTRACT_AND_FRESH_ROOT; FAILED_V2_ROOT_NOT_REUSED",
      "scientific_belief_update": "NONE",
      "reusable_rule": "Runtime qualification must be executable-binding, not merely package-list provenance."
    },
    {
      "failure_id": "R17-F005-SUPPORT-ZERO-FALSY",
      "stage": "E1-A post-run support adjudication",
      "terminal_status": "ADJUDICATOR_MECHANICAL_FAILURE",
      "classification": ["MEASUREMENT_ANALYSIS", "IMPLEMENTATION"],
      "symptom": "A valid updater_calls=0 summary was parsed as -1 by int(summary.get('updater_calls') or -1).",
      "root_cause": "Python falsy semantics incorrectly treated a meaningful zero as missing.",
      "provider_calls": 0,
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "Frozen 96 pools remained intact; thresholds/data were not changed.",
      "preserved_artifacts": [
        {"path": "generated/e2-r17-e1-a-support-adjudicator-zero-parse-repair-20260828.json", "sha256": "e632988b3ebf39588caaaa7b9b425b869e6d06656353506ef0c8782b5ca33d50"},
        {"path": "scripts/adjudicate_e2_r17_e1_a_pool_support_v2.py", "sha256": "cc5d43828179bbdcc932a3194140cb798ccfb9b6d60bda6a44090ae4983601a6"}
      ],
      "repair_or_stop": "Versioned adjudicator v2 changes only zero/missing parsing; the repair was independently reviewed before adjudicating the same frozen 96-pool artifact.",
      "rerun_policy": "REPARSE_SAME_FROZEN_ARTIFACT_ONLY; NO_NEW_ROLLOUTS",
      "scientific_belief_update": "NONE until repaired adjudicator reached the support endpoint.",
      "reusable_rule": "Scientific counters where zero is meaningful must distinguish absent/null from zero explicitly; never use truthiness as missingness."
    },
    {
      "failure_id": "R17-F006-REVIEW-ACK-SCHEMA",
      "stage": "V3.1 provider-runtime Pilot independent review",
      "terminal_status": "LOCAL_FAIL_SCHEMA_WITH_VALID_MODEL_CONTENT",
      "classification": ["IMPLEMENTATION"],
      "symptom": "Both Kimi and DeepSeek returned complete PASS reviews, but the shared local validator required the historical repair_sha256_acknowledged field while the new schema defined draft_contract_sha256_acknowledged.",
      "root_cause": "Review-harness validation hard-coded one historical acknowledgement field name instead of validating the acknowledgement field declared by the active schema.",
      "provider_calls": "2 original reviewer generations; 0 additional calls for repair/re-adjudication",
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "NONE; exact raw reviewer outputs were preserved and reparsed.",
      "preserved_artifacts": [
        {"path": "generated/e2-r17-v31-provider-runtime-pilot-review-reparsed-20260829.json", "sha256": "c7ae640e240975da32d50b1e63322ed49c481ed20f8735b71da67f7366728656"},
        {"path": "research_pipeline/test_e2_r17_review_harness_ack.py", "sha256": "3a985b963402f53137051aafa8007df44c6cc736dedf1e45cdd6ee8c2e901f78"},
        {"path": "scripts/adjudicate_e2_r17_v31_provider_runtime_pilot_review_reparse.py", "sha256": "618a2610281492b20c7ec0c763c255413a5f1f1bbd21463ed5085118f18a5cd0"}
      ],
      "repair_or_stop": "Shared validator now discovers active schema fields ending in _sha256_acknowledged, validates each exact SHA, remains backward-compatible, and fail-closes on wrong/missing acknowledgements. Existing model outputs were zero-provider reparsed.",
      "rerun_policy": "NO_NEW_REVIEWER_CALL_REQUIRED_WHEN_RAW_OUTPUT_IS_SEMANTICALLY_COMPLETE",
      "scientific_belief_update": "NONE",
      "reusable_rule": "Keep model generation and local schema adjudication as separate evidence layers; a parser failure does not erase a valid raw review."
    },
    {
      "failure_id": "R17-F007-REPARSE-IMPORT-PATH",
      "stage": "Zero-provider review re-adjudication utility",
      "terminal_status": "SCRIPT_IMPORT_FAILURE_THEN_REPAIRED",
      "classification": ["IMPLEMENTATION"],
      "symptom": "Direct execution of the new reparse script initially failed before reading review data because repo root was not inserted into sys.path.",
      "root_cause": "Launcher omitted the standard repository-root import binding used by other R17 scripts.",
      "provider_calls": 0,
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "NONE",
      "preserved_artifacts": [
        {"path": "scripts/adjudicate_e2_r17_v31_provider_runtime_pilot_review_reparse.py", "sha256": "618a2610281492b20c7ec0c763c255413a5f1f1bbd21463ed5085118f18a5cd0"}
      ],
      "repair_or_stop": "Added explicit ROOT insertion before importing sibling scripts; successful second invocation reused the same raw reviews.",
      "rerun_policy": "PERMITTED_ZERO_PROVIDER_REPARSE",
      "scientific_belief_update": "NONE",
      "reusable_rule": "Standalone adjudication scripts must prove their own import-path reproducibility before being treated as evidence processors."
    },
    {
      "failure_id": "R17-F008-UPDATER-RUNTIME-COVERAGE",
      "stage": "V3.1 provider-runtime Pilot preflight",
      "terminal_status": "HOLD_PROVIDER_RUNTIME_PILOT_BEFORE_PROVIDER_CALL",
      "classification": ["RUNTIME_INFRA", "IMPLEMENTATION"],
      "symptom": "The actor/evaluator venv could import mindmemos_eval but failed importing first-party mindmemos.pipelines.skill.evolution.SkillEvolver because omegaconf was absent.",
      "root_cause": "The existing runtime qualification covered the actor/evaluator entrypoints, not the persistent-updater dependency closure. The provider-runtime Pilot inherited a role-inappropriate runtime assumption.",
      "provider_calls": 0,
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "NONE; provider Pilot run root remained fresh.",
      "preserved_artifacts": [
        {"path": "/data/wyt/e2-r17-search-projection/runtime-qualifications/updater-runtime-zero-provider-20260829.json", "sha256": "9d2f4e3525a04a55128e3592f44531226962084613adf1bca17f0f96f7d521a9"},
        {"path": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv.freeze.txt", "sha256": "80cd6fdd8eb672e41252c099766fd171a5a7a4b90c284d87da87d09f0d559731"}
      ],
      "repair_or_stop": "Created a dedicated updater runtime from pinned MindMemOS uv.lock/package, then explicitly applied the predeclared R17 renderer compatibility override tiktoken==0.11.0; first-party SkillEvolver import and zero-provider six-arm updater qualification pass under this dedicated runtime.",
      "rerun_policy": "PROVIDER_RUNTIME_PILOT_MAY_BE_REDESIGNED_ONLY_WITH_DEDICATED_UPDATER_RUNTIME_BOUND_IN_NEW_CONTRACT",
      "scientific_belief_update": "NONE",
      "reusable_rule": "Runtime qualification is role-specific and must import/exercise the exact scientific entrypoint; actor/evaluator qualification never authorizes updater execution."
    },
    {
      "failure_id": "R17-F009-PREFLIGHT-SOURCE-BINDING",
      "stage": "Updater runtime diagnosis",
      "terminal_status": "NONAUTHORITATIVE_PREFLIGHT_MISMATCH",
      "classification": ["IMPLEMENTATION"],
      "symptom": "An initial manual updater import check could not find mindmemos because it did not reproduce the runner's source-tree sys.path binding.",
      "root_cause": "The diagnostic preflight did not mirror the actual execution environment/source binding.",
      "provider_calls": 0,
      "scientific_endpoint_reached": false,
      "scientific_data_observed_for_effectiveness": false,
      "contamination": "NONE",
      "preserved_artifacts": [],
      "repair_or_stop": "Repeated the check with the exact three source roots bound; that authoritative preflight then exposed the real missing omegaconf dependency in the actor venv.",
      "rerun_policy": "DIAGNOSTIC_RECHECK_PERMITTED_WITH_EXECUTION-FAITHFUL_BINDING",
      "scientific_belief_update": "NONE",
      "reusable_rule": "A preflight that does not reproduce the execution binding is diagnostic noise and must not authorize or block science by itself."
    }
  ],
  "current_scientific_state": {
    "e0_censoring_existence": "SUPPORTED_ON_CONTROLLED_PILOT",
    "e1_a_treatment_support": "PASS_STRONG_SUPPORT_78_OF_96_MIXED_12_OF_12_STREAMS_6_OF_6_FAMILIES",
    "provider_runtime_pilot": "HOLD_PENDING_DEDICATED_UPDATER_RUNTIME_V2_CONTRACT_AND_REVIEW",
    "e1_b_negative_control": "NOT_AUTHORIZED",
    "e1_b_mrw_causal_effect": "UNKNOWN",
    "central_mechanism": "OPEN_NOT_YET_ADJUDICATED"
  }
}


===== BOUND ARTIFACT: prior_unexecuted_v1_draft | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v31-provider-runtime-pilot-draft-contract-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-v31-provider-runtime-pilot-contract",
  "date": "2026-08-28",
  "status": "DRAFT_PENDING_DUAL_PREEXECUTION_REVIEW",
  "purpose": "Outcome-blind real-provider runtime/measurability qualification for the V3.1 MindMemOS updater path before any E1-B scientific authorization.",
  "run_root": "/data/wyt/e2-r17-search-projection/runtime-pilots/v31-provider-updater-20260828",
  "upstream_e1_a_support": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
    "sha256": "b2c611285c20377d77af7ea62448c6fee0d5973cd657687f6dde7f7fce6be6d7",
    "required_status": "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT"
  },
  "historical_inputs": {
    "source": "E0 historical pools only",
    "e0_root": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828",
    "selection_rule": "Lexicographically first eight pool_k8.json paths, frozen before reading mixed/rescue/outcome fields for this Pilot.",
    "selected_pools": [
      {"task_id": "r17-b1-agj-p1", "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-agj-p1/pool_k8.json", "sha256": "3872f2b33f11130aeed073e46650c7d6c4a13c256632252a7102ea81c8492c0c"},
      {"task_id": "r17-b1-agj-p4", "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-agj-p4/pool_k8.json", "sha256": "1afa7d56dca0b3b04ab4c494e05c43ad49f6015e928cf8348a61af81eb753813"},
      {"task_id": "r17-b1-fmv-p4", "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-fmv-p4/pool_k8.json", "sha256": "2b852fc1f2f41cc68e1869ce3f11f552ca176e63fd1121a528fa4361ade7e989"},
      {"task_id": "r17-b1-fmv-p8", "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-fmv-p8/pool_k8.json", "sha256": "945fde93b9812ceb750cace1140bb383eb59a2f1ae2fa966dc7723fe1ebd9d03"},
      {"task_id": "r17-b1-ioc-p2", "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-ioc-p2/pool_k8.json", "sha256": "5a5c6bc214b05fc807387cf32766aa6f0f42617af04ac24e0b9993d431169bdc"},
      {"task_id": "r17-b1-ioc-p5", "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-ioc-p5/pool_k8.json", "sha256": "7e5f613d500b2be2b40d42d4124b12213ee989619f0b6f464649522b194645df"},
      {"task_id": "r17-b1-msp-p0", "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-msp-p0/pool_k8.json", "sha256": "10d950ffdad2dce1957c9bac73f5f4e4816db47cff40bc4177ab4f8930f8834e"},
      {"task_id": "r17-b1-msp-p2", "path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/cases/r17-b1-msp-p2/pool_k8.json", "sha256": "18ce3604f249ecbbddab21dd39b9f9db67861c41cb97cd7866dbf5c5e9d1355c"}
    ]
  },
  "arms": ["win_a", "win_b", "mrw"],
  "arm_semantics": {
    "win_a": "V3.1 arm-blinded winner evidence from the eight exact historical pools.",
    "win_b": "Independent hosted-updater call sequence from a fresh cloned state receiving the exact same pre-provider winner evidence bytes as WIN-A.",
    "mrw": "V3.1 arm-blinded mixed-rejected-witness evidence for runtime/measurability only; no future-skill comparison is permitted in this Pilot."
  },
  "renderer": {
    "path": "research_pipeline/e2_r17_evidence_window_v2.py",
    "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0",
    "tokenizer_encoding": "cl100k_base",
    "final_block_cap_tokens": 3072,
    "padding": false,
    "exact_final_retokenized_parity_required": true,
    "arm_metadata_visible": false
  },
  "updater": {
    "first_party": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "wrapper_path": "research_pipeline/e2_r17_mindmemos_updater.py",
    "wrapper_sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d",
    "adapter_path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
    "adapter_sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8",
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "max_parse_attempts": 1,
    "temperature": 0.0,
    "provider_retry_limit": 0,
    "thinking": "disabled",
    "transcript_max_chars": 100000,
    "batch_size": 8,
    "score_semantics": "selected_evidence_trajectory"
  },
  "model_identity": {
    "path": "generated/e2-r17-v31-provider-pilot-model-identity-adjudication-20260828.json",
    "sha256": "2ea0412d672efe244acd40c4754a73b08158f3893e3f466dcff3a633e509425b",
    "qualification_path": "generated/e2-r17-v31-provider-pilot-model-identity-qualification-20260828.json",
    "qualification_sha256": "c920fa82199bf32071b0cb9c899b9002f091ef2e217ae8e6c7c763e9b1aab84a",
    "required_status": "PASS_CURRENT_REVIEW_TRANCHE"
  },
  "mindmemos": {
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "bound_files": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py": "771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e",
      "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py": "48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c"
    }
  },
  "initial_skill": {
    "path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
    "sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
  },
  "runtime": {
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2"
  },
  "budget": {
    "max_provider_calls_per_arm": 10,
    "max_provider_calls": 30,
    "claim_before_provider_io": true,
    "claims_never_released": true,
    "ledger_relative_path": "checkpoints/provider_budget.sqlite3"
  },
  "checkpoint": {
    "unit": "complete updater arm",
    "completed_manifest": "checkpoints/completed_arms.jsonl",
    "persist_immediately": true,
    "resume": "revalidate completed arm receipt and skill SHA; execute missing arms only",
    "partial_ambiguous_arm": "STOP_AND_ADJUDICATE; never auto-rerun a directory containing provider-call artifacts without a complete manifest"
  },
  "measurements_allowed": [
    "provider calls per arm",
    "provider input/output/total tokens",
    "provider call wall time",
    "parse-error/correction frequency",
    "resolved model identity",
    "temperature/retry/thinking receipts",
    "provider-budget claims",
    "content-addressed update receipt and skill artifact integrity"
  ],
  "forbidden": [
    "new actor rollouts",
    "E1 held-out probe evaluation",
    "comparison of learned skill quality",
    "scientific-effect GO/HOLD/STOP",
    "task/model/renderer selection based on learned-skill outcome",
    "E1-B scientific execution",
    "paper promotion",
    "frontend promotion",
    "submission"
  ],
  "bound_code": {
    "runner": {"path": "scripts/run_e2_r17_v31_provider_runtime_pilot.py", "sha256": "c203e49002490290e1f3366624e097671c2c6a1d1d988135601e53207d0f9f32"},
    "updater_adapter": {"path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py", "sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8"},
    "updater_wrapper": {"path": "research_pipeline/e2_r17_mindmemos_updater.py", "sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"},
    "renderer": {"path": "research_pipeline/e2_r17_evidence_window_v2.py", "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7"},
    "provider_budget": {"path": "research_pipeline/e2_r17_provider_budget.py", "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"},
    "runtime_validator": {"path": "scripts/run_e2_r17_e1_a_pool_support.py", "sha256": "24ea070b08399d48af99294615a508874f851af941f5bb0efabe341b0854617d"},
    "adapter_tests": {"path": "research_pipeline/test_e2_r17_mindmemos_ark_adapter.py", "sha256": "29a0dc539fddc33a710876efd33931b091f75fa68fd239a396e4e6f5fa182f8c"},
    "updater_tests": {"path": "research_pipeline/test_e2_r17_mindmemos_updater_v31.py", "sha256": "874fc99106e2f85f67180f4962f50b50ad2d921c8ba5ad8fad54fb12f62ded9f"},
    "renderer_tests": {"path": "research_pipeline/test_e2_r17_evidence_window_v2.py", "sha256": "4a217180b9711ed829e5d1e7be952d48698ca5572980f9c887457b28b5c84611"},
    "provider_budget_tests": {"path": "research_pipeline/test_e2_r17_provider_budget.py", "sha256": "443b0377941a4fbba1a6eaf7fa5af8e33615511b43890bd73da19a8ec94b61eb"}
  },
  "required_checks": [
    "contract-bound frozen venv is active before any provider call",
    "fresh DeepSeek resolved identity matches deepseek-v4-pro-ga-260813",
    "all eight historical pool and trajectory SHAs revalidate",
    "WIN-A and WIN-B share exact pre-provider winner evidence bytes and selected-evidence scores",
    "MRW differs from WIN only according to the frozen mixed-pool rule",
    "WIN/MRW final provider-visible evidence token counts match exactly within each pool",
    "no projection/role/rollout/path/provider/provenance labels enter model-visible evidence",
    "provider retries zero; temperature zero; thinking disabled",
    "provider budget claimed transactionally before I/O with 10-call per-arm and 30-call global hard ceilings",
    "each complete updater arm is content-addressed and checkpointed immediately",
    "ambiguous partial arm is never automatically rerun",
    "no held-out probe evaluation and no method-effectiveness comparison occurs"
  ],
  "authority": {
    "independent_review": true,
    "provider_runtime_pilot": false,
    "scientific_experiment": false,
    "e1_b": false,
    "paper_promotion": false,
    "frontend_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: prior_v1_review_reparse | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v31-provider-runtime-pilot-review-reparsed-20260829.json =====
{
  "artifact_type": "e2-r17-v31-provider-runtime-pilot-review-reparse-adjudication",
  "authority": {
    "execute_e1_b": false,
    "paper_promotion": false,
    "prepare_provider_runtime_pilot_authorization": true,
    "submission": false
  },
  "created_at_utc": "2026-08-29T10:43:15+00:00",
  "draft_contract_path": "generated/e2-r17-v31-provider-runtime-pilot-draft-contract-20260828.json",
  "draft_contract_sha256": "b7340add5392667551ab6838f6acf32876bec8b3d75bcd1a82fdfdcacb7254a1",
  "failure_classification": "IMPLEMENTATION/REVIEW_HARNESS_SCHEMA_VALIDATION",
  "original_fail_schema_preserved": true,
  "provider_generation_calls": 0,
  "provider_review_harness_path": "scripts/run_e2_r17_v31_provider_runtime_pilot_review.py",
  "provider_review_harness_sha256": "f38570580a159859c42e610af94844b26aa4ec9edb54ffb23762b264d2bbf45c",
  "reused_exact_model_outputs": true,
  "review_harness_path": "scripts/run_e2_r17_v3_1_review.py",
  "review_harness_sha256": "ef74d0fd83f5059aecf427902e260e38561a1c4f6083cd0fde402242708884af",
  "rows": {
    "deepseek-v4-pro": {
      "e1_b_recommendation": "HOLD",
      "original_missing_required_fields": [
        "repair_sha256_acknowledged_exact"
      ],
      "original_status": "FAIL_SCHEMA",
      "paper_claim_authority": false,
      "provider_runtime_pilot_recommendation": "ALLOW_SEPARATE_FROZEN_PROVIDER_RUNTIME_PILOT_AUTHORIZATION",
      "raw_text_sha256": "c5933c12bf695d5b5f10defff356156ee7beeba62cd207a9c7a996776169ed52",
      "remaining_blockers": [],
      "reparsed_missing_required_fields": [],
      "resolved_model": "deepseek-v4-pro-ga-260813",
      "resolved_model_matches_qualification": true,
      "single_sentence_verdict": "The provider-runtime Pilot is outcome-blind, arm-blinded, token-parity-enforced, budget-fail-closed, checkpoint-safe, and scientifically bounded, with no P0/P1 blockers, so it may proceed only under a separately minted SHA-bound provider-runtime Pilot authorization while E1-B remains HOLD and paper claims remain false.",
      "source_path": "generated/e2-r17-v31-provider-runtime-pilot-review-20260828/deepseek-v4-pro.json",
      "source_sha256": "2da6ce2e12b9d969bfa9b4f48986eb1fc5e169ca3995efaef4a221570a45cb42",
      "valid_after_harness_repair": true,
      "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_PROVIDER_RUNTIME_PILOT"
    },
    "kimi-k3": {
      "e1_b_recommendation": "HOLD",
      "original_missing_required_fields": [
        "repair_sha256_acknowledged_exact"
      ],
      "original_status": "FAIL_SCHEMA",
      "paper_claim_authority": false,
      "provider_runtime_pilot_recommendation": "ALLOW_SEPARATE_FROZEN_PROVIDER_RUNTIME_PILOT_AUTHORIZATION",
      "raw_text_sha256": "eb24f00087bbe94079d7ae50b2b9a16469944028ca8852a689236860f44a7398",
      "remaining_blockers": [],
      "reparsed_missing_required_fields": [],
      "resolved_model": "kimi-k3",
      "resolved_model_matches_qualification": true,
      "single_sentence_verdict": "The reviewed V3.1 provider-runtime Pilot is outcome-blind, arm-blinded, budgeted, checkpoint-safe, and runtime/measurability-only, so it may proceed only under a separate frozen provider-runtime authorization while E1-B remains on HOLD.",
      "source_path": "generated/e2-r17-v31-provider-runtime-pilot-review-20260828/kimi-k3.json",
      "source_sha256": "510de90e6cb078b775fba552e4fa4c0681de33416acd988eacb5682937036e6c",
      "valid_after_harness_repair": true,
      "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_PROVIDER_RUNTIME_PILOT"
    }
  },
  "schema_version": "1.0",
  "scientific_belief_update": "NONE; the original model content was valid and the failure was local schema validation only.",
  "status": "PASS_REPARSED_EXISTING_REVIEWS"
}


===== BOUND ARTIFACT: adapter_tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_mindmemos_ark_adapter.py =====
from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter
from research_pipeline.e2_r17_provider_budget import ProviderBudgetExceeded, ProviderBudgetLedger


class MindMemOSArkPlanAdapterTests(unittest.TestCase):
    def settings(self) -> ArkSettings:
        return ArkSettings(
            api_key="test-key",
            base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
            default_model="ark-code-latest",
            timeout_seconds=30,
            max_retries=0,
        )

    def test_raw_call_record_is_content_addressed_and_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter = MindMemOSArkPlanChatAdapter(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                record_dir=Path(tmp),
            )
            adapter.client.respond = lambda *args, **kwargs: {
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "text": "summary text",
                "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
                "response_id": "resp-secret-raw-id",
                "status": "completed",
            }
            response = asyncio.run(
                adapter.chat(
                    task="skill_trajectory_summary",
                    messages=[{"role": "user", "content": "trajectory"}],
                )
            )
            self.assertEqual(response.content, "summary text")
            receipts = adapter.public_receipts()
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["provider_retry_limit"], 0)
            record = Path(receipts[0]["record_path"])
            payload = json.loads(record.read_text(encoding="utf-8"))
            self.assertEqual(payload["response_text"], "summary text")
            self.assertEqual(payload["prompt_sha256"], receipts[0]["prompt_sha256"])
            self.assertFalse(payload["raw_response_id_included"])
            self.assertNotIn("resp-secret-raw-id", record.read_text(encoding="utf-8"))

    def test_parse_correction_is_explicit_not_hidden_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter = MindMemOSArkPlanChatAdapter(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                max_parse_attempts=2,
                record_dir=Path(tmp),
            )
            outputs = iter(["not-json", '{"ok": true}'])
            adapter.client.respond = lambda *args, **kwargs: {
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "text": next(outputs),
                "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
                "response_id": "private-id",
                "status": "completed",
            }

            def parser(text: str):
                return json.loads(text)

            response = asyncio.run(
                adapter.chat(
                    task="skill_patch_apply",
                    messages=[{"role": "user", "content": "apply"}],
                    format_parser=parser,
                    feedback_on_parse_error=True,
                )
            )
            self.assertEqual(response.parsed, {"ok": True})
            receipts = adapter.public_receipts()
            self.assertEqual(len(receipts), 2)
            self.assertTrue(receipts[0]["parse_error"])
            self.assertFalse(receipts[1]["parse_error"])
            self.assertTrue(all(not row["hidden_provider_retry_used"] for row in receipts))
            self.assertEqual([row["attempt"] for row in receipts], [0, 1])

    def test_provider_budget_blocks_before_updater_io(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = ProviderBudgetLedger(
                path=root / "budget.sqlite3",
                contract_sha256="a" * 64,
                authorization_sha256="b" * 64,
                total_limit=2,
                per_unit_limit=2,
                allow_create=True,
            )
            adapter = MindMemOSArkPlanChatAdapter(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                record_dir=root / "calls",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="stream-0/win-a",
            )
            provider_calls = 0

            def fake_respond(*args, **kwargs):
                nonlocal provider_calls
                provider_calls += 1
                return {
                    "resolved_model": "deepseek-v4-pro-ga-260813",
                    "text": "ok",
                    "usage": {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3},
                    "response_id": f"id-{provider_calls}",
                    "status": "completed",
                }

            adapter.client.respond = fake_respond
            for _ in range(2):
                asyncio.run(adapter.chat(task="skill_trajectory_summary", messages=[{"role": "user", "content": "x"}]))
            with self.assertRaisesRegex(ProviderBudgetExceeded, "before I/O"):
                asyncio.run(adapter.chat(task="skill_trajectory_summary", messages=[{"role": "user", "content": "x"}]))
            self.assertEqual(provider_calls, 2)
            self.assertEqual(ledger.snapshot().total_claimed, 2)
            receipts = adapter.public_receipts()
            self.assertEqual([row["provider_budget_unit_call_index"] for row in receipts], [1, 2])
            self.assertEqual([row["provider_budget_total_claimed_after"] for row in receipts], [1, 2])

    def test_resolved_model_drift_is_recorded_then_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter = MindMemOSArkPlanChatAdapter(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                record_dir=Path(tmp),
            )
            adapter.client.respond = lambda *args, **kwargs: {
                "resolved_model": "different-model",
                "text": "x",
                "usage": {},
                "response_id": "id",
                "status": "completed",
            }
            with self.assertRaisesRegex(RuntimeError, "resolved-model-drift"):
                asyncio.run(adapter.chat(task="skill_patch_propose", messages=[{"role": "user", "content": "x"}]))
            self.assertEqual(adapter.public_receipts()[0]["resolved_model"], "different-model")
            self.assertTrue(Path(adapter.public_receipts()[0]["record_path"]).exists())


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: updater_v31_tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_mindmemos_updater_v31.py =====
from __future__ import annotations

import hashlib
import unittest

from research_pipeline.e2_r17_mindmemos_updater import (
    BlindedEvidenceUnit,
    build_blinded_add_record_payload,
    sha_text,
)
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def trajectory(task: str, index: int, score: int) -> TrajectoryRef:
    return TrajectoryRef(
        task_id=task,
        rollout_index=index,
        score=float(score),
        trajectory_path=f"/frozen/{task}/rollout_{index}.json",
        trajectory_sha256=digest(f"trajectory:{task}:{index}:{score}"),
        input_sha256=digest(f"input:{task}"),
        prompt_sha256=digest(f"prompt:{task}"),
        skill_pre_sha256=digest("skill"),
        verifier_sha256=digest("verifier-v1"),
        requested_model="deepseek-v4-pro",
        resolved_model="deepseek-v4-pro-ga-260813",
        provider_call_id_sha256=digest(f"call:{task}:{index}"),
        evidence_tokens=100 + index,
        failure_code=None if score else "controlled_failure",
    )


def pool(task: str, scores: list[int]) -> SearchPool:
    return SearchPool.freeze([trajectory(task, index, score) for index, score in enumerate(scores)])


def unit_for(p: SearchPool, source_index: int, text: str) -> BlindedEvidenceUnit:
    source = p.trajectories[source_index]
    return BlindedEvidenceUnit(
        task_id=p.task_id,
        pool_id=p.pool_id,
        acting_winner_sha256=p.winner.trajectory_sha256,
        source_rollout_index=source.rollout_index,
        source_trajectory_sha256=source.trajectory_sha256,
        source_score=source.score,
        evidence_text=text,
        evidence_sha256=sha_text(text),
        evidence_tokens=321,
    )


class MindMemOSUpdaterV31Test(unittest.TestCase):
    def test_selected_evidence_score_is_separate_from_acting_score(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailed formula evidence")
        payload = build_blinded_add_record_payload(
            unit=failure,
            pool=p,
            project_id="internal-project-id-containing-mrw",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
            projection_label="mixed_rejected_witness",
        )
        self.assertEqual(payload["score"], 0.0)
        self.assertEqual(payload["r17_selected_evidence_score"], 0.0)
        self.assertEqual(payload["r17_acting_score"], 1.0)
        self.assertEqual(payload["messages"], [{"role": "user", "content": failure.evidence_text}])

    def test_projection_and_rollout_metadata_are_not_in_model_visible_messages(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailed formula evidence")
        payload = build_blinded_add_record_payload(
            unit=failure,
            pool=p,
            project_id="internal-project-id-containing-mrw",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
            projection_label="mixed_rejected_witness",
        )
        visible = payload["messages"][0]["content"]
        for forbidden in [
            "mixed_rejected_witness",
            "SOURCE_ROLLOUT_INDEX",
            "ROLE:",
            failure.source_trajectory_sha256,
            p.pool_id,
        ]:
            self.assertNotIn(forbidden, visible)
        self.assertEqual(payload["r17_projection"], "mixed_rejected_witness")
        self.assertEqual(payload["r17_source_rollout_index"], 1)

    def test_winner_and_failure_can_share_acting_provenance_but_not_learning_score(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        winner = unit_for(p, 0, "E2-R17 SELECTED EXPERIENCE\nwinner evidence")
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailure evidence")
        common = dict(
            pool=p,
            project_id="internal",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
        )
        win_payload = build_blinded_add_record_payload(
            unit=winner, projection_label="winner_only", **common
        )
        mrw_payload = build_blinded_add_record_payload(
            unit=failure, projection_label="mixed_rejected_witness", **common
        )
        self.assertEqual(win_payload["r17_acting_winner_sha256"], mrw_payload["r17_acting_winner_sha256"])
        self.assertEqual(win_payload["r17_acting_score"], mrw_payload["r17_acting_score"])
        self.assertEqual(win_payload["score"], 1.0)
        self.assertEqual(mrw_payload["score"], 0.0)

    def test_sha_drift_is_rejected(self) -> None:
        p = pool("mixed", [1, 0])
        broken = BlindedEvidenceUnit(
            task_id=p.task_id,
            pool_id=p.pool_id,
            acting_winner_sha256=p.winner.trajectory_sha256,
            source_rollout_index=1,
            source_trajectory_sha256=p.trajectories[1].trajectory_sha256,
            source_score=0.0,
            evidence_text="failure evidence",
            evidence_sha256=digest("different text"),
            evidence_tokens=10,
        )
        with self.assertRaises(ValueError):
            broken.validate()


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: renderer_tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_evidence_window_v2.py =====
from __future__ import annotations

import importlib.metadata
import unittest

from research_pipeline.e2_r17_evidence_window_v2 import (
    BLOCK_BOUNDARY,
    BLOCK_HEADER,
    FINAL_BLOCK_CAP_TOKENS,
    TOKENIZER_ENCODING,
    TOKENIZER_VERSION,
    ExactMatchedEvidenceBlockRenderer,
    _candidate_block,
    canonical_trajectory_text,
)


class _CharEncoding:
    def encode(self, text: str) -> list[int]:
        return [ord(char) for char in text]

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(token) for token in tokens)

    def decode_bytes(self, tokens: list[int]) -> bytes:
        return self.decode(tokens).encode("utf-8")


class EvidenceWindowV2Test(unittest.TestCase):
    def test_canonical_text_is_arm_blinded(self) -> None:
        payload = {
            "rollout_index": 7,
            "projection": "mixed_rejected_witness",
            "trajectory_path": "/secret/path",
            "provider_receipt": "opaque",
            "score": 0.0,
            "score_message": "formula mismatch",
            "messages": [
                {"role": "system", "content": "common system"},
                {"role": "user", "content": "fix workbook"},
                {"role": "assistant", "content": "attempt"},
            ],
        }
        text = canonical_trajectory_text(payload)
        self.assertIn("formula mismatch", text)
        self.assertIn("fix workbook", text)
        for forbidden in ["mixed_rejected_witness", "rollout_index", "/secret/path", "opaque", "common system"]:
            self.assertNotIn(forbidden, text)

    def test_candidate_always_uses_same_arm_blinded_wrapper(self) -> None:
        encoding = _CharEncoding()
        text, actual = _candidate_block(encoding, encoding.encode("abcdefghijklmnopqrstuvwxyz" * 10), 120)
        self.assertTrue(text.startswith(BLOCK_HEADER))
        self.assertIn(BLOCK_BOUNDARY, text)
        self.assertEqual(actual, len(encoding.encode(text)))
        self.assertNotIn("WIN", text)
        self.assertNotIn("MRW", text)

    def test_actual_tiktoken_pair_is_exact_when_dependency_available(self) -> None:
        try:
            observed = importlib.metadata.version("tiktoken")
        except importlib.metadata.PackageNotFoundError:
            self.skipTest("pinned tiktoken is intentionally absent from shared Python")
        if observed != TOKENIZER_VERSION:
            self.skipTest(f"requires tiktoken {TOKENIZER_VERSION}, observed {observed}")
        renderer = ExactMatchedEvidenceBlockRenderer()
        left = "A short spreadsheet execution. " * 800
        right = "A different failure trajectory with formula mismatch. " * 500
        left_block, right_block, receipt = renderer.render_pair(left, right)
        self.assertEqual(len(renderer.encoding.encode(left_block)), len(renderer.encoding.encode(right_block)))
        self.assertEqual(len(renderer.encoding.encode(left_block)), receipt.matched_final_block_tokens)
        self.assertLessEqual(receipt.matched_final_block_tokens, FINAL_BLOCK_CAP_TOKENS)
        self.assertFalse(receipt.padding_used)
        self.assertFalse(receipt.arm_metadata_visible)

    def test_identical_sources_remain_identical(self) -> None:
        try:
            observed = importlib.metadata.version("tiktoken")
        except importlib.metadata.PackageNotFoundError:
            self.skipTest("pinned tiktoken is intentionally absent from shared Python")
        if observed != TOKENIZER_VERSION:
            self.skipTest(f"requires tiktoken {TOKENIZER_VERSION}, observed {observed}")
        renderer = ExactMatchedEvidenceBlockRenderer()
        source = "same evidence " * 1000
        left, right, receipt = renderer.render_pair(source, source)
        self.assertEqual(left, right)
        self.assertEqual(receipt.left_selected_source_tokens, receipt.right_selected_source_tokens)

    def test_frozen_constants(self) -> None:
        self.assertEqual(TOKENIZER_VERSION, "0.11.0")
        self.assertEqual(TOKENIZER_ENCODING, "cl100k_base")
        self.assertEqual(FINAL_BLOCK_CAP_TOKENS, 3072)


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: provider_budget_tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_provider_budget.py =====
from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM
from research_pipeline.e2_r17_provider_budget import (
    ProviderBudgetBindingError,
    ProviderBudgetExceeded,
    ProviderBudgetLedger,
)


class ProviderBudgetTests(unittest.TestCase):
    def settings(self) -> ArkSettings:
        return ArkSettings(
            api_key="test-key",
            base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
            default_model="ark-code-latest",
            timeout_seconds=30,
            max_retries=0,
        )

    @staticmethod
    def successful_response() -> dict[str, object]:
        return {
            "requested_model": "deepseek-v4-pro",
            "resolved_model": "deepseek-v4-pro-ga-260813",
            "text": "done",
            "function_calls": [],
            "usage": {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3},
            "response_id": "resp-secret",
            "status": "completed",
        }

    def make_ledger(self, root: Path, *, total: int, per_unit: int) -> ProviderBudgetLedger:
        return ProviderBudgetLedger(
            path=root / "provider_budget.sqlite3",
            contract_sha256="a" * 64,
            authorization_sha256="b" * 64,
            total_limit=total,
            per_unit_limit=per_unit,
            allow_create=True,
        )

    def test_eleventh_rollout_call_is_rejected_before_provider_io(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = self.make_ledger(Path(tmp), total=100, per_unit=10)
            llm = ArkPlanReactLLM(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="task-1/rollout_0",
            )
            provider_calls = 0

            def fake_respond(*args, **kwargs):
                nonlocal provider_calls
                provider_calls += 1
                return self.successful_response()

            llm.client.respond = fake_respond
            for _ in range(10):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 10)
            with self.assertRaisesRegex(ProviderBudgetExceeded, "per-unit call budget exhausted before I/O"):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 10)
            snapshot = ledger.snapshot()
            self.assertEqual(snapshot.unit_claimed["task-1/rollout_0"], 10)
            self.assertEqual(snapshot.total_claimed, 10)
            receipts = llm.public_receipts()
            self.assertEqual(receipts[-1]["provider_budget_unit_call_index"], 10)
            self.assertEqual(receipts[-1]["provider_budget_total_claimed_after"], 10)

    def test_7681st_global_call_is_rejected_before_provider_io(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = self.make_ledger(Path(tmp), total=7680, per_unit=10)
            for index in range(7680):
                ledger.claim(f"prefill-{index // 10}")
            self.assertEqual(ledger.snapshot().total_claimed, 7680)

            llm = ArkPlanReactLLM(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="new-task/rollout_0",
            )
            provider_calls = 0

            def fake_respond(*args, **kwargs):
                nonlocal provider_calls
                provider_calls += 1
                return self.successful_response()

            llm.client.respond = fake_respond
            with self.assertRaisesRegex(ProviderBudgetExceeded, "total call budget exhausted before I/O"):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 0)
            self.assertEqual(ledger.snapshot().total_claimed, 7680)

    def test_contract_or_authorization_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "provider_budget.sqlite3"
            ProviderBudgetLedger(
                path=path,
                contract_sha256="a" * 64,
                authorization_sha256="b" * 64,
                total_limit=20,
                per_unit_limit=10,
                allow_create=True,
            )
            with self.assertRaises(ProviderBudgetBindingError):
                ProviderBudgetLedger(
                    path=path,
                    contract_sha256="c" * 64,
                    authorization_sha256="b" * 64,
                    total_limit=20,
                    per_unit_limit=10,
                    allow_create=False,
                )


if __name__ == "__main__":
    unittest.main()


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


===== BOUND ARTIFACT: e1_a_support_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json =====
{
  "artifact_type": "e2-r17-e1-a-pool-support-adjudication",
  "authority": {
    "execute_e1_b": false,
    "paper_promotion": false,
    "prepare_e1_b_contract": true,
    "provider_runtime_pilot": false,
    "submission": false
  },
  "authorization_sha256": "743836932a1aa08391ec7699f925097a17c01e94a0ad7d0470f25a367247d8dd",
  "contract_sha256": "f2919d201f03a0166d6255240378efd14d45bc7f8a3269bff5b78fcccb6d1d21",
  "created_at_utc": "2026-08-28T15:28:27+00:00",
  "family_generalization": {
    "claim_if_failed": "Block family-generalization and prospective family-ranking claims; pooled E1-B may still be contracted only if primary support passes.",
    "controls_primary_e1_b_authorization": false,
    "pass": true,
    "per_family_mixed_recomputed": {
      "aggregation_join": 9,
      "formula_materialization": 15,
      "input_output_contract": 14,
      "multi_step_pipeline": 14,
      "schema_key_alignment": 13,
      "target_sheet_range": 13
    },
    "required_supported_families": 4,
    "supported_families": 6
  },
  "integrity": {
    "actor_rollouts": 768,
    "all_trajectory_shas_revalidated": true,
    "frozen_k8_pools": 96,
    "streams": 12,
    "task_replacement_after_support_observation": false,
    "tasks": 96,
    "updater_calls": 0,
    "waiver_or_rounding": false
  },
  "interpretation": "This adjudication evaluates only pre-treatment mixed-pool support and protocol integrity. It does not evaluate MRW, WIN, RB-AGG, future skill utility, or paper effectiveness.",
  "next_gate": "SEPARATE_IMMUTABLE_E1_B_CONTRACT_WITH_FRESH_UPDATER_IDENTITY_AND_NEGATIVE_CONTROL_FIRST",
  "pool_sha256": {
    "r17-b2-agj-p0": "1e6902bb1a3e097f33dc1b6473719a67bf1299a06993c614d4a27b9198f54c35",
    "r17-b2-agj-p2": "6bb134e333f83aff68308b28bf4802d17babd04d0036d3141c652f8a48c82ecb",
    "r17-b2-agj-p3": "80a8cb85525eca0ad019442979e675259df8435b2fc73e58def52ae899546b2a",
    "r17-b2-agj-p4": "ea6fa00351c74465ff0a85a1ccb1f70bc3a8b42a9bc74b38d6539637fee15092",
    "r17-b2-agj-p5": "e85119a85cbd8addf87540c97ff36c166250f7c641b7c566530a45ccefee6dbf",
    "r17-b2-agj-p6": "16342f5e80b92d96117d735bb98ee1936c0a58f161ab58e4b371c286d6314120",
    "r17-b2-agj-p7": "5be18be58545d9dc3a9a3767770596e6588eb21183059481407746c118b28542",
    "r17-b2-agj-p8": "8a37c0684dde8122bf38c46b4f9ef242de0d0c7c249c19db68399e647538b319",
    "r17-b2-fmv-p0": "23ec56fc83b56f22b1061ce06eed424f81af889563b6d1307418975290d39705",
    "r17-b2-fmv-p1": "036519dae0bc3fe27b28308bafff70cfa6d7fb4c8b19f2186b62dd7f23a80ed9",
    "r17-b2-fmv-p2": "db66d85187df26140620477517869f26e2d2e4f46714c6d68392d10da7373ec1",
    "r17-b2-fmv-p3": "143bf0be3a8b93643626f714cdf07dd84b2fbd8e6bad24c085a1264b8f9a34d6",
    "r17-b2-fmv-p5": "cc550cbc5d5367fbc76446d25dabf722068540d47d7acf17aa8e241550f6ed3e",
    "r17-b2-fmv-p6": "b9fd2b30a712efc1d26863657e9606fab8506f584fda827649c33096d0ea495b",
    "r17-b2-fmv-p7": "2fb9f47bc96b30d293f5a469394fd78ec6dd7ed733834d43c461f11ccb8cdeec",
    "r17-b2-fmv-p8": "cac193e8a5cf02923a36c1193361fe69129228223aaa473b4c99e5b5115bbf2c",
    "r17-b2-ioc-p0": "59d3ce067b69c9361da8c7af22e1defb67e273b3110e23befc27301d323e6ef3",
    "r17-b2-ioc-p1": "112ec9c04ea158a9fece4c1451201c1c6fe7699cd340d198f8d10d31253f7ce5",
    "r17-b2-ioc-p2": "2ef9e6dbf0f5e10f508c36966151382afe002417e267e784dc1edf6e95d9a9d6",
    "r17-b2-ioc-p3": "369e898a1e978794df9d64ea310740a8afadceb15ca8fc7679e55e3bbe6cbaf1",
    "r17-b2-ioc-p5": "787d3c46a713a989fa0eb14c8fda89adf577187b1161abf9aaa457471b31ba39",
    "r17-b2-ioc-p6": "3872f0d870c5499271ea00c0f1cee26e2975dcb7ed7fb4b68c44f8e8ab3a7a6c",
    "r17-b2-ioc-p7": "ce9d08ad623af78288e0290de2f62669c924f1fc455a42233e01a1b704445546",
    "r17-b2-ioc-p8": "a0183b03443671fc7a4a18fcab1c29c5787e5586f37975348091548ed978defc",
    "r17-b2-msp-p1": "fbae337d7c6ea228c2f6d359a8f3d9ed5647030eb85396d360a8ea70d2d8945f",
    "r17-b2-msp-p2": "258e9ef7819912d726c92534d859510f3f525f1936928b1a1db7264f851ab325",
    "r17-b2-msp-p4": "7f8215c093ac7f6ff4723bbbdf2eedc2ff571773bd4165e566bb8fb811986cfb",
    "r17-b2-msp-p5": "43db62f847808a9b7160dcb14682f2d71d3464dbdccbc724fdf2ed8f8c0edb75",
    "r17-b2-msp-p6": "7235b9e297a27eaef0c88619f07f0061fab79f089096539ba048c12e6bd97d92",
    "r17-b2-msp-p7": "dc8501f34a24ff528a8493fac9ae2b0f41a9b59db7317b57016b42f977b12502",
    "r17-b2-msp-p8": "ee4555eac647b133cfcb3cb29e0ce1924d3c8d7ab19069642baf122688049ba4",
    "r17-b2-ska-p0": "ffd0d0d406d9b1872193bb4fa23d970b32eb8d7b3a0c2ae3d9df131736be699f",
    "r17-b2-ska-p1": "d7ce5380af0a22d41ef086f76dffe4506880dd5f635eed36a3643c8183b002cc",
    "r17-b2-ska-p3": "e94180c1358472f37ec9392fabe27933dfa4eef3d4e2a203a8aeee1a69f4cea1",
    "r17-b2-ska-p4": "bf8ae65a983b3b787cc2e652ed39ac90610d50ff31e2b8dbe6ff563e17745ad0",
    "r17-b2-ska-p5": "03cc59702d4252aedd4e8ead9f33cf9f7adf51e7df7a8dd43cfaf5d1251a55b6",
    "r17-b2-ska-p6": "f8727a2cba0b75f2941eb828c212f9ab538c1ae9f55e31c06960d17488aec925",
    "r17-b2-ska-p7": "44654dc3802ead8dcf6d2bfeed817bf662d2b43deb63227c18f9030808189491",
    "r17-b2-ska-p8": "ad64441334ef865061bcb5ab498bc9ef986d719b36bf52999ccf382ab65fa433",
    "r17-b2-tsr-p0": "663a34241988cb1d1c68d9a9baf7c5d576bcef0e85ca08eb7420a1ebb486cfdf",
    "r17-b2-tsr-p1": "a3e1ef9524f3575a66cc40ccf1b6cc088f297e9a18d7505c2a622198e60c671c",
    "r17-b2-tsr-p2": "b36a3799cd74647d7bb8859b024f3fd3bab6063e4e54fda5620279aca13cbefc",
    "r17-b2-tsr-p3": "565ca49b5b75be18b38351bce67975808f5103f7dc5d80449717b524d298b798",
    "r17-b2-tsr-p4": "0080b3e0da0786ef1dfcc51d704c041b287c4917323fd9d570d0f42ab2091811",
    "r17-b2-tsr-p5": "d86c7832efbbfdb11b3e5539740a5e02491f8ad4488462939ba721612d0d653c",
    "r17-b2-tsr-p6": "b636c1d63aee3877e8326a5fe477abdc6381722792f99bd8847a05b681cce0e5",
    "r17-b2-tsr-p8": "5001ce346851199f40616f4f78531e1f6b5b6aff929ba8c7a9cc73b4303b2d97",
    "r17-b3-agj-p0": "f5b8130bdd069944cc496778bcf0069ace535255542fb80d46345f04cc64b5f6",
    "r17-b3-agj-p1": "717a4fe8b845778864ed721f692d2e00c6fe6edd01cadb7fdac1bde8c4ee70f8",
    "r17-b3-agj-p2": "b124d8c84183c6928785e3c31151c892815a4610d4ada8bc9236f5e9cf1e191f",
    "r17-b3-agj-p3": "bb979598543063189ccabecc4709ee53e6fd65c2626f32e738269c5f904575ce",
    "r17-b3-agj-p5": "f30a24f0c0306ed74a29ada88ba0d35e02a5d6842e9bed3f9811fc2b825160f9",
    "r17-b3-agj-p6": "d23aa4d3ee3940ab6988f752432c3b19f804a1c698f0a9d8d86eacdde6c29a1b",
    "r17-b3-agj-p7": "dd643b2837c809e89266354217c98deb3f35177e0613d3d02541c0768244574d",
    "r17-b3-agj-p8": "3c10937593f08179e8e0f6e149dd31526d2a51df44ddcaf4c7d9d35266d88235",
    "r17-b3-fmv-p0": "2e5cb6d399c0e1dc8fb0267803a9f9729ba205349cb6ef0917677abaad61a2ef",
    "r17-b3-fmv-p1": "c1411e2dda57b231c328afb1bdd6ac9d15ed7301759456ad8c29e2cffe315198",
    "r17-b3-fmv-p2": "300a94e47f366314be37667610aa2e24369fcd11050bec2e8347967da9033cc2",
    "r17-b3-fmv-p3": "ba66f94bc70a7e29b5dde847e1fd3660fe9d76fb1446accf22264ac0ead77a70",
    "r17-b3-fmv-p4": "c977806d6aa3fe35a86c59114b6d9316476017a64400867b99888b0edf33a797",
    "r17-b3-fmv-p5": "c6aa1978c86b02147f9da88c1a2d331fa3e141696ce16720e7eb50b46c907fb4",
    "r17-b3-fmv-p7": "5fb29370edbe86d825bbc64fa10b808c065d311bb28def9360fda3bfc276e655",
    "r17-b3-fmv-p8": "9db88a383f686ac799ad18c6bd8c48f7522ccb65a9ffcc84a446e227a3a8dfa7",
    "r17-b3-ioc-p0": "5407d2318a6d053bde52cb6c4de6f7079a8f1fe8c6acb42ef0020b82b66e2bac",
    "r17-b3-ioc-p1": "da3925602042081560c415664ce41309d36a93ba498575c8b8dec0d6f0dd2589",
    "r17-b3-ioc-p3": "5a60c8bd0b20a20dac0be2478b17d477a85cf7da18532a9953cb056fed1ccea2",
    "r17-b3-ioc-p4": "53cc55ec3b5df3e475a813a05d11652fdcf6d697c09f007b32e99d6677f439f3",
    "r17-b3-ioc-p5": "0858dee963758fb641f31ed788c55ec1682385139f1b28a96ce901a709705ba7",
    "r17-b3-ioc-p6": "2d409ff2826b54c8f2201ca60fd7e445f7ea3bf729897df3da81e576dc1c8b41",
    "r17-b3-ioc-p7": "eb08e0a291340d2655f68b80994b911d9abb3651d87a2faf5f273cf6564103e6",
    "r17-b3-ioc-p8": "4e4802cc4410bad1ea60b0901632ead3fbff1adb753b34fc58fe54375715389d",
    "r17-b3-msp-p0": "ff061ca5f682d0bb220e5338136407d32a3ab837a65d21e8bb83f964443a4e6d",
    "r17-b3-msp-p1": "473c55a55e0b6c85596176e07f608bd6a3533215c42f188177a448f5e355a040",
    "r17-b3-msp-p2": "1390be4ff1d570a17b2aeebd6c0b8e481cf6486bec98da124468a4178b935fc6",
    "r17-b3-msp-p3": "3a1e1405dad812b1d1605f3f07da920dfca26d7432e79298a4c2ad44429a34a8",
    "r17-b3-msp-p4": "e52d3b41e6cd3dda34b40f603b594ac3f2dbcc08adeb3584f67ec610fb05cbf9",
    "r17-b3-msp-p5": "ecf628a6ac526eda6b7c978b4e7b51ab1a95403238487c4fcda8b20afeae8418",
    "r17-b3-msp-p6": "9157867f046ad31eaadc919914222a7b3e27bcb266475116a5571c0c9ece5c29",
    "r17-b3-msp-p7": "5613132d9b0792353995c79b2d9339de6250da8287944ea1ce434dda7de477a9",
    "r17-b3-msp-p8": "4c84e7a2412927fadb452c805846c9750668c506cf34ccb534a2b5476d4fa571",
    "r17-b3-ska-p0": "3815b59fa03f76701e9141e2cb220443031956cb92f6561f1c94ec8f6a06d662",
    "r17-b3-ska-p1": "47b29f7c9e7028031073706297548456bc7dbe6d379bf7a9f163daf76d7e5f00",
    "r17-b3-ska-p2": "cc77ee33688c739cf9e0522115761c0bb6a843f5560a9c574563ddbcf40d663c",
    "r17-b3-ska-p3": "9a8e802336f46e692b679d4cb8eb60e46ac679df915ec67a9ebc8ab0fc78d544",
    "r17-b3-ska-p5": "f96291b324f9cd6419a6747ca5a7c14514ff226150de82b1132939ef2f677b6f",
    "r17-b3-ska-p6": "0a23e630167af078242ed0cd2e4b233d32928f02879696e52ae43736f2f6470e",
    "r17-b3-ska-p7": "c07b632ac118fb0f62210475947bd6e98651b2d1c696c79a50f0424d471304e6",
    "r17-b3-ska-p8": "4e6e4dede165a6f304438f72d084953483c37169a7b6054359b7ab4afc7e44ee",
    "r17-b3-tsr-p0": "2629ce7090a3f5b6142bd996e50366ff1bf8cac709d482a636844f6c5b28511c",
    "r17-b3-tsr-p1": "e82d66f5f0b906925a5eafe69fba670d0c524abc1b0db81dc5c7ac3d0d80b5fa",
    "r17-b3-tsr-p3": "0e1c97e4f4554b27eb2463e0d0b937198e67b267a8b38f967d598875e90da2b0",
    "r17-b3-tsr-p4": "2ca13720131c23499d9058371510668376e4a7346d51ad811609132950718ec3",
    "r17-b3-tsr-p5": "4d8da1f5c4c69da2eb8ad1535eef854d2e583c14bb7d46af06954321294ba6ff",
    "r17-b3-tsr-p6": "935f4e3f6793ad81d69e9f39c0b0a5279a3ad995306f994a6e36e995b13b5610",
    "r17-b3-tsr-p7": "53d9abbbce1a5fb4bf48906a273785e9f8f280b637f9ad8f6d577f610e9db6b6",
    "r17-b3-tsr-p8": "ca70f41358fd2a586f0980a4a2bf81951833956a497a446126f5d6df081af501"
  },
  "primary_support": {
    "exposed_streams": 12,
    "mixed_per_exposed_stream": 2,
    "mixed_pools": 78,
    "pass": true,
    "per_stream_mixed_recomputed": {
      "e1-agj-00": 4,
      "e1-agj-01": 5,
      "e1-fmv-00": 8,
      "e1-fmv-01": 7,
      "e1-ioc-00": 8,
      "e1-ioc-01": 6,
      "e1-msp-00": 8,
      "e1-msp-01": 6,
      "e1-ska-00": 7,
      "e1-ska-01": 6,
      "e1-tsr-00": 7,
      "e1-tsr-01": 6
    },
    "required_exposed_streams": 8,
    "required_mixed_pools": 24
  },
  "schema_version": "1.0",
  "status": "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT",
  "summary_path": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828/summary/e1_a_pool_freeze_summary.json",
  "summary_sha256": "4df8cd4ee88bb8ed7bdccb2bbdf763f13fa090168e09dfedf688d30befe38356"
}


===== BOUND ARTIFACT: v31_mechanical_contract | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v3-1-mechanical-pilot-contract-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-v3-1-mechanical-pilot-contract",
  "date": "2026-08-28",
  "status": "AUTHORIZED_ZERO_PROVIDER_MECHANICAL_PILOT_ONLY",
  "run_root": "/data/wyt/e2-r17-search-projection/runtime-pilots/v3-1-mechanical-20260828",
  "runner": {
    "path": "scripts/run_e2_r17_v3_1_mechanical_pilot.py",
    "sha256": "3a486d529a9f2e0208d072a15de11c56bfd75ff92949af1b565e1adb012bc2f5"
  },
  "repair": {
    "path": "generated/e2-r17-v3-1-causal-purity-repair-20260828.json",
    "sha256": "2b4589d704037c9dd781c4091d03b12dddf727b6d7a7aad765dc7536863a6880"
  },
  "upstream_prompt_dataflow_audit": {
    "path": "generated/e2-r17-v3-1-upstream-prompt-dataflow-audit-20260828.json",
    "sha256": "ecd160e6c87b259c56e5a667fe94a9cc7310c37c5fca92ce514436c131d30d7c"
  },
  "review_adjudication": {
    "path": "generated/e2-r17-v3-1-review-adjudication-20260828.json",
    "sha256": "858e200f2fa9a3b9e4b591b4b895e590e10537d0b96c85346f8c5e98b89e4585",
    "required_status": "PASS_TO_FRESH_ZERO_PROVIDER_MECHANICAL_PILOT_ONLY"
  },
  "historical_inputs": {
    "e0_root": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828",
    "e0_summary": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/e0_pilot_summary.json",
    "e0_summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
    "expected_k8_pools": 12
  },
  "renderer": {
    "path": "research_pipeline/e2_r17_evidence_window_v2.py",
    "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0",
    "tokenizer_encoding": "cl100k_base",
    "final_block_cap_tokens": 3072,
    "padding": false,
    "exact_final_retokenized_parity_required": true
  },
  "updater_wrapper": {
    "path": "research_pipeline/e2_r17_mindmemos_updater.py",
    "sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d",
    "test_path": "research_pipeline/test_e2_r17_mindmemos_updater_v31.py",
    "test_sha256": "874fc99106e2f85f67180f4962f50b50ad2d921c8ba5ad8fad54fb12f62ded9f",
    "transcript_max_chars": 100000,
    "score_semantics": "selected_evidence_trajectory"
  },
  "mindmemos": {
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "bound_files": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py": "771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e",
      "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py": "48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c"
    }
  },
  "checks": [
    "revalidate every historical pool and trajectory SHA",
    "exact actual final WIN/MRW token parity on all 12 pools",
    "nonmixed WIN/MRW byte identity",
    "MRW differs from WIN only on mixed pools",
    "model-visible messages contain no projection/role/rollout/path/provider/provenance treatment labels",
    "selected evidence score equals selected trajectory verifier score",
    "served acting winner SHA and acting score remain identical across cloned WIN/MRW payload provenance",
    "no downstream first-party transcript truncation under frozen 100000-char limit",
    "pinned MindMemOS commit and bound source SHAs revalidate",
    "completed-unit receipts are content-addressed and revalidated on resume",
    "temporary corruption detector catches receipt SHA drift",
    "provider calls remain zero",
    "new actor rollouts remain zero",
    "scientific effectiveness is not evaluated"
  ],
  "checkpoint": {
    "unit": "historical K8 pool",
    "persist_immediately": true,
    "completed_manifest": "checkpoints/completed_units.jsonl",
    "resume": "revalidate completed receipt SHA then execute missing units only",
    "reuse_v3_failed_root": false
  },
  "forbidden": [
    "provider calls",
    "new actor rollouts",
    "held-out future-skill evaluation",
    "method effectiveness comparison",
    "scientific GO/HOLD/STOP from method outcome",
    "retrying the V3 failed contract/root",
    "E1-A generation",
    "E1-B updater execution",
    "paper promotion"
  ],
  "authority": {
    "independent_review": true,
    "execute_mechanical_pilot": true,
    "provider_runtime_pilot": false,
    "e1_a": false,
    "e1_b": false,
    "scientific_effectiveness": false,
    "paper_promotion": false,
    "submission": false
  }
}


BOUND DOSSIER END
