You are an independent adversarial pre-execution reviewer for E2-R17 E1-B WIN-A/WIN-B negative-control FULL. You are blind to the other reviewer. This is a nuisance-control scientific tranche, not the MRW mechanism experiment. Even PASS cannot authorize MRW, paper claims, frontend promotion, or submission.

Reviewer endpoint: kimi-k3
Exact draft SHA-256: 8010b307d084d2996522df30ae12ff71cdaf46b5228659a44c770c3f09db5781

Context: E1-A has frozen 96 exact K=8 pools and passed strong treatment-support (78/96 mixed, 12/12 exposed streams). A hosted updater runtime Pilot and a receipt-bound update->noninitial-skill->actor transition Pilot both passed. Before MRW can be interpreted causally, we must empirically show that two independent hosted executions of the exact same WIN learning treatment produce practically equivalent future frozen-skill performance.

The proposed full nuisance-control experiment has 12 independent paired stream units. Each stream contains the exact same eight E1-A K=8 pools and frozen initial skill. WIN-A and WIN-B receive the same pre-rendered V3.1 winner evidence bytes and selected-evidence scores but use independent provider calls and cloned persistent states. Each learned state is evaluated on the same 18 never-fed E1 common heldout probes at K=1. The 18 probes are repeated measurements; the independent inferential units are 12 stream pairs.

Audit the actual draft, runner and predeclared analysis. Answer:

1. UNITS/SPLIT: Does the runner bind exactly the 12 frozen e1_update_streams, eight exact content-addressed E1-A pools per stream, and exactly the 18 e1_common_heldout_probe tasks? Is there any task replacement/drop/subset path based on observed A/B outcomes?

2. IDENTICAL TREATMENT: Are WIN-A and WIN-B generated from the same initial SKILL.md, same exact pools, same winner StreamProjection and same deterministic V3.1 matched-window winner BlindedEvidenceUnits? They must differ only in hosted provider stochasticity and resulting learned state. Note the renderer computes WIN/MRW matched windows even though MRW is not executed; judge whether this compromises A/B identity or is a legitimate prospective freeze for the later MRW comparison.

3. ARM ORDER: Update and heldout A/B order are deterministic SHA-based functions of stream/task/arm, frozen before outcomes. Is this a reasonable way to avoid systematic A-first/B-second temporal bias without outcome-dependent randomization? Flag any hidden order-selection path.

4. RUNTIME/HANDOFF: Are updater and actor runtimes separately qualified, model identity freshly bound, update receipt/skill content-addressed, and noninitial skill accepted only when path/SHA/contract/auth receipt checks pass? Does the full runner preserve the V3.1 arm-blinded selected-evidence score semantics?

5. BUDGET/RESUME: Each learned state has its own contract/auth-bound SQLite ledger capped at 190 calls: exact 10 updater calls plus 18 evaluation units each capped at 10. Across exactly 24 states the structural hard maximum is 4560; the ~2621 planning estimate must not relax it. Are completed updates/probes immediately checkpointed and SHA-revalidated on resume? Does any partial ambiguous update/evaluation fail closed and leave the global lock rather than auto-rerun? Could separate per-state ledgers permit an accidental extra state outside the frozen 24-state structure?

6. HELDOUT EVALUATION: Does each state evaluate all the same 18 probes at K=1 with the same actor/verifier/model settings? Is treating the 18 probes as repeated observations and the 12 stream pairs as independent units correct? Does the execution code avoid scientific inference until a separate analysis step?

7. STATISTICS: The predeclared nuisance endpoint is N_s=J_s(WIN-B)-J_s(WIN-A), epsilon=1/18, alpha=.05. Primary equivalence is paired TOST, implemented equivalently as the 90% paired-mean t CI lying strictly inside [-epsilon,+epsilon], with fixed t_0.95,11=1.7958848187. A deterministic 100000-resample paired-stream bootstrap (seed 1717) gives a 90% robustness CI but does not control the gate. Is this statistically correct? With n=12 and a narrow margin it is intentionally strict; state whether failure should be HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY rather than a mechanism negative. Check that nonsignificance is never treated as equivalence.

8. OUTCOME SELECTION / FAILURE POLICY: The nuisance gate was frozen before these outcomes. If equivalence fails, MRW is held because the causal contrast is not interpretable; this is not evidence against R17. Is that legitimate, or does it create an outcome-selective escape hatch? Conversely, if equivalence passes, does it merely allow a separately contracted MRW experiment rather than prove the mechanism?

9. MRW SEPARATION: Confirm zero MRW provider execution, zero RB-AGG, and zero method-effect inference in this full negative-control tranche. Any MRW execution path is P0.

10. DECISION: PASS only if there is no P0/P1 blocker. Keep `mrw_execution_recommendation=HOLD` and paper_claim_authority=false even on PASS.

