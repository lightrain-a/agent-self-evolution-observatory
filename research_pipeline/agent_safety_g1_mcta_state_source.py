from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path
from typing import Any

ALGORITHM_ID = "G1-MCTA-STATE-SOURCE-HASH-V1"
EXPERIMENT_NAMESPACE = "G1-MCTA-v1"
FAMILIES = ["gitlab", "map", "reddit", "shopping", "shopping_admin"]
P1_FAMILY_QUOTAS = (3, 3, 2)


class StateSourceError(ValueError):
    pass


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def split_workflow_units(text: str) -> list[dict[str, Any]]:
    starts = [m.start() for m in re.finditer(r"(?m)^Query:", text)]
    if not starts:
        raise StateSourceError("workflow source has no Query units")
    units: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        raw = text[start:end]
        units.append({
            "index": index,
            "raw": raw,
            "sha256": sha_text(raw),
        })
    return units


def serialize_state(units: list[dict[str, Any]]) -> bytes:
    if len(units) != 3:
        raise StateSourceError("a state must contain exactly three workflow units")
    return ("\n\n".join(str(unit["raw"]).strip("\n") for unit in units) + "\n").encode("utf-8")


def family_role_split(families: list[str] | None = None) -> tuple[list[dict[str, str]], list[str], list[str]]:
    families = list(families or FAMILIES)
    if len(families) != 5 or len(set(families)) != 5:
        raise StateSourceError("exactly five distinct workflow source families are required")
    ranked = sorted(
        (sha_text(f"{EXPERIMENT_NAMESPACE}|STATE_FAMILY_RANK|{family}"), family)
        for family in families
    )
    state_families = [family for _, family in ranked[:3]]
    update_families = [family for _, family in ranked[3:]]
    rows = [{"family": family, "rank_key": key} for key, family in ranked]
    return rows, state_families, update_families


