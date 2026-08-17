from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation

CANDIDATE_ID = "AUTO-1"
SEARCH_PRIMITIVE = "CONTRADICTION"
TRANSACTION_ID = "2975a3f837b4577abf958e5e021c4f85f7f097c36f4d7563f29353529f84fdf5"
GENERATOR_RUN_ID = "20260817T161813Z"
GENERATOR_RAW_SHA256 = "b921767ef4674142af7d6b3124786e2f71dd9cabcee0eac31bd8eb088f578deb"
SOURCE_A = "arXiv:2607.05297"
SOURCE_B = "arXiv:2607.01874"
SOURCE_A_FULLTEXT_SHA256 = "84e40d16a13395870ca336bd8999e727d20aacc134f1fb821292a7452bc6fb8a"
SOURCE_B_FULLTEXT_SHA256 = "98e09b6cf2748867e3843fe1ace5525225b0d87a2821316614b6942be12fd728"
PRIMARY_STATE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
GENERATOR_STATE = PROJECT_ROOT / "generated" / "paper-first-problem-generator-state.json"
QUEUE_STATE = PROJECT_ROOT / "generated" / "paper-first-problem-gate-queue.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "static-procedural-prior-cross-regime-contradiction-principle-readjudication-20260817.json"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object: {path}")
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_readjudication() -> dict[str, Any]:
    primary = _load(PRIMARY_STATE)
    generator = _load(GENERATOR_STATE)
    queue = _load(QUEUE_STATE)
    if not (primary.get("discovery_transaction_id") == generator.get("discovery_transaction_id") == queue.get("discovery_transaction_id") == TRANSACTION_ID):
        raise ValueError("static-procedural-prior transaction drift")
    if generator.get("run_id") != GENERATOR_RUN_ID:
        raise ValueError("static-procedural-prior generator run drift")
    raw = (generator.get("raw_artifacts") or {}).get("generator") or {}
    if raw.get("sha256") != GENERATOR_RAW_SHA256:
        raise ValueError("static-procedural-prior generator raw drift")
    audited = [row for row in queue.get("audited") or [] if isinstance(row, dict) and row.get("candidate_id") == CANDIDATE_ID]
    if len(audited) != 1:
        raise ValueError("static-procedural-prior candidate receipt missing")
    candidate = audited[0].get("candidate") or {}
    blockers = sorted(str(value) for value in ((audited[0].get("audit") or {}).get("blockers") or []))
    expected_blockers = sorted(["semantic-reduction-review-missing", "unresolved-exact-reduction-test:1", "unresolved-exact-reduction-test:2"])
    if blockers != expected_blockers:
        raise ValueError(f"static-procedural-prior queue blocker drift: {blockers}")
    if candidate.get("discovery_lane") != SEARCH_PRIMITIVE:
        raise ValueError("static-procedural-prior lane drift")
    evidence = candidate.get("empirical_evidence") or {}
    if str((evidence.get("source_a") or {}).get("ref") or "") != SOURCE_A or str((evidence.get("source_b") or {}).get("ref") or "") != SOURCE_B:
        raise ValueError("static-procedural-prior source pair drift")
    records = {str(row.get("ref") or ""): row for row in primary.get("records") or [] if isinstance(row, dict)}
    if (records.get(SOURCE_A) or {}).get("fulltext_sha256") != SOURCE_A_FULLTEXT_SHA256:
        raise ValueError("MetaSkill-Evolve fulltext hash drift")
    if (records.get(SOURCE_B) or {}).get("fulltext_sha256") != SOURCE_B_FULLTEXT_SHA256:
        raise ValueError("SkillCoach fulltext hash drift")

    counter = {
        "type": "NECESSARY_ASSUMPTION_REFUTED",
        "necessary_assumption_id": "shared-static-procedural-artifact-treatment",
        "necessity_established": True,
        "assumption_refuted": True,
        "statement": (
            "The proposed CONTRADICTION requires the two reported signs to estimate the same treatment under a shared operationalization, but the primary papers intervene on different causal surfaces. MetaSkill-Evolve's Static Skill loads a fixed skill into a frozen Gemma-4 31B agent and compares held-out task accuracy against the same no-skill executor; on ALFWorld that inference-time skill changes 92.31% to 90.38% (-1.93 points). SkillCoach's R0 result is not an inference-time static-context effect: R0 is a task-level process rubric used to score and filter verifier-passing trajectories, and the reported 8->16 and 14->28 gains are measured after supervised fine-tuning on the filtered demonstrations. That intervention changes the training set and then model parameters. Opposite signs across an inference-time frozen-agent skill treatment and a rubric-filtered SFT treatment do not constitute incompatible outcomes under one treatment contract, so the claimed cross-regime sign contradiction is not identified before either headroom or applicability theory is tested."
        ),
        "opposite_prediction": (
            "If procedural interventions are typed by causal surface, inference-time static context, data-selection/filtering, parameter training, and artifact evolution may have different signed effects without contradiction. A genuine cross-regime sign reversal must first hold the treatment definition fixed: the same frozen executor must receive the same kind of static procedural artifact with the same no-artifact comparator and endpoint, and only the task regime may vary. Under the current two papers, treatment-surface differences alone permit the observed -1.93 and positive SFT gains."
        ),
        "opposite_principle": (
            "Treatment-effect signs are only comparable after intervention semantics are aligned. Cross-paper sign differences cannot define a regime-conditioned certificate when one effect is an inference-time context intervention on a frozen policy and the other is a trajectory-selection intervention followed by parameter updating. Treatment typing precedes effect-heterogeneity or sign-certificate claims."
        ),
        "opposite_search_seed": (
            "Search only for first-party matched cells where an identically defined static procedural artifact is applied to the same frozen executor with an identical no-artifact control, endpoint, and budget across at least two task regimes. Match base/headroom within sampling error, then ask whether the within-regime treatment deltas have reproducibly opposite signs and whether pre-deployment artifact/regime features predict that interaction beyond ordinary conditional treatment-effect or domain-shift baselines. Do not reopen by comparing inference-time skills with rubric-filtered SFT, prompt tuning, parameter training, or another update surface."
        ),
        "scope": (
            "Canonical transaction 2975a3f8..., AUTO-1 CONTRADICTION combining MetaSkill-Evolve arXiv:2607.05297 Static Skill on ALFWorld with SkillCoach arXiv:2607.01874 R0-filtered SFT, restricted to the claim that these two reported signs instantiate one shared static-procedural-prior treatment and motivate a pre-deployment regime-conditioned sign certificate."
        ),
        "same_information_or_scope_matched": True,
        "evidence_refs": [
            SOURCE_A,
            f"primary-fulltext:{SOURCE_A}#sha256={SOURCE_A_FULLTEXT_SHA256}",
            SOURCE_B,
            f"primary-fulltext:{SOURCE_B}#sha256={SOURCE_B_FULLTEXT_SHA256}",
            f"canonical-generator-raw:sha256={GENERATOR_RAW_SHA256}",
            f"canonical-discovery-transaction:{TRANSACTION_ID}",
        ],
        "alternative_explanations_ruled_out": [
            "The -1.93 ALFWorld sign was fabricated: false; MetaSkill-Evolve explicitly reports 92.31% no-skill versus 90.38% static skill and describes the static skill as slightly regressing in the near-ceiling regime.",
            "SkillCoach's +8/+14 numbers are the direct effect of placing R0 into the frozen executor context: false; the paper states that R0 scores trajectories, filters verifier-passing demonstrations, and the reported gains are downstream results of rubric-filtered supervised fine-tuning.",
            "Both papers merely use different names for the same procedural artifact intervention: false; one changes inference-time context while keeping model parameters frozen, whereas the other changes the training examples used for SFT and therefore the learned parameter state.",
            "A matched-base/headroom test can rescue the current contradiction without treatment alignment: false; matching baseline accuracy does not make two different interventions estimate the same causal effect."
        ],
        "reopen_condition": (
            "Reopen only with primary or first-party evidence containing at least two regimes that share an identical static-procedural-artifact intervention on the same frozen executor, identical no-artifact comparator, endpoint, rollout/compute budget, and treatment timing; base/headroom must be matched within sampling error and the within-regime treatment deltas must have reproducibly opposite signs. Any residual sign predictor must then beat a same-information conditional-treatment/domain-shift baseline using only pre-deployment observables."
        ),
    }
    audit = audit_dead_end_counter_explanation(counter)
    if audit.get("passed") is not True:
        raise ValueError(f"static-procedural-prior counter audit failed: {audit.get('blockers')}")

    return {
        "schema_version": "1.0",
        "candidate_id": "AUTO-1-STATIC-PROCEDURAL-PRIOR-CROSS-REGIME",
        "title": "Cross-regime static-procedural sign contradiction collapses because the two papers intervene on different causal surfaces",
        "adjudication_date": "2026-08-17",
        "search_primitive": SEARCH_PRIMITIVE,
        "principle_dead_end_certified": True,
        "experiment_run_for_this_readjudication": False,
        "source_proposal_had_scientific_authority": False,
        "source_discovery_transaction_id": TRANSACTION_ID,
        "source_generator_run_id": GENERATOR_RUN_ID,
        "source_generator_raw_sha256": GENERATOR_RAW_SHA256,
        "broader_procedural_artifact_sign_heterogeneity_falsified": False,
        "dead_end_scope": counter["scope"],
        "principle_diagnosis": {
            "status": "PRINCIPLE_DEAD_END_CERTIFIED",
            "counter_explanation_type": "NECESSARY_ASSUMPTION_REFUTED",
            "counter_explanation": counter,
            "audit": audit,
        },
        "scientific_interpretation": {
            "do_not_say": [
                "static skills cannot hurt",
                "rubric-filtered SFT cannot help",
                "procedural artifact effects never change sign across tasks",
                "headroom and task-artifact applicability are irrelevant"
            ],
            "safe_claim": (
                "The two source results are individually real, but they are effects of different interventions. MetaSkill-Evolve reports a small negative inference-time Static Skill effect on near-ceiling ALFWorld, while SkillCoach reports positive downstream gains after R0-based trajectory filtering and SFT. These values cannot by themselves define a contradiction or a common sign certificate for one frozen procedural-context treatment."
            ),
            "new_search_basin": "matched-treatment-static-procedural-sign-interaction-after-treatment-typing",
        },
        "authority": {
            "experiment_alone_authorizes_dead_end": False,
            "counter_explanation_authorizes_scoped_dead_end": True,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": "principle-adjudication-only",
        },
        "source_artifact_sha256": {
            "primary_state": _sha(PRIMARY_STATE),
            "generator_state": _sha(GENERATOR_STATE),
            "queue_state": _sha(QUEUE_STATE),
        },
    }


def write_readjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_readjudication()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(write_readjudication(), ensure_ascii=False, indent=2))