Return exactly one JSON object and no markdown using this schema:
{
  "draft_contract_sha256_acknowledged": "",
  "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_NEGATIVE_CONTROL_FULL|REVISE_NEGATIVE_CONTROL_BEFORE_EXECUTION|STOP_NEGATIVE_CONTROL",
  "scientific_units_and_split_assessment": "",
  "identical_treatment_assessment": "",
  "arm_order_and_temporal_bias_assessment": "",
  "runtime_and_receipt_handoff_assessment": "",
  "provider_budget_and_resume_assessment": "",
  "heldout_evaluation_assessment": "",
  "statistics_and_equivalence_assessment": "",
  "outcome_selection_and_failure_policy_assessment": "",
  "mrw_separation_assessment": "",
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
  "negative_control_execution_recommendation": "ALLOW_SEPARATE_FROZEN_NEGATIVE_CONTROL_AUTHORIZATION|HOLD|STOP",
  "mrw_execution_recommendation": "HOLD|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}
Set `draft_contract_sha256_acknowledged` exactly to the SHA above. For PASS use verdict `PASS_TO_SEPARATELY_AUTHORIZED_NEGATIVE_CONTROL_FULL` and recommendation `ALLOW_SEPARATE_FROZEN_NEGATIVE_CONTROL_AUTHORIZATION`. Keep MRW HOLD and paper authority false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: negative_control_draft | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-b-negative-control-full-draft-contract-20260829.json =====
{
  "actor": {
    "concurrency_per_probe": 1,
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
  "arm_order": {
    "evaluation_pair_order": "SHA256(E2-R17-E1B-NC-EVAL-PAIR-ORDER-v1|stream_id|task_id|arm)",
    "purpose": "balance systematic temporal order without outcome-dependent randomization",
    "update_order": "SHA256(E2-R17-E1B-NC-UPDATE-ORDER-v1|stream_id|arm)"
  },
  "artifact_type": "e2-r17-e1-b-negative-control-full-contract",
  "authority": {
    "dual_preexecution_review": true,
    "execute_mrw": false,
    "execute_negative_control_full": false,
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
    "analysis": {
      "path": "scripts/analyze_e2_r17_e1_b_negative_control.py",
      "sha256": "5b040c81632ab930ddbd7d44c80b38db21c8ddf01b70dcf87c350bf05376bf23"
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
    "runner": {
      "path": "scripts/run_e2_r17_e1_b_negative_control_full.py",
      "sha256": "bd43723450bfee0f9aea1e3c5f8e9bef91fa41109d1ab2969c9084269f80b978"
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
    "claim_before_provider_io": true,
    "claims_never_released": true,
    "hard_max_provider_calls_structural": 4560,
    "max_provider_calls_per_state": 190,
    "max_provider_calls_per_unit": 10,
    "planning_basis": "E1-A observed mean 5.5104 actor calls/rollout plus exact 10 updater calls/state; planning only, never a ceiling relaxation",
    "planning_expected_actor_tokens": 7155016,
    "planning_expected_provider_calls": 2621,
    "planning_expected_updater_tokens": 724864,
    "state_structure": "10 updater + 18 heldout rollouts x <=10 actor calls",
    "states": 24
  },
  "checkpoint": {
    "exclusive_lock": ".exclusive.lock",
    "partial_ambiguous_unit_auto_rerun": false,
    "persist_each_heldout_probe_immediately": true,
    "preserve_lock_on_failure": true,
    "resume_completed_units_only_after_sha_revalidation": true,
    "state_eval_manifest": "states/<stream>/<arm>/checkpoints/completed_eval_tasks.jsonl",
    "state_update_checkpoint": "states/<stream>/<arm>/checkpoints/update_completed.json",
    "stream_manifest": "checkpoints/completed_streams.jsonl"
  },
  "date": "2026-08-29",
  "e1_a_pool_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
  "e1_a_support": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
    "required_status": "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT",
    "sha256": "b2c611285c20377d77af7ea62448c6fee0d5973cd657687f6dde7f7fce6be6d7"
  },
  "env_file": ".env",
  "forbidden": [
    "MRW provider execution",
    "ReasoningBank/RB-AGG execution",
    "task/model/threshold replacement based on negative-control result",
    "treating nonsignificance as equivalence",
    "paper/frontend/submission promotion",
    "automatic rerun after ambiguous provider calls"
  ],
  "heldout": {
    "evaluation_k": 1,
    "never_fed_to_updater": true,
    "source_split": "e1_common_heldout_probe",
    "task_ids": [
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
    ]
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
    "path": "generated/e2-r17-e1-b-negative-control-model-identity-adjudication-20260829.json",
    "qualification_path": "generated/e2-r17-e1-b-negative-control-model-identity-qualification-20260829.json",
    "qualification_sha256": "1b61624ef347532fd5a083cac26ed6f8febc7ffe9e22a68b32e95362e5d7bc21",
    "required_status": "PASS_CURRENT_REVIEW_TRANCHE",
    "sha256": "6ebc6ee7edb67b78a7aae910b87a158d81232477f676b42e15ee9c6449432746"
  },
  "parents": {
    "e1_a_support": {
      "path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
      "sha256": "b2c611285c20377d77af7ea62448c6fee0d5973cd657687f6dde7f7fce6be6d7"
    },
    "failure_registry": {
      "path": "generated/e2-r17-failure-differential-registry-v3-20260829.json",
      "sha256": "5f44cc4a43e0aa94a84f42b1fc8c752b2a9d396dfde54144afff2e1aacfd59a6"
    },
    "provider_runtime": {
      "path": "generated/e2-r17-v31-provider-runtime-pilot-v2-adjudication-20260829.json",
      "sha256": "8be8a4596ffef8e3702f8e422ed4dd2c55b7fc1f97573b125f30096d64f60424"
    },
    "transition_runtime": {
      "path": "generated/e2-r17-e1-b-transition-runtime-pilot-adjudication-20260829.json",
      "sha256": "75e19d67b1cdb0e65a28a1f2943e223629c27cfcb2b0b562bbca8d32ee988185"
    }
  },
  "purpose": "Measure residual hosted updater+evaluator stochasticity under byte-identical WIN treatment before any MRW causal comparison. Exactly 12 paired stream units, two independent WIN clones per stream, same 18 common heldout probes at K=1. MRW is not executed.",
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
  "run_root": "/data/wyt/e2-r17-search-projection/runs/e1-b-negative-control-v1-20260829",
  "schema_version": "1.0",
  "scientific_units": {
    "arms": [
      "win_a",
      "win_b"
    ],
    "heldout_probes_are_repeated_measurements": true,
    "heldout_probes_per_state": 18,
    "heldout_rollout_units": 432,
    "independent_unit": "stream-level learned-state pair",
    "learned_states": 24,
    "paired_streams": 12,
    "update_tasks_per_stream": 8
  },
  "statistics": {
    "alpha": 0.05,
    "bootstrap_robustness": {
      "controls_primary_gate": false,
      "interval": "90%",
      "paired_stream_resampling": true,
      "reps": 100000,
      "seed": 1717
    },
    "difference": "N_s=J_s(WIN-B)-J_s(WIN-A)",
    "endpoint": "J_s(arm)=mean binary success over the same 18 heldout K=1 probes",
    "equivalence_margin": 0.05555555555555555,
    "if_equivalence_fail": "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY; MRW remains unauthorized",
    "if_equivalence_pass": "PASS_NEGATIVE_CONTROL_EQUIVALENCE_READY_FOR_SEPARATE_MRW_CONTRACT",
    "n_pairs": 12,
    "nonsignificance_is_not_equivalence": true,
    "primary_gate": "paired TOST equivalence, implemented equivalently as the 90% paired-mean t interval lying strictly within [-1/18,+1/18]",
    "t_critical_0_95_df11": 1.7958848187036691
  },
  "status": "DRAFT_PENDING_DUAL_PREEXECUTION_REVIEW",
  "streams": [
    "e1-agj-00",
    "e1-agj-01",
    "e1-fmv-00",
    "e1-fmv-01",
    "e1-ioc-00",
    "e1-ioc-01",
    "e1-msp-00",
    "e1-msp-01",
    "e1-ska-00",
    "e1-ska-01",
    "e1-tsr-00",
    "e1-tsr-01"
  ],
  "suite": {
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "treatment": {
    "mrw_executed": false,
    "pre_provider_evidence_identity_required": true,
    "same_exact_search_pools": true,
    "same_heldout_probes": true,
    "same_initial_skill": true,
    "same_served_winner": true,
    "same_updater_config": true,
    "win_a": "V3.1 arm-blinded matched-window winner evidence for all eight exact pools",
    "win_b": "byte-identical V3.1 arm-blinded matched-window winner evidence for all eight exact pools, independent hosted provider calls and cloned persistent state"
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


===== BOUND ARTIFACT: negative_control_runner | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_e1_b_negative_control_full.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
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
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import run_projection_update
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, project_stream
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import bind_mindmemos, evidence_units, validate_updater_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import sha_file, load_json, atomic_json, require

ARMS = ("win_a", "win_b")
UPDATE_ORDER_SALT = "E2-R17-E1B-NC-UPDATE-ORDER-v1"
EVAL_ORDER_SALT = "E2-R17-E1B-NC-EVAL-PAIR-ORDER-v1"


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[str(row[key])] = row
    return out


def canonical_sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def ordered_arms(stream_id: str, salt: str, task_id: str = "") -> list[str]:
    return sorted(ARMS, key=lambda arm: hashlib.sha256(f"{salt}|{stream_id}|{task_id}|{arm}".encode()).hexdigest())


def acquire_lock(path: Path, contract_sha: str, auth_sha: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"negative-control lock exists: {path}; inspect checkpoints before resume") from exc
    os.write(fd, (json.dumps({"pid": os.getpid(), "contract_sha256": contract_sha, "authorization_sha256": auth_sha}, sort_keys=True) + "\n").encode())
    os.fsync(fd)
    return fd


def validate_contract_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == "FROZEN_E1_B_NEGATIVE_CONTROL_FULL", "negative-control contract not frozen")
    require(auth.get("status") == "AUTHORIZED_E1", "negative-control authorization invalid")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization/contract mismatch")
    authority = auth.get("authority") or {}
    require(authority.get("scientific_experiment") is True, "negative-control scientific authority absent")
    require(authority.get("e1_b") is True and authority.get("e1_b_negative_control") is True, "negative-control authority bit absent")
    require(authority.get("mrw_causal_comparison") is False, "negative-control must not authorize MRW")
    require(authority.get("paper_promotion") is False, "negative-control cannot promote paper")
    scope = auth.get("execution_scope") or {}
    require(scope.get("allowed_modes") == ["e1"], "mode scope drift")
    require(scope.get("allowed_task_ids") == contract["heldout"]["task_ids"], "heldout scope drift")
    require(int(scope.get("exact_k")) == 1 and scope.get("allow_noninitial_skill") is True, "K/noninitial scope drift")
    bscope = scope.get("provider_budget") or {}
    require(bscope.get("required") is True, "provider budget must be required")
    require(int(bscope.get("total_limit")) == int(contract["budget"]["max_provider_calls_per_state"]), "state total budget drift")
    require(int(bscope.get("per_unit_limit")) == int(contract["budget"]["max_provider_calls_per_unit"]), "state unit budget drift")
    return contract, auth


def load_stream_pools(contract: dict[str, Any], stream_id: str, split: dict[str, Any], support: dict[str, Any]) -> list[Any]:
    pools = []
    for task_id in map(str, split["e1_update_streams"][stream_id]):
        path = Path(contract["e1_a_pool_root"]) / "cases" / task_id / "pool_k8.json"
        require(path.is_file() and sha_file(path) == support["pool_sha256"][task_id], f"E1-A pool SHA drift: {task_id}")
        pool = load_frozen_pool(path)
        require(pool.task_id == task_id and pool.k == 8, f"invalid frozen pool: {task_id}")
        pools.append(pool)
    require(len(pools) == 8, f"stream {stream_id} must have eight pools")
    return pools


def verify_update(path: Path, contract_sha: str, auth_sha: str) -> dict[str, Any]:
    row = load_json(path)
    receipt = Path(row["update_receipt_path"]); skill = Path(row["skill_post_path"])
    require(receipt.is_file() and skill.is_file(), "completed update artifacts missing")
    require(sha_file(receipt) == row["update_receipt_sha256"] and sha_file(skill) == row["skill_post_sha256"], "completed update SHA drift")
    payload = load_json(receipt)
    require(payload.get("contract_sha256") == contract_sha and payload.get("authorization_sha256") == auth_sha, "update receipt binding drift")
    require(payload.get("causal_purity_mode") == "arm_blinded_selected_evidence" and payload.get("arm_metadata_visible_in_transcript") is False, "update causal-purity drift")
    return row


async def ensure_update(*, contract: dict[str, Any], contract_sha: str, auth_sha: str, stream_id: str, arm: str, pools: list[Any], win_units: list[Any], initial_skill: str, initial_sha: str, mind_head: str, requested: str, resolved: str, settings: ArkSettings, state_root: Path, ledger: ProviderBudgetLedger) -> dict[str, Any]:
    checkpoint = state_root / "checkpoints/update_completed.json"
    if checkpoint.exists():
        return verify_update(checkpoint, contract_sha, auth_sha)
    update_dir = state_root / "update"
    if update_dir.exists() and any(update_dir.rglob("*")):
        raise RuntimeError(f"partial ambiguous update exists: {stream_id}/{arm}; no auto-rerun")
    stream = project_stream(stream_id=stream_id, initial_skill_sha256=initial_sha, pools=pools, projection=ProjectionName.WINNER_ONLY)
    adapter = MindMemOSArkPlanChatAdapter(settings=settings, requested_model=requested, required_resolved_model=resolved, max_parse_attempts=int(contract["updater"]["max_parse_attempts"]), record_dir=update_dir / "provider_calls", provider_budget_ledger=ledger, provider_budget_unit_id=f"{stream_id}/{arm}/update")
    result = await run_projection_update(stream=stream, pools=pools, initial_skill_md=initial_skill, run_dir=update_dir, llm_adapter=adapter, mindmemos_commit=mind_head, contract_sha256=contract_sha, authorization_sha256=auth_sha, transcript_max_chars=int(contract["updater"]["transcript_max_chars"]), blinded_evidence_units=win_units)
    receipts = adapter.public_receipts()
    require(result.provider_calls == 10 and len(receipts) == 10, "WIN update must use exact nominal 10 calls")
    require(not any(r.get("parse_error") for r in receipts), "WIN update parse error")
    row = {"status":"COMPLETED","stream_id":stream_id,"arm":arm,"update_receipt_path":result.update_receipt_path,"update_receipt_sha256":result.update_receipt_sha256,"skill_post_path":result.skill_post_path,"skill_post_sha256":result.skill_post_sha256,"provider_calls":result.provider_calls,"provider_tokens":result.provider_total_tokens}
    atomic_json(checkpoint, row)
    return verify_update(checkpoint, contract_sha, auth_sha)

def verify_eval(row: dict[str, Any], state_root: Path, skill_sha: str, receipt_sha: str) -> None:
    summary_path = Path(row["summary_path"])
    require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], "eval summary SHA drift")
    summary = load_json(summary_path)
    require(summary.get("status") == "COMPLETED" and summary.get("k") == 1, "eval summary status/K drift")
    require(summary.get("skill_pre_sha256") == skill_sha and summary.get("updater_receipt_sha256") == receipt_sha, "eval learned-skill/receipt binding drift")
    require([str(x["task_id"]) for x in summary.get("tasks") or []] == [row["task_id"]], "eval task drift")
    ref = state_root / "evaluation" / row["task_id"] / "cases" / row["task_id"] / "rollout_0" / "r17_trajectory_ref.json"
    require(ref.is_file() and sha_file(ref) == row["trajectory_ref_sha256"], "eval trajectory-ref SHA drift")
    ref_payload = load_json(ref); trajectory = Path(ref_payload["trajectory_path"])
    require(trajectory.is_file() and sha_file(trajectory) == ref_payload["trajectory_sha256"], "eval trajectory SHA drift")


def ensure_eval(*, contract: dict[str, Any], auth_path: Path, identity_path: Path, actor_python: Path, actor_env: dict[str, str], stream_id: str, arm: str, task_id: str, state_root: Path, update: dict[str, Any], ledger_path: Path) -> dict[str, Any]:
    manifest = state_root / "checkpoints/completed_eval_tasks.jsonl"
    existing = rows_by(manifest, "task_id")
    if task_id in existing:
        verify_eval(existing[task_id], state_root, update["skill_post_sha256"], update["update_receipt_sha256"])
        return existing[task_id]
    eval_root = state_root / "evaluation" / task_id
    summary_path = eval_root / "evaluation_summary.json"
    if eval_root.exists() and any(eval_root.rglob("*")):
        raise RuntimeError(f"partial ambiguous evaluation exists: {stream_id}/{arm}/{task_id}; no auto-rerun")
    command = [str(actor_python), str(ROOT / "scripts/run_e2_r17_actor_pool.py"), "--env-file", contract["env_file"], "--suite-root", contract["suite"]["root"], "--mindmemos-root", contract["mindmemos"]["root"], "--run-root", str(eval_root), "--identity", str(identity_path), "--authorization", str(auth_path), "--skill-source", str(Path(update["skill_post_path"]).parent), "--updater-receipt", update["update_receipt_path"], "--mode", "e1", "--model", contract["actor"]["requested_model"], "--task-id", task_id, "--k", "1", "--prefix-ks", "1", "--max-turns", str(contract["actor"]["max_turns"]), "--max-output-tokens", str(contract["actor"]["max_output_tokens"]), "--concurrency", "1", "--provider-budget-ledger", str(ledger_path), "--provider-total-call-limit", str(contract["budget"]["max_provider_calls_per_state"]), "--provider-per-unit-call-limit", str(contract["budget"]["max_provider_calls_per_unit"]), "--output", str(summary_path)]
    result = subprocess.run(command, cwd=ROOT, env=actor_env, capture_output=True, text=True)
    if result.returncode != 0:
        atomic_json(state_root / "checkpoints" / f"eval_failure_{task_id}.json", {"status":"TECHNICAL_FAILURE","stream_id":stream_id,"arm":arm,"task_id":task_id,"returncode":result.returncode,"stdout_tail":result.stdout[-3000:],"stderr_tail":result.stderr[-3000:],"provider_relaunch_authorized":False})
        raise RuntimeError(f"heldout evaluation technical failure: {stream_id}/{arm}/{task_id}")
    require(summary_path.is_file(), "actor returned without eval summary")
    ref = eval_root / "cases" / task_id / "rollout_0" / "r17_trajectory_ref.json"
    require(ref.is_file(), "actor returned without trajectory ref")
    row = {"task_id":task_id,"summary_path":str(summary_path),"summary_sha256":sha_file(summary_path),"trajectory_ref_path":str(ref),"trajectory_ref_sha256":sha_file(ref),"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
    verify_eval(row, state_root, update["skill_post_sha256"], update["update_receipt_sha256"])
    append_jsonl(manifest, row)
    return row


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    contract, auth = validate_contract_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract); auth_sha = sha_file(args.authorization)
    updater_python, _ = validate_updater_runtime({"runtime":contract["updater_runtime"],"mindmemos":contract["mindmemos"]})
    require(Path(sys.executable) == updater_python, "negative-control runner must use dedicated updater runtime")
    actor_python, actor_env = validate_actor_runtime({"runtime":contract["actor_runtime"]}); actor_env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]; require(path.is_file() and sha_file(path) == item["sha256"], f"bound code drift: {label}")
    suite_root = Path(contract["suite"]["root"]); split_path = suite_root / "r17_split_manifest.json"
    require(sha_file(suite_root / "suite_manifest.json") == contract["suite"]["suite_manifest_sha256"] and sha_file(split_path) == contract["suite"]["split_manifest_sha256"], "suite/split drift")
    split = load_json(split_path)
    require(list(split["e1_update_streams"].keys()) == contract["streams"], "stream manifest drift")
    require([str(x) for x in split["e1_common_heldout_probe"]] == contract["heldout"]["task_ids"], "heldout list drift")
    support_path = ROOT / contract["e1_a_support"]["path"]; require(support_path.is_file() and sha_file(support_path) == contract["e1_a_support"]["sha256"], "E1-A support artifact drift")
    support = load_json(support_path); require(support.get("status") == "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT", "E1-A support no longer passing")
    mind_root = Path(contract["mindmemos"]["root"]); mind_head = subprocess.check_output(["git","-C",str(mind_root),"rev-parse","HEAD"],text=True).strip()
    require(mind_head == contract["mindmemos"]["commit"] and not subprocess.check_output(["git","-C",str(mind_root),"status","--short"],text=True).strip(), "MindMemOS drift/dirty")
    bind_mindmemos(mind_root)
    identity_path = ROOT / contract["model_identity"]["path"]; require(identity_path.is_file() and sha_file(identity_path) == contract["model_identity"]["sha256"], "identity artifact drift")
    identity = load_json(identity_path); require(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "model identity not qualified")
    model_row = identity["requested_and_resolved"][contract["updater"]["requested_model"]]; requested=str(model_row["requested"]); resolved=str(model_row["resolved"])
    require(resolved == contract["updater"]["resolved_model"] == contract["actor"]["resolved_model"], "resolved-model drift")
    load_env_file(Path(contract["env_file"])); raw=ArkSettings.from_env(required=True); require(raw.base_url.rstrip("/") == PLAN_BASE_URL, "non-Ark-Plan route")
    settings=ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=300.0,max_retries=0)
    initial_path=Path(contract["initial_skill"]["path"]); require(initial_path.is_file() and sha_file(initial_path)==contract["initial_skill"]["sha256"], "initial skill drift")
    initial_skill=initial_path.read_text(encoding="utf-8"); initial_sha=sha_file(initial_path)
    run_root=Path(contract["run_root"]); lock_path=run_root/".exclusive.lock"; lock_fd=acquire_lock(lock_path,contract_sha,auth_sha); success=False
    stream_manifest=run_root/"checkpoints/completed_streams.jsonl"; completed_streams=rows_by(stream_manifest,"stream_id")

    try:
        for row in completed_streams.values():
            path=Path(row["summary_path"]); require(path.is_file() and sha_file(path)==row["summary_sha256"], f"completed stream summary drift: {row['stream_id']}")
        for stream_id in contract["streams"]:
            if stream_id in completed_streams:
                continue
            pools=load_stream_pools(contract,stream_id,split,support)
            win_units,_,evidence_receipts=evidence_units(pools,final_block_cap_tokens=int(contract["renderer"]["final_block_cap_tokens"]),transcript_max_chars=int(contract["updater"]["transcript_max_chars"]))
            stream_root=run_root/"states"/stream_id; evidence_path=stream_root/"evidence_windows.json"; bundle_sha=canonical_sha([u.__dict__ for u in win_units])
            if evidence_path.exists():
                require(load_json(evidence_path).get("evidence_bundle_sha256")==bundle_sha, "frozen evidence-window drift")
            else:
                atomic_json(evidence_path,{"stream_id":stream_id,"evidence_bundle_sha256":bundle_sha,"receipts":evidence_receipts,"mrw_provider_execution_authorized":False})
            updates: dict[str,dict[str,Any]]={}
            for arm in ordered_arms(stream_id,UPDATE_ORDER_SALT):
                state_root=stream_root/arm; ledger_path=state_root/"checkpoints/provider_budget.sqlite3"
                ledger=ProviderBudgetLedger(path=ledger_path,contract_sha256=contract_sha,authorization_sha256=auth_sha,total_limit=int(contract["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),allow_create=not ledger_path.exists())
                updates[arm]=await ensure_update(contract=contract,contract_sha=contract_sha,auth_sha=auth_sha,stream_id=stream_id,arm=arm,pools=pools,win_units=win_units,initial_skill=initial_skill,initial_sha=initial_sha,mind_head=mind_head,requested=requested,resolved=resolved,settings=settings,state_root=state_root,ledger=ledger)
            for task_id in contract["heldout"]["task_ids"]:
                for arm in ordered_arms(stream_id,EVAL_ORDER_SALT,task_id):
                    state_root=stream_root/arm
                    ensure_eval(contract=contract,auth_path=args.authorization,identity_path=identity_path,actor_python=actor_python,actor_env=actor_env,stream_id=stream_id,arm=arm,task_id=task_id,state_root=state_root,update=updates[arm],ledger_path=state_root/"checkpoints/provider_budget.sqlite3")
            states=[]
            for arm in ARMS:
                state_root=stream_root/arm; eval_manifest=state_root/"checkpoints/completed_eval_tasks.jsonl"; eval_rows=rows_by(eval_manifest,"task_id")
                require(set(eval_rows)==set(contract["heldout"]["task_ids"]), f"heldout completion set invalid: {stream_id}/{arm}")
                for row in eval_rows.values(): verify_eval(row,state_root,updates[arm]["skill_post_sha256"],updates[arm]["update_receipt_sha256"])
                ledger=ProviderBudgetLedger(path=state_root/"checkpoints/provider_budget.sqlite3",contract_sha256=contract_sha,authorization_sha256=auth_sha,total_limit=int(contract["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),allow_create=False)
                states.append({"arm":arm,"update_receipt_sha256":updates[arm]["update_receipt_sha256"],"skill_post_sha256":updates[arm]["skill_post_sha256"],"completed_heldout_tasks":len(eval_rows),"eval_manifest_path":str(eval_manifest),"eval_manifest_sha256":sha_file(eval_manifest),"provider_budget":ledger.snapshot().to_dict()})
            stream_summary={"schema_version":"1.0","artifact_type":"e2-r17-e1-b-negative-control-stream","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED","stream_id":stream_id,"pool_ids":[p.pool_id for p in pools],"evidence_windows_sha256":sha_file(evidence_path),"update_order":ordered_arms(stream_id,UPDATE_ORDER_SALT),"heldout_task_ids":contract["heldout"]["task_ids"],"states":states,"mrw_executed":False,"paper_promotion_authority":False}
            stream_summary_path=run_root/"summary/streams"/f"{stream_id}.json"; atomic_json(stream_summary_path,stream_summary)
            manifest_row={"stream_id":stream_id,"summary_path":str(stream_summary_path),"summary_sha256":sha_file(stream_summary_path),"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}; append_jsonl(stream_manifest,manifest_row); completed_streams[stream_id]=manifest_row
        require(set(completed_streams)==set(contract["streams"]), "negative-control did not complete all streams")
        final={"schema_version":"1.0","artifact_type":"e2-r17-e1-b-negative-control-full-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED_PENDING_SEPARATE_NEGATIVE_CONTROL_ADJUDICATION","contract_sha256":contract_sha,"authorization_sha256":auth_sha,"streams":len(contract["streams"]),"arms":list(ARMS),"learned_states":len(contract["streams"])*2,"heldout_tasks_per_state":len(contract["heldout"]["task_ids"]),"heldout_rollout_units":len(contract["streams"])*2*len(contract["heldout"]["task_ids"]),"mrw_executed":False,"negative_control_inference_performed":False,"paper_promotion_authority":False,"completed_stream_manifest":str(stream_manifest),"completed_stream_manifest_sha256":sha_file(stream_manifest)}
        atomic_json(run_root/"summary/e1_b_negative_control_full_summary.json",final); success=True; return final
    finally:
        os.close(lock_fd)
        if success: lock_path.unlink(missing_ok=True)


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--contract",type=Path,required=True); parser.add_argument("--authorization",type=Path,required=True); args=parser.parse_args()
    payload=asyncio.run(main_async(args)); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if payload["status"]=="COMPLETED_PENDING_SEPARATE_NEGATIVE_CONTROL_ADJUDICATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: negative_control_analysis | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/analyze_e2_r17_e1_b_negative_control.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

T_CRITICAL_095_DF11 = 1.7958848187036691
BOOTSTRAP_SEED = 1717
BOOTSTRAP_REPS = 100000
ALPHA = 0.05
EPSILON = 1.0 / 18.0
ARMS = ("win_a", "win_b")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line); rows[str(row[key])] = row
    return rows


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position)); hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    frac = position - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def bootstrap_ci(differences: list[float]) -> tuple[float, float]:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(differences)
    means = [statistics.fmean(differences[rng.randrange(n)] for _ in range(n)) for _ in range(BOOTSTRAP_REPS)]
    return quantile(means, 0.05), quantile(means, 0.95)


def paired_t_ci_90(differences: list[float]) -> tuple[float, float, float, float]:
    n = len(differences); mean = statistics.fmean(differences)
    sd = statistics.stdev(differences) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else float("nan")
    half = T_CRITICAL_095_DF11 * se
    return mean, sd, mean - half, mean + half


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_json(args.contract); auth = load_json(args.authorization); summary = load_json(args.run_summary)
    contract_sha = sha_file(args.contract); auth_sha = sha_file(args.authorization)
    require(contract.get("status") == "FROZEN_E1_B_NEGATIVE_CONTROL_FULL", "negative-control contract not frozen")
    require(auth.get("contract_sha256") == contract_sha, "authorization contract binding drift")
    require(summary.get("status") == "COMPLETED_PENDING_SEPARATE_NEGATIVE_CONTROL_ADJUDICATION", "negative-control run incomplete")
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == auth_sha, "negative-control summary binding drift")
    require(summary.get("mrw_executed") is False and summary.get("negative_control_inference_performed") is False, "run summary violates negative-control-only boundary")

    run_root = Path(contract["run_root"])
    heldout = contract["heldout"]["task_ids"]
    stream_rows = []
    differences = []
    for stream_id in contract["streams"]:
        arm_scores: dict[str, list[float]] = {}
        for arm in ARMS:
            state_root = run_root / "states" / stream_id / arm
            manifest = rows_by(state_root / "checkpoints/completed_eval_tasks.jsonl", "task_id")
            require(set(manifest) == set(heldout), f"heldout completion mismatch: {stream_id}/{arm}")
            scores = []
            for task_id in heldout:
                row = manifest[task_id]
                require(sha_file(Path(row["summary_path"])) == row["summary_sha256"], "eval summary SHA drift")
                ref_path = Path(row["trajectory_ref_path"])
                require(sha_file(ref_path) == row["trajectory_ref_sha256"], "trajectory-ref SHA drift")
                ref = load_json(ref_path)
                trajectory = Path(ref["trajectory_path"])
                require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], "trajectory SHA drift")
                score = float(ref["score"])
                require(score in (0.0, 1.0), "negative-control endpoint score must be binary")
                scores.append(score)
            arm_scores[arm] = scores
        ja = statistics.fmean(arm_scores["win_a"]); jb = statistics.fmean(arm_scores["win_b"]); diff = jb - ja
        differences.append(diff)
        stream_rows.append({"stream_id":stream_id,"j_win_a":ja,"j_win_b":jb,"difference_win_b_minus_win_a":diff,"win_a_successes":int(sum(arm_scores["win_a"])),"win_b_successes":int(sum(arm_scores["win_b"]))})

    require(len(differences) == 12, "negative-control requires exactly 12 paired stream units")
    mean, sd, ci_low, ci_high = paired_t_ci_90(differences)
    boot_low, boot_high = bootstrap_ci(differences)
    equivalent = ci_low > -EPSILON and ci_high < EPSILON
    status = "PASS_NEGATIVE_CONTROL_EQUIVALENCE_READY_FOR_MRW_CONTRACT" if equivalent else "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY"
    payload = {
        "schema_version":"1.0","artifact_type":"e2-r17-e1-b-negative-control-adjudication","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,
        "contract_sha256":contract_sha,"authorization_sha256":auth_sha,"run_summary_path":str(args.run_summary),"run_summary_sha256":sha_file(args.run_summary),
        "scientific_unit":"12 paired stream-level learned states; 18 probes are repeated measurements, not 216 independent units per arm",
        "epsilon":EPSILON,"alpha":ALPHA,"n_pairs":12,"difference_definition":"J_s(WIN-B)-J_s(WIN-A)","mean_difference":mean,"sd_difference":sd,
        "paired_t_90_ci":[ci_low,ci_high],"t_critical_0_95_df11":T_CRITICAL_095_DF11,"paired_tost_equivalence_pass":equivalent,
        "bootstrap":{"seed":BOOTSTRAP_SEED,"reps":BOOTSTRAP_REPS,"interval":"90% paired bootstrap robustness","ci":[boot_low,boot_high],"controls_primary_gate":False},
        "per_stream":stream_rows,
        "interpretation":("Identical-treatment hosted updater+evaluation variability is practically equivalent within one held-out probe of success rate; MRW may now be separately contracted." if equivalent else "Identical-treatment variability is not demonstrated equivalent within the preregistered margin. MRW remains unauthorized; this is a nuisance-control HOLD, not evidence for or against the R17 mechanism."),
        "authority":{"prepare_mrw_contract":equivalent,"execute_mrw":False,"paper_promotion":False,"submission":False},
        "central_mechanism_adjudicated":False
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if equivalent else 3


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


===== BOUND ARTIFACT: e1_a_support | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json =====
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


===== BOUND ARTIFACT: transition_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-b-transition-runtime-pilot-adjudication-20260829.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-e1-b-transition-runtime-pilot-adjudication",
  "date": "2026-08-29",
  "status": "PASS_UPDATE_TO_NONINITIAL_SKILL_EVALUATION_HANDOFF_ONLY",
  "contract": {
    "path": "generated/e2-r17-e1-b-transition-runtime-pilot-contract-20260829.json",
    "sha256": "f39d53fc9e83ad04e9cb2d73a01224ec8859bc8f3ce4d69ffc57050d8ece2ecd"
  },
  "authorization": {
    "path": "generated/e2-r17-e1-b-transition-runtime-pilot-authorization-20260829.json",
    "sha256": "f6d5cccdb2e8d3a03fe498acfbd3bef692af40cfb270661e0f348c753dffa376"
  },
  "run": {
    "root": "/data/wyt/e2-r17-search-projection/runtime-pilots/e1-b-transition-v1-20260829",
    "summary": "/data/wyt/e2-r17-search-projection/runtime-pilots/e1-b-transition-v1-20260829/summary/transition_runtime_pilot_summary.json",
    "summary_sha256": "9f073da468c0cdfe036686ade09503197cba05b886d4c885acb5286ed375e961",
    "evaluation_summary_sha256": "8e263a2573bd718e45c341c9cd6b11f30464dd4f1d1990e477735730962ba339"
  },
  "handoff_integrity": {
    "updater_causal_purity_mode": "arm_blinded_selected_evidence",
    "arm_metadata_visible_in_updater_transcript": false,
    "updater_score_semantics": "selected_evidence_trajectory",
    "updater_summaries": 8,
    "updater_consumed_records": 8,
    "actor_loaded_skill_sha_matches_update_receipt": true,
    "actor_loaded_updater_receipt_sha_matches_transition_summary": true,
    "actor_k": 1,
    "actor_task_id": "r17-b0-agj-p4",
    "actor_requested_model": "deepseek-v4-pro",
    "actor_resolved_model": "deepseek-v4-pro-ga-260813",
    "actor_provider_retry_limit": 0,
    "actor_thinking": "disabled",
    "verifier_pipeline_completed": true
  },
  "budget": {
    "total_claimed": 16,
    "total_limit": 20,
    "updater_claimed": 10,
    "actor_rollout_claimed": 6,
    "per_unit_limit": 10,
    "pre_io_claiming": true,
    "claims_never_released": true
  },
  "scientific_boundary": {
    "e1_common_heldout_accessed": false,
    "heldout_evaluation_calls": 0,
    "mrw_executed": false,
    "negative_control_inference_performed": false,
    "scientific_effectiveness_evaluated": false,
    "development_task_outcome_used_for_promotion": false,
    "paper_claim_authority": false
  },
  "interpretation": "The receipt/content-addressed handoff from the dedicated updater runtime to the independently frozen actor/evaluator runtime is operational. A learned noninitial SKILL.md can be loaded only with its matching updater receipt and then completed by the fixed K=1 SpreadsheetBench actor/verifier path. The development-task score is not interpreted. This PASS is runtime/provenance evidence only and provides no evidence that WIN-A/WIN-B are behaviorally equivalent or that MRW improves future skill.",
  "next_gate": "FREEZE_AND_DUAL_REVIEW_E1_B_WIN_A_WIN_B_NEGATIVE_CONTROL_FULL_CONTRACT",
  "authority": {
    "prepare_e1_b_negative_control_full_contract": true,
    "execute_e1_b_negative_control": false,
    "mrw_causal_comparison": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: failure_registry | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-failure-differential-registry-v3-20260829.json =====
{
  "artifact_type": "e2-r17-failure-differential-registry",
  "current_scientific_state": {
    "central_mechanism": "OPEN_NOT_YET_ADJUDICATED",
    "e0_censoring_existence": "SUPPORTED_ON_CONTROLLED_PILOT",
    "e1_a_treatment_support": "PASS_STRONG_SUPPORT_78_OF_96_MIXED_12_OF_12_STREAMS_6_OF_6_FAMILIES",
    "e1_b_mrw_causal_effect": "UNKNOWN",
    "e1_b_negative_control": "FULL_RUNNER_AND_PREDECLARED_ANALYSIS_IMPLEMENTED_PENDING_CONTRACT_REVIEW",
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
    },
    {
      "classification": [
        "IMPLEMENTATION"
      ],
      "contamination": "NONE",
      "failure_id": "R17-F011-RUNNER-WRITE-TRANSPORT-LIMIT",
      "preserved_artifacts": [
        {
          "path": "generated/e2-r17-e1-b-negative-control-runner-write-failure-20260829.json",
          "sha256": "5fa4cf51566e6eee58b870618efba60e77a918802efb79335b7724e97802b2f9"
        }
      ],
      "provider_calls": 0,
      "repair_or_stop": "Write the same runner in bounded chunks; keep all protocol checks.",
      "rerun_policy": "SOURCE_ARTIFACT_WRITE_PERMITTED_IN_BOUNDED_CHUNKS",
      "reusable_rule": "Tool payload limits are implementation failures; split artifact writes rather than deleting scientific checks.",
      "root_cause": "Tool/transport command-size limit, not experiment/runtime failure.",
      "scientific_belief_update": "NONE",
      "scientific_data_observed_for_effectiveness": false,
      "scientific_endpoint_reached": false,
      "stage": "E1-B negative-control runner implementation",
      "symptom": "One oversized remote atomic source-write failed with spawn ENAMETOOLONG before creating the runner file.",
      "terminal_status": "ARTIFACT_WRITE_NOT_CREATED"
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
    },
    {
      "evidence": {
        "path": "generated/e2-r17-e1-b-transition-runtime-pilot-adjudication-20260829.json",
        "sha256": "75e19d67b1cdb0e65a28a1f2943e223629c27cfcb2b0b562bbca8d32ee988185"
      },
      "heldout_evaluation_calls": 0,
      "lesson": "Receipt/content-addressed learned skill can cross from dedicated updater runtime into frozen actor/evaluator runtime and complete K=1 verifier execution; this removes the final runtime handoff blocker before full WIN-A/WIN-B negative control.",
      "provider_calls": 16,
      "scientific_effectiveness_evaluated": false,
      "stage": "E1-B update-to-noninitial-skill transition runtime Pilot",
      "status": "PASS_UPDATE_TO_NONINITIAL_SKILL_EVALUATION_HANDOFF_ONLY",
      "success_id": "R17-S002-E1B-TRANSITION-HANDOFF"
    }
  ],
  "schema_version": "1.2",
  "status": "ACTIVE_CANONICAL_FAILURE_LEDGER_FOR_R17_WORKTREE",
  "supersedes": {
    "path": "generated/e2-r17-failure-differential-registry-v2-20260829.json",
    "sha256": "7850763eeeb3c08db0e1989d456ea21c03384fa46d559f78f802e9323b69f4c5"
  },
  "taxonomy": {
    "IMPLEMENTATION": "Local code, launcher, parser, review harness, checkpoint, or accounting defect before a valid scientific endpoint.",
    "MEASUREMENT_ANALYSIS": "Estimator, renderer, token/accounting, or adjudicator failure that invalidates the intended measurement without establishing a scientific negative.",
    "PROTOCOL_CAUSAL_PURITY": "A design or dataflow defect that changes or leaks treatment, invalidating causal interpretation even if code runs.",
    "RUNTIME_INFRA": "Environment/dependency/role-runtime or provider-route failure that prevents the frozen scientific procedure from reaching its endpoint.",
    "SCIENTIFIC_MECHANISM": "A protocol-valid, fully qualified primary experiment reaches its endpoint and rejects/equates/harms the central mechanism under the frozen decision rule. This class triggers scientific STOP unless a predeclared scope limitation applies."
  }
}


===== BOUND ARTIFACT: fresh_identity_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-b-negative-control-model-identity-adjudication-20260829.json =====
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
      "path": "generated/e2-r17-e1-b-negative-control-model-identity-qualification-20260829.json",
      "sha256": "1b61624ef347532fd5a083cac26ed6f8febc7ffe9e22a68b32e95362e5d7bc21",
      "status": "PASS"
    }
  ],
  "created_at_utc": "2026-08-29T11:18:49+00:00",
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "requested_and_resolved": {
    "deepseek-v4-pro": {
      "requested": "deepseek-v4-pro",
      "resolved": "deepseek-v4-pro-ga-260813",
      "source_artifact": "generated/e2-r17-e1-b-negative-control-model-identity-qualification-20260829.json",
      "source_artifact_sha256": "1b61624ef347532fd5a083cac26ed6f8febc7ffe9e22a68b32e95362e5d7bc21",
      "thinking_requested": "disabled"
    },
    "kimi-k3": {
      "requested": "kimi-k3",
      "resolved": "kimi-k3",
      "source_artifact": "generated/e2-r17-e1-b-negative-control-model-identity-qualification-20260829.json",
      "source_artifact_sha256": "1b61624ef347532fd5a083cac26ed6f8febc7ffe9e22a68b32e95362e5d7bc21",
      "thinking_requested": "disabled"
    }
  },
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS_CURRENT_REVIEW_TRANCHE"
}


===== BOUND ARTIFACT: fresh_identity_qualification | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-b-negative-control-model-identity-qualification-20260829.json =====
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
  "created_at_utc": "2026-08-29T11:18:49+00:00",
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
      "response_id_sha256": "f62c2fb8f361e237dfe86665f69a3f65367ee035244e80b96b1b0deb3d07e2b4",
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
      "response_id_sha256": "3dab9c27510e568556430ea633921090759162a205637cdf0bb26068fc1a1dec",
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
