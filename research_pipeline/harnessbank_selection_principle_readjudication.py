from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation

SOURCE_REF = "arXiv:2607.13683"
CANDIDATE_ID = "PA-03-HARNESS-SELECTION-INVERSION"
PRIMARY_STATE = PROJECT_ROOT / "generated" / "paper-first-primary-evidence-state.json"
SUPPORT_AUDIT = PROJECT_ROOT / "generated" / "harnessbank-support-audit-20260817.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "harnessbank-selection-principle-readjudication-20260817.json"
EXPECTED_FULLTEXT_SHA256 = "74082edc56e911da43e9b70b8eeaf4d6552b8fea7e15b7a0ab00d4c20aff2997"
GDPVAL_BOUNDARY_EVIDENCE_SHA256 = "faf94010c18b42621b5d62229c148b4c9c07cb0de9a8c6c0218cedb954397558"


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected object: {path}")
    return data


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_readjudication() -> dict[str, Any]:
    primary = _load(PRIMARY_STATE)
    support = _load(SUPPORT_AUDIT)
    record = next((row for row in primary.get("records") or [] if row.get("ref") == SOURCE_REF), None)
    if not isinstance(record, dict):
        raise ValueError("HarnessBank primary-evidence record missing")
    if record.get("fulltext_sha256") != EXPECTED_FULLTEXT_SHA256:
        raise ValueError("HarnessBank fulltext hash drift")
    if support.get("candidate_id") != CANDIDATE_ID:
        raise ValueError("HarnessBank support-audit candidate mismatch")
    if support.get("status") != "HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT":
        raise ValueError("HarnessBank support-audit state drift")
    # Full-text identity is bound by the canonical primary-evidence registry above.
    # The release-support audit has a different responsibility: it certifies only
    # whether the required first-party per-gene replay unit is currently released.
    # Do not couple principle validity to an optional duplicate fulltext_sha256 field
    # in the release-audit schema.
    if support.get("released_required_unit_present") is not False:
        raise ValueError("HarnessBank support-audit release-unit state drift")

    counter = {
        "type": "SAME_INFORMATION_REDUCTION",
        "statement": (
            "The current PA-03 evidence is already explained by ordinary noisy/adaptive model selection rather than an "
            "identified harness-specific selection-inversion mechanism. HarnessBank reports one GDPval case where a "
            "train-lower variant scores +11.5pp on test while the train-selected winner scores +9.2pp, and separately "
            "constructs post-convergence neutral-candidate rounds where weak single-run or K=3-mean crediting produces "
            "62-76% phantom progress. The latter disappears under the paper's paired-2sigma verification rule. Finite-sample "
            "selection-criterion variance, winner's curse, and adaptive selection are sufficient to predict both rank reversal "
            "and false progress without introducing a new harness-specific causal primitive."
        ),
        "opposite_prediction": (
            "If many candidates are adaptively proposed and the winner is chosen by a noisy finite-sample training estimate, "
            "the selected maximum can regress or be outranked on fresh held-out data even when every candidate obeys the same "
            "underlying generalization process. After convergence, neutral candidates will also be falsely promoted at high "
            "rates by weak mean-improves rules, while a calibrated paired significance gate should suppress those false elites "
            "and permit stopping. No harness-specific inversion variable is required for these observations."
        ),
        "opposite_principle": (
            "Harness selection is a post-selection inference problem before it is a new self-evolution mechanism: apparent "
            "train/test inversions and post-convergence progress must first be explained against finite-sample criterion "
            "variance, adaptive search, multiple comparisons, and winner's curse. A distinct mechanism exists only if a "
            "pre-specified harness structural variable predicts residual selection failure after those same-information controls."
        ),
        "opposite_search_seed": (
            "Reopen only on first-party paired gene histories with selected and rejected candidates, verification lineage, "
            "candidate counts, per-task outcomes, and downstream held-out outcomes. Fit a selection-aware baseline that is "
            "matched on candidate count, train sample size, adaptive search depth, verification rule, and deployment sample size; "
            "then ask whether a pre-registered harness structural variable predicts replicated ranking reversals or regret beyond "
            "that baseline. Do not reopen from another aggregate train/test reversal or another weak-crediting false positive rate."
        ),
        "scope": (
            "HarnessBank arXiv:2607.13683v2, specifically the current standalone PA-03 inference from the GDPval aggregate "
            "train/test ranking reversal and the TB2 post-convergence phantom-progress ablation. This closure does not claim "
            "that all future harness-selection transport questions reduce to winner's curse."
        ),
        "same_information_or_scope_matched": True,
        "same_information_reduction_verified": True,
        "positive_support": True,
        "evidence_refs": [
            SOURCE_REF,
            f"primary-fulltext:{SOURCE_REF}#sha256={EXPECTED_FULLTEXT_SHA256}",
            "JMLR:11(70):2079-2107:Cawley-Talbot-2010-model-selection-overfitting",
            "arXiv:1506.02629:adaptive-data-analysis-holdout-reuse",
            "arXiv:2605.05973:selection-aware-adaptive-LLM-benchmarking",
        ],
        "alternative_explanations_ruled_out": [
            "The 62-76% phantom-progress rate identifies a separate self-evolution failure mechanism: the primary paper defines these as post-convergence rounds with neutral candidates under weaker crediting, and reports that paired-2sigma verification prevents false elites and restores stopping.",
            "A single GDPval train/test rank reversal establishes a systematic inversion law: the paper reports the aggregate reversal but does not release the selected/rejected gene lineage, candidate-level uncertainty, or repeated inversion units required to distinguish systematic inversion from finite-sample selection variance.",
            "The current evidence shows the train-selected harness generally fails to generalize: HarnessBank reports positive sealed-test gains for the train-selected evolved harnesses; the cited PA-03 observation concerns ranking among variants, not collapse of the overall held-out gain.",
            "The missing lineage can be reconstructed from public code today: the v2 primary paper says code will be public upon acceptance, and the bounded first-party release audit found no replayable paired gene-history substrate.",
        ],
        "reopen_condition": (
            "Reopen only if a first-party release provides replayable paired selected-versus-rejected gene histories and downstream "
            "outcomes sufficient to match candidate count, selection pressure, train sample size, adaptive search depth, verification "
            "rule, and deployment sample size, and a preregistered harness-specific structural variable yields replicated residual "
            "ranking inversion or deployment regret beyond a strongest selection-aware/winner's-curse baseline."
        ),
    }
    audit = audit_dead_end_counter_explanation(counter)
    if not audit.get("passed"):
        raise ValueError(f"counter-explanation audit failed: {audit.get('blockers')}")

    support_sha = _sha(SUPPORT_AUDIT)
    return {
        "schema_version": "1.0",
        "candidate_id": CANDIDATE_ID,
        "source_ref": SOURCE_REF,
        "adjudicated_at": "2026-08-17",
        "status": "STOP_REDUCTION_SELECTION_BIAS_ABSORBS_CURRENT_PHENOMENON",
        "principle_dead_end_certified": True,
        "experiment_run_for_this_readjudication": False,
        "fresh_phenomenon_closure": {
            "source_ref": SOURCE_REF,
            "closed_evidence_sha256": [GDPVAL_BOUNDARY_EVIDENCE_SHA256],
            "primary_fulltext_sha256": EXPECTED_FULLTEXT_SHA256,
            "support_audit_sha256": support_sha,
            "closure_scope": (
                "current standalone PA-03 inference from one aggregate GDPval train/test rank reversal plus the TB2 neutral-candidate phantom-progress ablation"
            ),
            "scientific_authority": False,
        },
        "primary_observations": {
            "gdpval": {
                "train_lower_variant_test_gain_pp": 11.5,
                "train_selected_winner_test_gain_pp": 9.2,
                "unit": "single aggregate ranking reversal reported in ablation text",
                "evidence_sha256": GDPVAL_BOUNDARY_EVIDENCE_SHA256,
            },
            "phantom_progress": {
                "context": "post-convergence rounds with neutral candidates",
                "weak_crediting_rate_range_percent": [62, 76],
                "paired_2sigma_false_elites": 0,
                "weak_gate_false_elites": [2, 3],
                "paired_2sigma_rounds": 10.0,
                "weak_gate_rounds": ">20 cap",
            },
            "release": {
                "support_audit_status": support.get("status"),
                "required_unit": support.get("required_unit"),
                "code_disclosure": ((support.get("primary_source") or {}).get("code_disclosure")),
            },
        },
        "principle_diagnosis": {
            "status": "PRINCIPLE_DEAD_END_CERTIFIED",
            "counter_explanation_type": "SAME_INFORMATION_REDUCTION",
            "counter_explanation": counter,
            "audit": audit,
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
    }


def write_readjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    payload = build_readjudication()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = write_readjudication()
    print(DEFAULT_JSON)
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
