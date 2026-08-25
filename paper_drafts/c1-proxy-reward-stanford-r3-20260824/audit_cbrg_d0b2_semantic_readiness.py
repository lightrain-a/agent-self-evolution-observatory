#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
AUDIT_ID = "C1-CBRG-D0B2-SEMANTIC-READINESS-V1"
STATUS = "D0B2_SEMANTIC_ADJUDICATOR_NOT_BOUND_READINESS_HOLD"
DECISION = "D0B2_READINESS_HOLD_NO_ADMISSIBLE_OUTCOME_INDEPENDENT_VALIDITY_SIGNAL"

HERE = Path(__file__).resolve().parent
PROGRAM = HERE / "mechanism-closure-program-20260824.json"
B1C = HERE / "cbrg-d0b1c-operational-contrast-evidence-locator-20260824.json"
OUT = HERE / "cbrg-d0b2-semantic-readiness-audit-20260824.json"
B1C_SHA256 = "d127ea711288fc6455923198e48bdc9c6674663ad210aca30372256270b31d74"

MINILM = Path(
    "/data/wyt/agent-self-evolution-observatory/runs/"
    "d2-proxy-reward-b3-expanded-retrieval-exposure-20260824/"
    "exact-minilm-l6-v2"
)
MINILM_CONFIG_SHA256 = "953f9c0d463486b10a6871cc2fd59f223b2c70184f49815e7efbcab5d8908b41"
MINILM_WEIGHTS_SHA256 = "53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db"

# Search roots are bounded to the active user's Hugging Face cache and the
# canonical Agent Self-Evolution data root. The resulting zero-candidate fact is
# a snapshot receipt, not a permanent global claim.
MODEL_SEARCH_ROOTS = (
    Path("/home/wyt/.cache/huggingface/hub"),
    Path("/data/wyt/agent-self-evolution-observatory"),
)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def semantic_labels(config: dict[str, Any]) -> set[str]:
    labels: set[str] = set()
    for key in ("id2label", "label2id"):
        value = config.get(key)
        if isinstance(value, dict):
            labels.update(str(k).lower() for k in value.keys())
            labels.update(str(v).lower() for v in value.values())
    return labels


def find_local_nli_classifier_configs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    visited: set[str] = set()
    for root in MODEL_SEARCH_ROOTS:
        if not root.is_dir():
            continue
        for config_path in root.rglob("config.json"):
            # Keep the scan bounded away from Python package metadata / unrelated
            # huge trees; model configs need a sibling or nearby model weights.
            parent = config_path.parent
            weight_candidates = list(parent.glob("*.safetensors")) + list(parent.glob("pytorch_model*.bin"))
            if not weight_candidates:
                continue
            try:
                config = load_json(config_path)
            except (OSError, json.JSONDecodeError, RuntimeError):
                continue
            labels = semantic_labels(config)
            has_entailment = any("entail" in label for label in labels)
            has_contradiction = any("contrad" in label for label in labels)
            if not (has_entailment and has_contradiction):
                continue
            resolved = str(config_path.resolve())
            if resolved in visited:
                continue
            visited.add(resolved)
            rows.append(
                {
                    "config_path": resolved,
                    "config_sha256": sha_file(config_path),
                    "architectures": config.get("architectures"),
                    "model_type": config.get("model_type"),
                    "id2label": config.get("id2label"),
                    "label2id": config.get("label2id"),
                    "weight_files": [
                        {"path": str(path.resolve()), "sha256": sha_file(path)}
                        for path in sorted(weight_candidates)[:4]
                    ],
                }
            )
    return sorted(rows, key=lambda row: row["config_path"])


