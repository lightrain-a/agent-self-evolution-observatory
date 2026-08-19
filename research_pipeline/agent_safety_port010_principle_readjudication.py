from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .principle_adjudication import audit_dead_end_counter_explanation

F0_IMMUTABLE = PROJECT_ROOT / "generated" / "agent-safety-port010-f0-framing-matched-immutable-20260819.json"
EXTRACTION_RECEIPT = PROJECT_ROOT / "generated" / "agent-safety-port010-f0-extraction-receipt-20260819.json"
REPLAY_RECEIPT = PROJECT_ROOT / "generated" / "agent-safety-port010-framing-replay-receipt-20260819.json"
RESULT_REVIEW = PROJECT_ROOT / "generated" / "agent-safety-port010-result-adjudication-20260819.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "agent-safety-port010-principle-readjudication-20260819.json"

F0_SHA256 = "56a670d7a4096e917a425b4ebc408d1fbf835e23eac21017c41ce268f0ef0b95"
EXTRACTION_RECEIPT_SHA256 = "988d5677c0278b356da5f880cd8ecfe47be637cbd2f758a2417c6192448c2f68"
RESULT_REVIEW_SHA256 = "370efd416c4c33724f990ff8fae1e596b973f505a04aa503e1c3ce572d3d1871"
PROTOCOL_SHA256 = "f702df8e74157829347c2c5d769ddecd934c1c78daf2ed2b97e6e25a5591bb65"
EXTRACTION_CACHE_SHA256 = "5f605e82dbbf3b93a33db7b797b0c8861a0b3f57b992eb978910b5174dadcdc3"


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def build_readjudication(
    *,
    f0: dict[str, Any] | None = None,
    extraction: dict[str, Any] | None = None,
    replay: dict[str, Any] | None = None,
    review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    f0 = f0 or _load(F0_IMMUTABLE)
    extraction = extraction or _load(EXTRACTION_RECEIPT)
    replay = replay or _load(REPLAY_RECEIPT)
    review = review or _load(RESULT_REVIEW)
    detectors = f0.get("detectors") or {}
    word = detectors.get("word") or {}
    char = detectors.get("char") or {}
    regex = detectors.get("regex") or {}
    gate = f0.get("gate_audit") or {}

    scope = (
        "PORT-010 exact standalone residual on released SkillJack/SkillX: SkillX extraction causes a detector-general "
        "detection failure on framed attacks that remains after controlling attack-framing/distribution shift."
    )
    statement = (
        "On the preregistered released-SkillJack 20-trajectory holdout, attack-framing support mismatch positively explains "
        "the binary detection failure attributed to extraction. Cross-framing word/character detectors score 100% on "
        "direct-naive attacks but 0% on the raw framed attacks before extraction, while framing-matched detectors retain "
        "95%->95% (word) and 80%->100% (character) binary detection after extraction. The extraction-specific residual is "
        "therefore absent under the matched framing control even though extraction can change continuous detector scores."
    )
    counter = {
        "type": "COUNTER_MECHANISM_SUPPORTED",
        "statement": statement,
        "opposite_prediction": (
            "If attack-framing support mismatch, rather than SkillX extraction, is the dominant cause of detector failure, "
            "detectors trained only on direct-naive attacks should fail on raw framed trajectories before extraction, while "
            "detectors trained on framed attacks should retain high binary detection after extraction. Both predictions are "
            "observed in the immutable framing-matched F0 replay."
        ),
        "opposite_principle": (
            "A raw-to-skill detector-score change is not evidence of detector-general extraction whitewashing unless detector "
            "support is matched to attack framing and the extraction-induced binary failure remains larger than the matched "
            "framing shift."
        ),
        "opposite_search_seed": (
            "Search for fresh preregistered settings where attack-framing-matched competent detectors still show a practically "
            "large extraction-specific binary detection collapse across at least two independent detector families; otherwise "
            "move to a different decision object such as semantic-effect retention rather than reusing detector score drop."
        ),
        "scope": scope,
        "same_information_or_scope_matched": True,
        "counter_prediction_observed": True,
        "positive_support": True,
        "evidence_refs": [
            "arXiv:2608.03509",
            "generated/agent-safety-port010-f0-framing-matched-immutable-20260819.json",
            "generated/agent-safety-port010-f0-extraction-receipt-20260819.json",
            "generated/agent-safety-port010-framing-replay-receipt-20260819.json",
            "generated/agent-safety-port010-result-adjudication-20260819.json",
        ],
        "alternative_explanations_ruled_out": [
            "Mutable-result provenance drift: the adjudicated F0 bytes were deterministically rebuilt with zero provider calls and reproduced SHA-256 56a670d7... exactly before certification.",
            "Detector incapacity: framing-matched word and character detectors detect 95% and 80% of raw held-out framed attacks, while direct-naive-trained cross-framing detectors detect 100% of direct-naive attacks.",
            "Extraction/substrate failure: the frozen extraction receipt records full source-linked pairing for all 20 required holdout units.",
            "Threshold leakage: detector thresholds were selected from five-fold OOF training data with the F0 holdout excluded.",
            "A weak fixed regex detector is sufficient: regex has only 45% raw framed sensitivity, whereas the two competent learned families preserve or improve binary detection after extraction.",
        ],
        "reopen_condition": (
            "Reopen only with fresh preregistered evidence, not threshold changes or post-hoc subgroups: on a new holdout with "
            "attack-framing-matched detector training/support, at least two independent competent detector families must show "
            "a statistically supported and practically large extraction-specific binary detection drop that exceeds the "
            "matched framing-shift control, or a new pre-outcome structural variable must force such a prediction under matched information."
        ),
    }
    return {
        "schema_version": "1.1",
        "generated_at": str(replay.get("generated_at") or ""),
        "candidate_id": "PORT-010",
        "parent_source": "arXiv:2608.03509",
        "title": "Skill-extraction detector-general whitewashing does not survive attack-framing-matched detection control",
        "search_primitive": "COMPOSITION_INTERACTION",
        "principle_dead_end_certified": True,
        "stop_class": "PRINCIPLE_STOP",
        "benchmark_level_dead_end_certified": False,
        "broader_core_principle_falsified": False,
        "dead_end_scope": scope,
        "experiment_run_for_this_readjudication": True,
        "provenance_status": "IMMUTABLE_ZERO_PROVIDER_REPLAY_BOUND",
        "registered_f0": {
            "decision": f0.get("decision"),
            "full_20_pairing": gate.get("full_20_pairing"),
            "gate1_detectors": gate.get("gate1_extraction_shift_detectors") or [],
            "gate2_detectors": gate.get("gate2_exceeds_framing_shift_detectors") or [],
            "framing_confound_detectors": gate.get("framing_confound_detectors") or [],
            "word": {key: word.get(key) for key in (
                "raw_framed_within_detection_rate", "extracted_framed_within_detection_rate",
                "raw_framed_cross_detection_rate", "raw_direct_naive_cross_detection_rate",
                "extraction_drop_within", "framing_drop_cross", "paired_extraction_permutation_p_one_sided",
            )},
            "char": {key: char.get(key) for key in (
                "raw_framed_within_detection_rate", "extracted_framed_within_detection_rate",
                "raw_framed_cross_detection_rate", "raw_direct_naive_cross_detection_rate",
                "extraction_drop_within", "framing_drop_cross", "paired_extraction_permutation_p_one_sided",
            )},
            "regex": {key: regex.get(key) for key in (
                "raw_framed_within_detection_rate", "extracted_framed_within_detection_rate",
                "extraction_drop_within", "framing_drop_cross", "paired_extraction_permutation_p_one_sided",
            )},
        },
        "principle_diagnosis": {
            "status": "PRINCIPLE_DEAD_END_CERTIFIED_SCOPED",
            "counter_explanation_type": "COUNTER_MECHANISM_SUPPORTED",
            "counter_explanation": counter,
        },
        "independent_review": {
            "kimi_disposition": (review.get("kimiz_diagnosis") or {}).get("disposition"),
            "kimi_failure_layer": (review.get("kimiz_diagnosis") or {}).get("failure_layer"),
            "kimi_persistent_dead_end_authorized": (review.get("kimiz_diagnosis") or {}).get("persistent_dead_end_authorized"),
            "deepseek_disposition": (review.get("independent_adjudication") or {}).get("disposition"),
            "deepseek_failure_layer": (review.get("independent_adjudication") or {}).get("failure_layer"),
            "deepseek_persistent_dead_end_authorized": (review.get("independent_adjudication") or {}).get("persistent_dead_end_authorized"),
        },
        "scientific_interpretation": {
            "safe_claim": (
                "PORT-010's exact detector-general whitewashing residual is closed in the released SkillJack/SkillX setting: "
                "framing/support mismatch can create the detector failure before extraction, while framing-matched learned "
                "detectors retain high binary detection after extraction. This does not imply that extraction has zero score "
                "effect, that SkillJack is invalid, that SkillX is safe, or that agent-safety/skill-extraction research is exhausted."
            ),
            "negative_experiment_alone_authorized_dead_end": False,
            "positive_counter_mechanism_required": True,
            "skilljack_source_still_useful": True,
            "skillx_security_exhausted": False,
            "port013_port014_automatically_closed": False,
            "next_action": "Persist only this exact scoped closure; continue searching other safety problem objects and support holds.",
        },
        "source_artifact_sha256": {
            "immutable_f0": _sha(F0_IMMUTABLE),
            "extraction_receipt": _sha(EXTRACTION_RECEIPT),
            "replay_receipt": _sha(REPLAY_RECEIPT),
            "independent_result_review": _sha(RESULT_REVIEW),
        },
        "replay_binding": {
            "status": replay.get("status"),
            "byte_identical_to_adjudicated_result": ((replay.get("replay_result") or {}).get("byte_identical_to_adjudicated_result")),
            "provider_calls_executed": ((replay.get("replay_result") or {}).get("provider_calls_executed")),
            "immutable_f0_sha256": ((replay.get("replay_result") or {}).get("sha256")),
            "review_bound_f0_sha256": ((replay.get("independent_adjudication") or {}).get("bound_f0_sha256")),
        },
        "authority": {
            "experiment_alone_authorizes_dead_end": False,
            "positive_counter_mechanism_authorizes_scoped_dead_end": True,
            "benchmark_level_dead_end": False,
            "automatic_problem_gate_authority": False,
            "automatic_method_authority": False,
            "automatic_experiment_authority": False,
            "automatic_p0_authority": False,
            "automatic_gpu_authority": False,
            "scientific_authority": "principle-adjudication-only",
        },
        "scientific_authority": False,
    }


def validate_readjudication(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("stop_class") != "PRINCIPLE_STOP" or state.get("principle_dead_end_certified") is not True:
        errors.append("scoped principle stop missing")
    if state.get("benchmark_level_dead_end_certified") is not False or state.get("broader_core_principle_falsified") is not False:
        errors.append("broader scope leakage")
    if state.get("provenance_status") != "IMMUTABLE_ZERO_PROVIDER_REPLAY_BOUND":
        errors.append("immutable replay provenance missing")

    hashes = state.get("source_artifact_sha256") or {}
    if hashes.get("immutable_f0") != F0_SHA256:
        errors.append("immutable F0 hash mismatch")
    if hashes.get("extraction_receipt") != EXTRACTION_RECEIPT_SHA256:
        errors.append("extraction receipt hash mismatch")
    if hashes.get("independent_result_review") != RESULT_REVIEW_SHA256:
        errors.append("independent review hash mismatch")
    if not isinstance(hashes.get("replay_receipt"), str) or len(hashes.get("replay_receipt")) != 64:
        errors.append("replay receipt hash missing")

    replay = _load(REPLAY_RECEIPT)
    replay_result = replay.get("replay_result") or {}
    replay_inputs = replay.get("replay_inputs") or {}
    replay_review = replay.get("independent_adjudication") or {}
    if replay.get("status") != "ZERO_PROVIDER_IMMUTABLE_REPLAY_VERIFIED" or replay_result.get("byte_identical_to_adjudicated_result") is not True or replay_result.get("provider_calls_executed") != 0:
        errors.append("zero-provider replay binding invalid")
    if replay_result.get("sha256") != F0_SHA256 or replay_review.get("bound_f0_sha256") != F0_SHA256:
        errors.append("replay F0 binding invalid")
    if replay_inputs.get("protocol_sha256") != PROTOCOL_SHA256 or replay_inputs.get("extraction_cache_sha256") != EXTRACTION_CACHE_SHA256:
        errors.append("replay input binding invalid")
    if replay_inputs.get("extraction_receipt_sha256") != EXTRACTION_RECEIPT_SHA256 or replay_review.get("sha256") != RESULT_REVIEW_SHA256:
        errors.append("replay receipt chain invalid")

    extraction = _load(EXTRACTION_RECEIPT)
    if extraction.get("status") != "EXTRACTION_COMPLETE_FULL_PAIRING" or extraction.get("usable_units") != 20:
        errors.append("extraction support binding invalid")
    if extraction.get("protocol_sha256") != PROTOCOL_SHA256 or extraction.get("extraction_cache_sha256") != EXTRACTION_CACHE_SHA256:
        errors.append("extraction provenance drift")

    f0 = state.get("registered_f0") or {}
    if f0.get("decision") != "PORT010_E_AXIS_F0_NEGATIVE_NO_PRINCIPLE_STOP" or f0.get("full_20_pairing") is not True:
        errors.append("F0 binding invalid")
    if f0.get("gate1_detectors") or f0.get("gate2_detectors"):
        errors.append("registered GO gate unexpectedly passed")
    if set(f0.get("framing_confound_detectors") or []) != {"word", "char", "regex"}:
        errors.append("framing counter-mechanism audit drift")
    word = f0.get("word") or {}
    char = f0.get("char") or {}
    if (
        word.get("raw_framed_within_detection_rate"), word.get("extracted_framed_within_detection_rate"),
        word.get("raw_framed_cross_detection_rate"), word.get("raw_direct_naive_cross_detection_rate"),
    ) != (0.95, 0.95, 0.0, 1.0):
        errors.append("word evidence drift")
    if (
        char.get("raw_framed_within_detection_rate"), char.get("extracted_framed_within_detection_rate"),
        char.get("raw_framed_cross_detection_rate"), char.get("raw_direct_naive_cross_detection_rate"),
    ) != (0.8, 1.0, 0.0, 1.0):
        errors.append("char evidence drift")

    counter = (state.get("principle_diagnosis") or {}).get("counter_explanation") or {}
    audit = audit_dead_end_counter_explanation(counter)
    if audit.get("passed") is not True:
        errors.append("counter explanation invalid:" + ",".join(audit.get("blockers") or []))

    review = state.get("independent_review") or {}
    for prefix in ("kimi", "deepseek"):
        if review.get(f"{prefix}_disposition") != "STOP_SCOPED_RESIDUAL" or review.get(f"{prefix}_failure_layer") != "core_principle" or review.get(f"{prefix}_persistent_dead_end_authorized") is not True:
            errors.append(f"{prefix} independent adjudication mismatch")
    if (state.get("scientific_interpretation") or {}).get("negative_experiment_alone_authorized_dead_end") is not False:
        errors.append("negative experiment cannot authorize dead end")
    if (state.get("scientific_interpretation") or {}).get("positive_counter_mechanism_required") is not True:
        errors.append("positive counter-mechanism requirement missing")
    return sorted(set(errors))


def write_readjudication(path: Path = DEFAULT_JSON) -> dict[str, Any]:
    state = build_readjudication()
    errors = validate_readjudication(state)
    if errors:
        raise ValueError("Invalid PORT-010 principle readjudication:\n- " + "\n- ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


if __name__ == "__main__":
    print(json.dumps(write_readjudication(), ensure_ascii=False, indent=2))