def candidate_states(
    family: str,
    units: list[dict[str, Any]],
    historical_exact_state_hashes: set[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for combo in itertools.combinations(units, 3):
        raw = serialize_state(list(combo))
        workflow_sha = sha_bytes(raw)
        if workflow_sha in historical_exact_state_hashes:
            continue
        rank_key = sha_text(
            f"{EXPERIMENT_NAMESPACE}|STATE_CANDIDATE|{family}|"
            + "|".join(str(unit["sha256"]) for unit in combo)
        )
        rows.append({
            "rank_key": rank_key,
            "family": family,
            "unit_indices": [int(unit["index"]) for unit in combo],
            "unit_sha256": [str(unit["sha256"]) for unit in combo],
            "workflow_sha256": workflow_sha,
            "bytes": len(raw),
        })
    return sorted(rows, key=lambda row: str(row["rank_key"]))


def build_manifest(
    *,
    source_texts: dict[str, str],
    source_file_sha256: dict[str, str],
    historical_exact_state_hashes: set[str],
) -> dict[str, Any]:
    if set(source_texts) != set(FAMILIES):
        raise StateSourceError("source_texts must contain the exact frozen five-family source set")
    rank_rows, state_families, update_families = family_role_split()
    unit_map = {family: split_workflow_units(source_texts[family]) for family in FAMILIES}
    candidates = {
        family: candidate_states(family, unit_map[family], historical_exact_state_hashes)
        for family in state_families
    }
    if any(len(candidates[family]) < 4 for family in state_families[:2]) or len(candidates[state_families[2]]) < 2:
        raise StateSourceError("insufficient state candidates after exact historical-state exclusion")

    p0_states: list[dict[str, Any]] = []
    used_hashes: set[str] = set()
    for family in state_families[:2]:
        row = dict(candidates[family][0])
        row["state_id"] = f"P0-{len(p0_states)+1:02d}-{family}"
        p0_states.append(row)
        used_hashes.add(str(row["workflow_sha256"]))

    p1_states: list[dict[str, Any]] = []
    for family, quota in zip(state_families, P1_FAMILY_QUOTAS):
        selected = 0
        for source_row in candidates[family]:
            if str(source_row["workflow_sha256"]) in used_hashes:
                continue
            row = dict(source_row)
            row["state_id"] = f"P1-{len(p1_states)+1:02d}-{family}"
            p1_states.append(row)
            used_hashes.add(str(row["workflow_sha256"]))
            selected += 1
            if selected == quota:
                break
        if selected != quota:
            raise StateSourceError(f"could not satisfy P1 family quota:{family}:{quota}")

    update_sequences: list[dict[str, Any]] = []
    for family in update_families:
        ranked_units = sorted(
            unit_map[family],
            key=lambda unit: sha_text(
                f"{EXPERIMENT_NAMESPACE}|UPDATE_SELECT|{family}|{unit['sha256']}"
            ),
        )[:3]
        ordered_units = sorted(
            ranked_units,
            key=lambda unit: sha_text(
                f"{EXPERIMENT_NAMESPACE}|UPDATE_ORDER|{family}|{unit['sha256']}"
            ),
        )
        update_sequences.append({
            "sequence_id": f"UPD-{len(update_sequences)+1:02d}-{family}",
            "family": family,
            "steps": [
                {
                    "step": step,
                    "unit_index": int(unit["index"]),
                    "unit_sha256": str(unit["sha256"]),
                }
                for step, unit in enumerate(ordered_units, start=1)
            ],
        })

    historical_hash_set_sha = sha_text("\n".join(sorted(historical_exact_state_hashes)) + "\n")
    return {
        "schema_version": "1.0",
        "artifact_id": "AGENT-SAFETY-G1-MCTA-FRESH-STATE-SOURCE-MANIFEST-20260904",
        "algorithm_id": ALGORITHM_ID,
        "experiment_namespace": EXPERIMENT_NAMESPACE,
        "status": "ZERO_PROVIDER_FRESH_STATE_AND_UPDATE_SOURCE_FREEZE_NO_EXECUTION_AUTHORITY",
        "source_file_sha256": source_file_sha256,
        "historical_exact_state_hash_count": len(historical_exact_state_hashes),
        "historical_exact_state_hash_set_sha256": historical_hash_set_sha,
        "state_family_rank": rank_rows,
        "state_families": state_families,
        "update_families": update_families,
        "source_unit_counts": {family: len(unit_map[family]) for family in FAMILIES},
        "p0_states": p0_states,
        "p1_states": p1_states,
        "update_sequences": update_sequences,
        "selection_policy": {
            "safety_outcomes_used": False,
            "semantic_evaluator_labels_used": False,
            "historical_exact_state_bytes_excluded": True,
            "p0_exact_states_disjoint_from_p1_exact_states": True,
            "p1_family_quotas": list(P1_FAMILY_QUOTAS),
            "state_units_per_state": 3,
            "serialization": "strip leading/trailing newlines per exact AWM unit, join units by two newlines, terminate file by one newline",
            "replacement_after_future_outcome": False,
        },
        "authority": {
            "provider_calls": False,
            "p0_execution": False,
            "p1_execution": False,
            "harmful_model_calls": False,
            "paper_claim_upgrade": False,
        },
    }


def reconstruct_state_bytes(
    manifest_state: dict[str, Any],
    source_text: str,
) -> bytes:
    units = split_workflow_units(source_text)
    selected = [units[int(index)] for index in manifest_state["unit_indices"]]
    raw = serialize_state(selected)
    if sha_bytes(raw) != manifest_state["workflow_sha256"]:
        raise StateSourceError(f"state hash mismatch:{manifest_state.get('state_id')}")
    return raw


def reconstruct_update_unit_bytes(
    step: dict[str, Any],
    source_text: str,
) -> bytes:
    units = split_workflow_units(source_text)
    unit = units[int(step["unit_index"])]
    raw = str(unit["raw"]).encode("utf-8")
    if sha_bytes(raw) != step["unit_sha256"]:
        raise StateSourceError("update unit hash mismatch")
    return raw


def load_source_texts(source_root: Path) -> tuple[dict[str, str], dict[str, str]]:
    texts: dict[str, str] = {}
    hashes: dict[str, str] = {}
    for family in FAMILIES:
        path = Path(source_root) / f"{family}.txt"
        raw = path.read_bytes()
        texts[family] = raw.decode("utf-8")
        hashes[family] = sha_bytes(raw)
    return texts, hashes


def historical_state_hashes(runtime_root: Path) -> set[str]:
    hashes: set[str] = set()
    for path in Path(runtime_root).glob("**/states/*.txt"):
        try:
            hashes.add(sha_bytes(path.read_bytes()))
        except OSError:
            continue
    return hashes


def materialize_manifest(
    manifest: dict[str, Any],
    *,
    source_root: Path,
    output_root: Path,
) -> None:
    source_texts, source_hashes = load_source_texts(source_root)
    if source_hashes != manifest["source_file_sha256"]:
        raise StateSourceError("source file bytes drifted")
    output_root = Path(output_root)
    state_dir = output_root / "states"
    update_dir = output_root / "updates"
    state_dir.mkdir(parents=True, exist_ok=False)
    update_dir.mkdir(parents=True, exist_ok=False)
    for row in [*manifest["p0_states"], *manifest["p1_states"]]:
        raw = reconstruct_state_bytes(row, source_texts[str(row["family"])])
        (state_dir / f"{row['state_id']}.txt").write_bytes(raw)
    for sequence in manifest["update_sequences"]:
        family = str(sequence["family"])
        for step in sequence["steps"]:
            raw = reconstruct_update_unit_bytes(step, source_texts[family])
            (update_dir / f"{sequence['sequence_id']}__step{step['step']}.txt").write_bytes(raw)
    (output_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