def main() -> None:
    require(B1C.is_file(), "missing B1c operational-contrast locator artifact")
    require(sha_file(B1C) == B1C_SHA256, "B1c artifact SHA drift")
    b1c = load_json(B1C)
    summary = b1c.get("summary") or {}
    require(b1c.get("decision") == "D0B1C_COMPILER_GO_LOCATOR_PARTIAL_FAIL_CLOSED_D0B2_READY", "B1c decision drift")
    require(summary.get("directional_branch_contrast_units") == 423, "B1c unit count drift")
    require(summary.get("units_with_exact_nonzero_lexical_evidence_anchor") == 397, "B1c located count drift")
    require(summary.get("units_without_nonzero_lexical_evidence_anchor") == 26, "B1c unlocated count drift")
    require(summary.get("semantic_validity_adjudicated_units") == 0, "B1c semantic authority leaked")

    require(MINILM.is_dir(), "frozen MiniLM baseline directory missing")
    require(sha_file(MINILM / "config.json") == MINILM_CONFIG_SHA256, "MiniLM config SHA drift")
    require(sha_file(MINILM / "model.safetensors") == MINILM_WEIGHTS_SHA256, "MiniLM weights SHA drift")
    minilm_config = load_json(MINILM / "config.json")
    require((minilm_config.get("architectures") or []) == ["BertModel"], "MiniLM architecture drift")
    require(minilm_config.get("id2label") in (None, {}), "MiniLM unexpectedly acquired classifier labels")
    require(minilm_config.get("label2id") in (None, {}), "MiniLM unexpectedly acquired classifier labels")

    program = load_json(PROGRAM)
    registered_binding = program.get("semantic_adjudicator_binding")
    require(registered_binding in (None, {}, []), "a semantic adjudicator is already registered; readiness audit must be superseded")

    local_nli_configs = find_local_nli_classifier_configs()

    # Existence of a generic NLI classifier would still not be sufficient. A C1
    # adjudicator must be independently qualified on pre-outcome support /
    # contradiction cases before it can label the 423 branch-contrast units.
    qualification_receipts = sorted(
        str(path.relative_to(HERE))
        for path in HERE.glob("*semantic*qualification*.json")
        if path.resolve() != OUT.resolve()
    )

    admissible_candidates: list[dict[str, Any]] = []
    for row in local_nli_configs:
        # Current audit has no C1 qualification receipt tied to a candidate SHA.
        # Therefore even a discovered generic classifier remains unqualified.
        row = dict(row)
        row["c1_qualification_receipt_bound"] = False
        row["admissible_for_c1_b2"] = False
        admissible_candidates.append(row)

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "c1-d0b2-semantic-adjudicator-readiness-audit",
        "audit_id": AUDIT_ID,
        "paper_id": PAPER_ID,
        "status": STATUS,
        "decision": DECISION,
        "input_binding": {
            "b1c_artifact": str(B1C.relative_to(HERE.parents[1])),
            "b1c_sha256": B1C_SHA256,
            "operational_units": 423,
            "exact_candidate_anchors": 397,
            "unlocated_units": 26,
        },
        "adjudicator_contract": {
            "allowed_inputs": [
                "content-addressed operational branch-contrast unit",
                "content-addressed pre-writer evidence span(s) from the same frozen trajectory",
            ],
            "required_output_states": ["SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"],
            "required_capabilities": [
                "distinguish semantic support from contradiction rather than return only similarity",
                "return UNVERIFIABLE when evidence is absent or insufficient",
                "operate without terminal reward, task rubric, downstream outcome, or treatment label as validity evidence",
                "be frozen/content-addressed and reproducible offline or be an equally deterministic registered rule",
                "carry an independent C1 qualification receipt before labeling the scientific pool",
            ],
            "same_information_baselines": [
                "lexical overlap / exact anchor availability",
                "MiniLM semantic similarity / applicability",
                "neutral/metadata memory controls",
                "generic common-core/residual factorization",
            ],
            "incremental_information_requirement": "A future adjudicator must produce reproducible support/contradiction/unverifiable information not reducible to a monotone transform of locator or semantic similarity on the same frozen support.",
            "unlocated_policy": "The 26 B1c units without a nonzero exact lexical anchor are forced fail-closed and cannot receive imputed support authority. A future B2 adjudicator may only mark them UNVERIFIABLE unless a separately frozen outcome-independent evidence locator is added before adjudication.",
        },
        "local_asset_audit": {
            "search_roots": [str(path) for path in MODEL_SEARCH_ROOTS],
            "nli_classifier_configs_with_entailment_and_contradiction_labels": len(local_nli_configs),
            "nli_classifier_candidates": local_nli_configs,
            "c1_semantic_qualification_receipts": qualification_receipts,
            "registered_semantic_adjudicator_binding_present": False,
            "admissible_qualified_adjudicators": 0,
        },
        "baseline_asset_boundary": {
            "minilm_path": str(MINILM),
            "minilm_config_sha256": MINILM_CONFIG_SHA256,
            "minilm_weights_sha256": MINILM_WEIGHTS_SHA256,
            "architecture": minilm_config.get("architectures"),
            "id2label": minilm_config.get("id2label"),
            "label2id": minilm_config.get("label2id"),
            "classification": "EMBEDDING_SIMILARITY_BASELINE_ONLY_NOT_A_VALIDITY_ADJUDICATOR",
        },
        "readiness_summary": {
            "operational_units_ready": 423,
            "exact_candidate_anchors_ready": 397,
            "future_forced_unverifiable_without_new_locator": 26,
            "qualified_semantic_adjudicators_bound": 0,
            "semantic_validity_adjudicated_units": 0,
            "supported_units": 0,
            "contradicted_units": 0,
            "unverifiable_units_adjudicated": 0,
            "nonzero_branch_authority_units": 0,
            "provider_calls": 0,
            "gpu_runs": 0,
        },
        "scientific_interpretation": "B1c makes the operational contrast and candidate evidence locations executable, but the current frozen local stack contains no qualified C1 semantic-validity adjudicator. MiniLM and lexical overlap are explicitly baseline/locator signals and cannot be relabeled as support evidence. Therefore B2 semantic execution is not scientifically admissible in the current zero-call round.",
        "next_permitted_action": "Zero-call qualification/binding work only: bind a frozen entailment/contradiction-capable local classifier or deterministic semantic rule together with an independent pre-outcome C1 qualification receipt, then re-run B2 readiness. If no such validity signal can be qualified without reward/outcome leakage or similarity reduction, STOP/MERGE CBRG and preserve C1 as the stage-resolved identification/measurement paper.",
        "reopen_conditions": [
            "a content-addressed local classifier/rule with explicit SUPPORTED/CONTRADICTED/UNVERIFIABLE semantics is bound",
            "an independent C1 qualification receipt demonstrates semantic support/contradiction discrimination on pre-outcome evidence",
            "the adjudicator is shown not to reduce to lexical or embedding similarity/applicability on the same information",
            "the 26 currently unlocated units remain fail-closed unless a separately frozen outcome-independent locator is added before semantic adjudication",
        ],
        "provider_calls_added_by_this_audit": 0,
        "gpu_runs_added_by_this_audit": 0,
        "scientific_authority": False,
        "experiment_authority": False,
        "provider_call_authority": False,
        "gpu_authority": False,
        "claim_expansion_authority": False,
        "submission_authority": False,
    }

    require(payload["local_asset_audit"]["admissible_qualified_adjudicators"] == 0, "qualified adjudicator unexpectedly available")
    require(payload["readiness_summary"]["semantic_validity_adjudicated_units"] == 0, "semantic validity must remain zero")
    require(payload["readiness_summary"]["nonzero_branch_authority_units"] == 0, "branch authority must remain zero")
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": STATUS,
                "decision": DECISION,
                **payload["local_asset_audit"],
                **payload["readiness_summary"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
