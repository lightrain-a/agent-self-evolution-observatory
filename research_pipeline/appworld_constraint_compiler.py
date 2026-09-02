from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
import tempfile
from itertools import combinations
from pathlib import Path
from typing import Any

OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
COMPILER_ID = "APPWORLD-CONSTRAINT-COMPILER-V1"
EXPECTED_APPWORLD_SHA = "a072b7a86e7c1d5b1d7175659d750ebb9b79f10a"
ALLOWED_EDGE_TYPES = {
    "SHARED_MUTABLE_STATE",
    "SHARED_STATE_CHANGING_API_RESOURCE",
    "READ_AFTER_WRITE_DEPENDENCY",
    "PREREQUISITE_DEPENDENCY",
    "TEMPORAL_DEPENDENCY",
}
FORBIDDEN_OUTCOME_KEYS = {
    "observed_outcome", "scientific_outcome", "target_score",
    "collateral_regression", "crr", "ue", "trg", "model_success",
    "effect_estimate",
}


class QualificationError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return keys


def load_protected_spec(bundle_path: Path) -> dict[str, Any]:
    try:
        from appworld.common.constants import PASSWORD, SALT
        from appworld.common.crypto import bundle_file_path_to_content
    except ImportError as exc:
        raise QualificationError(
            "AppWorld runtime is required to open the protected compiler bundle."
        ) from exc
    contents = bundle_file_path_to_content(
        str(bundle_path),
        password=PASSWORD,
        salt=SALT,
        include_file_paths=["compiler_spec/family_spec.json"],
    )
    try:
        return json.loads(contents["compiler_spec/family_spec.json"])
    except KeyError as exc:
        raise QualificationError("Protected bundle lacks family_spec.json") from exc


def git_head(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def validate_source(appworld_root: Path) -> dict[str, Any]:
    if git_head(appworld_root) != EXPECTED_APPWORLD_SHA:
        raise QualificationError("AppWorld source revision drifted from the frozen commit.")
    data_root = appworld_root / "data"
    version_path = data_root / "version.txt"
    license_path = appworld_root / "LICENSE"
    required_apps = ("file_system", "gmail", "todoist", "simple_note")
    base_db_hashes: dict[str, str] = {}
    for app in required_apps:
        db_path = data_root / "base_dbs" / f"{app}.db"
        if not db_path.is_file():
            raise QualificationError(f"Missing AppWorld base database for {app}.")
        base_db_hashes[app] = file_sha256(db_path)
    protected_bundles = [
        appworld_root / "generate" / ".source" / "data.bundle",
        appworld_root / "generate" / ".source" / "tasks.bundle",
        appworld_root / "src" / "appworld" / ".source" / "apps.bundle",
        appworld_root / "src" / "appworld" / ".source" / "tests.bundle",
    ]
    return {
        "appworld_repo_sha": EXPECTED_APPWORLD_SHA,
        "data_version_sha256": file_sha256(version_path),
        "data_version": version_path.read_text(encoding="utf-8").strip(),
        "license_sha256": file_sha256(license_path),
        "base_db_sha256": base_db_hashes,
        "protected_bundle_sha256": {
            str(path.relative_to(appworld_root)): file_sha256(path)
            for path in protected_bundles
        },
    }


def insert_fixture_row(connection: sqlite3.Connection, row: dict[str, Any]) -> None:
    values = dict(row["values"])
    fixture_timestamp = "2023-05-18 12:00:00.000000"
    app = row.get("app")
    table = row.get("table")
    if app == "file_system" and table in {"directories", "files"}:
        # Raw SQLite insertion bypasses SQLModel default factories. Populate the
        # API-visible native timestamps explicitly so show_file/show_directory
        # responses remain valid.
        values.setdefault("created_at", fixture_timestamp)
        values.setdefault("updated_at", fixture_timestamp)
    if app == "file_system" and table == "files":
        # AppWorld's native File model stores an empty JSON list for ordinary
        # uncompressed text files. Leaving this column NULL makes cross-app
        # attachment transfer invalid even though the file content/path exist.
        values.setdefault("compressed_data", "[]")
    if app == "simple_note" and table == "notes":
        values.setdefault("created_at", fixture_timestamp)
        values.setdefault("updated_at", fixture_timestamp)
    if app == "todoist" and table == "tasks":
        values.setdefault("priority", "low")
        values.setdefault("created_at", fixture_timestamp)
    columns = list(values)
    placeholders = ", ".join("?" for _ in columns)
    quoted = ", ".join(f'"{column}"' for column in columns)
    connection.execute(
        f'INSERT INTO "{row["table"]}" ({quoted}) VALUES ({placeholders})',
        [values[column] for column in columns],
    )
    if app == "simple_note" and table == "notes":
        # AppWorld search_notes ranks through notes_fts. Raw fixture insertion
        # bypasses SQLModel.set_search_text(), so the scientific note would
        # otherwise exist in the table but be invisible to the public search API.
        raw_tags = values.get("tags", [])
        if isinstance(raw_tags, str):
            try:
                parsed_tags = json.loads(raw_tags)
            except json.JSONDecodeError:
                parsed_tags = []
        else:
            parsed_tags = raw_tags
        tags = parsed_tags if isinstance(parsed_tags, list) else []
        search_text = " ".join(
            str(part).strip()
            for part in (
                values.get("title", ""),
                values.get("content", ""),
                " ".join(str(tag) for tag in tags),
            )
            if str(part).strip()
        )
        search_text = " ".join(search_text.lower().split())
        connection.execute(
            "INSERT INTO notes_fts (id, saved_search_text) VALUES (?, ?)",
            (values["id"], search_text),
        )


def evaluate_binding(connection: sqlite3.Connection, binding: dict[str, Any]) -> bool:
    where = binding["where"]
    clauses = " AND ".join(f'"{column}" = ?' for column in where)
    query = f'SELECT * FROM "{binding["table"]}" WHERE {clauses}'
    cursor = connection.execute(query, list(where.values()))
    rows = cursor.fetchall()
    if len(rows) != binding.get("expected_count", 1):
        return False
    expected_fields = binding.get("expected_fields", {})
    if not expected_fields:
        return True
    columns = [item[0] for item in cursor.description]
    for row in rows:
        record = dict(zip(columns, row))
        if any(record.get(key) != value for key, value in expected_fields.items()):
            return False
    return True


def build_snapshot(
    appworld_root: Path, family: dict[str, Any], directory: Path
) -> tuple[str, dict[str, sqlite3.Connection]]:
    directory.mkdir(parents=True, exist_ok=True)
    apps = family["fixture"]["apps"]
    connections: dict[str, sqlite3.Connection] = {}
    for app in apps:
        source = appworld_root / "data" / "base_dbs" / f"{app}.db"
        target = directory / f"{app}.db"
        shutil.copy2(source, target)
        connections[app] = sqlite3.connect(target)
    try:
        for row in family["fixture"]["rows"]:
            insert_fixture_row(connections[row["app"]], row)
        for connection in connections.values():
            connection.commit()
        for check in family["fixture"]["initial_checks"]:
            if not evaluate_binding(connections[check["app"]], check):
                raise QualificationError(
                    f'Initial fixture check failed for family {family["family_id"]}.'
                )
        state_hash = digest(
            {app: file_sha256(directory / f"{app}.db") for app in sorted(apps)}
        )
        return state_hash, connections
    except Exception:
        for connection in connections.values():
            connection.close()
        raise


def resource_set(constraint: dict[str, Any]) -> set[str]:
    return set(
        constraint["read_resources"]
        + constraint["write_resources"]
        + constraint["prerequisite_resources"]
    )


def validate_constraint(constraint: dict[str, Any]) -> None:
    required = {
        "constraint_id", "role", "semantic_description", "evaluator_binding",
        "affected_entities", "read_resources", "write_resources",
        "prerequisite_resources",
    }
    missing = required - set(constraint)
    if missing:
        raise QualificationError(f"ConstraintSpec is missing fields: {sorted(missing)}")
    if constraint["role"] not in {"TARGET", "NON_TARGET"}:
        raise QualificationError("Constraint role must be TARGET or NON_TARGET.")
    if not constraint["semantic_description"].strip():
        raise QualificationError("Constraint semantic description is empty.")
    if not constraint["affected_entities"]:
        raise QualificationError("Constraint has no affected entity binding.")


def validate_family(
    family: dict[str, Any], appworld_root: Path, scratch_root: Path
) -> dict[str, Any]:
    arms = family["arms"]
    if {arm["coupling_level"] for arm in arms} != {"INDEPENDENT", "LOW", "HIGH"}:
        raise QualificationError("Every family must contain independent, low, and high arms.")
    target_hashes: set[str] = set()
    target_footprints: set[str] = set()
    constraint_counts: set[int] = set()
    matching_hashes: set[str] = set()
    update_interface_hashes: set[str] = set()
    exposure_by_level: dict[str, int] = {}
    evaluator_hashes: dict[str, str] = {}
    graph_hashes: dict[str, str] = {}
    arm_instruction_hashes: dict[str, str] = {}
    instruction_byte_lengths: set[int] = set()
    instruction_word_counts: set[int] = set()
    target_ids: set[str] = set()
    all_non_target_initially_satisfied = True

    state_hash, connections = build_snapshot(
        appworld_root, family, scratch_root / family["family_id"]
    )
    try:
        for arm in arms:
            instruction = arm.get("task_instruction", "")
            if not instruction.startswith(family["target_instruction"] + " "):
                raise QualificationError(
                    "Agent-visible arm instruction must preserve the exact target prefix."
                )
            lowered_instruction = instruction.lower()
            forbidden_labels = ("independent", "coupled", "topology")
            if any(label in lowered_instruction for label in forbidden_labels):
                raise QualificationError("Agent-visible instruction leaks a topology label.")
            instruction_tokens = {
                token.strip(".,:;!?()[]{}").lower()
                for token in instruction.split()
            }
            if instruction_tokens & {"low", "high"}:
                raise QualificationError("Agent-visible instruction leaks a coupling level.")
            arm_instruction_hashes[arm["arm_id"]] = digest(instruction)
            instruction_byte_lengths.add(len(instruction.encode("utf-8")))
            instruction_word_counts.add(len(instruction.split()))

            constraints = arm["constraints"]
            for constraint in constraints:
                validate_constraint(constraint)
            targets = [item for item in constraints if item["role"] == "TARGET"]
            if len(targets) != 1:
                raise QualificationError("Each arm must have exactly one target constraint.")
            target = targets[0]
            non_targets = [item for item in constraints if item["role"] == "NON_TARGET"]
            if len(non_targets) != 2:
                raise QualificationError("Each arm must have exactly two non-target constraints.")
            target_ids.add(target["constraint_id"])
            target_hashes.add(digest(target["semantic_description"]))
            target_footprints.add(digest(sorted(resource_set(target))))
            constraint_counts.add(len(constraints))
            matching_hashes.add(digest(arm["matching"]))
            update_interface_hashes.add(digest(family["update_interface"]))

            target_resources = resource_set(target)
            shared_resources: set[str] = set()
            for non_target in non_targets:
                shared_resources.update(target_resources & resource_set(non_target))
                binding = non_target["evaluator_binding"]
                if not evaluate_binding(connections[binding["app"]], binding):
                    all_non_target_initially_satisfied = False
            observed_exposure = len(shared_resources)
            declared_exposure = arm["structure"]["shared_resource_exposure_count"]
            if observed_exposure != declared_exposure:
                raise QualificationError(
                    f"Declared exposure does not match resource bindings in {arm['arm_id']}."
                )
            exposure_by_level[arm["coupling_level"]] = observed_exposure

            constraint_ids = {item["constraint_id"] for item in constraints}
            for edge in arm["edges"]:
                if edge["edge_type"] not in ALLOWED_EDGE_TYPES:
                    raise QualificationError("Forbidden or post-hoc edge type.")
                if edge["source"] not in constraint_ids or edge["target"] not in constraint_ids:
                    raise QualificationError("Graph edge references an unknown constraint.")
                if not edge["resource_witnesses"]:
                    raise QualificationError("Graph edge has no static resource witness.")
            evaluator_hashes[arm["arm_id"]] = digest(
                [item["evaluator_binding"] for item in constraints]
            )
            graph_hashes[arm["arm_id"]] = digest(arm["edges"])
    finally:
        for connection in connections.values():
            connection.close()

    if len(target_ids) != 1 or len(target_hashes) != 1 or len(target_footprints) != 1:
        raise QualificationError("Target identity, semantics, or footprint changed across arms.")
    if len(constraint_counts) != 1 or len(matching_hashes) != 1:
        raise QualificationError("Constraint count or matching budget changed across arms.")
    if len(update_interface_hashes) != 1:
        raise QualificationError("Persistent update exposure interface changed across arms.")
    if len(set(arm_instruction_hashes.values())) != 3:
        raise QualificationError(
            "Every topology arm must expose a distinct dependency context to the agent."
        )
    if len(instruction_byte_lengths) != 1 or len(instruction_word_counts) != 1:
        raise QualificationError(
            "Agent-visible arm instructions are not byte- and word-count matched."
        )
    if exposure_by_level != {"INDEPENDENT": 0, "LOW": 1, "HIGH": 2}:
        raise QualificationError("Coupling levels are not the preregistered 0/1/2 exposure ladder.")
    if not all_non_target_initially_satisfied:
        raise QualificationError("A non-target constraint is not satisfied in the initial fixture.")

    return {
        "family_id": family["family_id"],
        "category": family["category"],
        "arm_count": len(arms),
        "coupling_levels": ["INDEPENDENT", "LOW", "HIGH"],
        "shared_resource_exposure": exposure_by_level,
        "constraint_count": next(iter(constraint_counts)),
        "target_constraint_id_sha256": digest(next(iter(target_ids))),
        "target_instruction_sha256": digest(family["target_instruction"]),
        "arm_instruction_sha256_by_arm": arm_instruction_hashes,
        "instruction_byte_length": next(iter(instruction_byte_lengths)),
        "instruction_word_count": next(iter(instruction_word_counts)),
        "target_semantics_sha256": next(iter(target_hashes)),
        "target_resource_footprint_sha256": next(iter(target_footprints)),
        "matching_sha256": next(iter(matching_hashes)),
        "update_interface_sha256": next(iter(update_interface_hashes)),
        "initial_snapshot_sha256": state_hash,
        "evaluator_sha256_by_arm": evaluator_hashes,
        "graph_sha256_by_arm": graph_hashes,
        "residual_confounds": family["residual_confounds"],
        "initial_non_target_constraints_satisfied": all_non_target_initially_satisfied,
    }


def compile_artifacts(
    appworld_root: Path, bundle_path: Path, output_root: Path
) -> dict[str, Any]:
    spec = load_protected_spec(bundle_path)
    if spec["object_id"] != OBJECT_ID or spec["compiler_id"] != COMPILER_ID:
        raise QualificationError("Protected specification belongs to another scientific object.")
    forbidden = FORBIDDEN_OUTCOME_KEYS & set(_walk_keys(spec))
    if forbidden:
        raise QualificationError(
            f"Protected compiler input contains outcome keys: {sorted(forbidden)}"
        )
    source = validate_source(appworld_root)
    if spec["appworld_repo_sha"] != source["appworld_repo_sha"]:
        raise QualificationError("Protected family specification targets another AppWorld SHA.")

    with tempfile.TemporaryDirectory(prefix="appworld-constraint-compiler-") as temp:
        family_summaries = [
            validate_family(family, appworld_root, Path(temp))
            for family in spec["families"]
        ]

    categories = {item["category"] for item in family_summaries}
    pass_conditions = {
        "at_least_10_families": len(family_summaries) >= 10,
        "at_most_20_families": len(family_summaries) <= 20,
        "file_gmail_covered": "FILE_GMAIL" in categories,
        "todo_note_file_covered": "TODO_NOTE_FILE" in categories,
        "all_have_independent_coupled_three_level": all(
            item["arm_count"] == 3
            and item["shared_resource_exposure"]
            == {"INDEPENDENT": 0, "LOW": 1, "HIGH": 2}
            for item in family_summaries
        ),
        "target_semantics_invariant": True,
        "agent_visible_structural_context": all(
            len(set(item["arm_instruction_sha256_by_arm"].values())) == 3
            and item["instruction_byte_length"] > 0
            and item["instruction_word_count"] > 0
            for item in family_summaries
        ),
        "exact_update_interface_replayable": True,
        "constraint_count_matched": len(
            {item["constraint_count"] for item in family_summaries}
        ) == 1,
        "no_evaluator_leakage": True,
        "outcome_blind_graph": True,
        "static_topology_diff_complete": all(
            bool(item["residual_confounds"]) for item in family_summaries
        ),
        "all_non_target_constraints_initially_satisfied": all(
            item["initial_non_target_constraints_satisfied"]
            for item in family_summaries
        ),
    }
    verdict = (
        "PRE_F0_5_PASS"
        if all(pass_conditions.values())
        else "PRE_F0_5_FAIL_CONSTRUCT_INVALID"
    )

    family_manifest = {
        "schema_version": "appworld-constraint-matched-family-manifest-v1",
        "generated_at": spec["generated_at"],
        "object_id": OBJECT_ID,
        "compiler_id": COMPILER_ID,
        "classification": "BENCHMARK_DERIVED_CONTROLLED_EXTENSION",
        "protected_detail_bundle": bundle_path.name,
        "protected_detail_bundle_sha256": file_sha256(bundle_path),
        "family_count": len(family_summaries),
        "families": family_summaries,
        "scientific_outcomes_observed": 0,
    }
    topology_diffs: list[dict[str, Any]] = []
    for family, summary in zip(spec["families"], family_summaries, strict=True):
        arms = {arm["coupling_level"]: arm for arm in family["arms"]}
        for left, right in combinations(("INDEPENDENT", "LOW", "HIGH"), 2):
            topology_diffs.append({
                "family_id": family["family_id"],
                "left": left,
                "right": right,
                "intended_structural_difference": {
                    "shared_resource_exposure_count": [
                        arms[left]["structure"]["shared_resource_exposure_count"],
                        arms[right]["structure"]["shared_resource_exposure_count"],
                    ],
                    "graph_sha256": [
                        summary["graph_sha256_by_arm"][arms[left]["arm_id"]],
                        summary["graph_sha256_by_arm"][arms[right]["arm_id"]],
                    ],
                },
                "target_invariant_fields": [
                    "target_constraint_id", "target_semantics",
                    "target_resource_footprint", "persistent_update_interface",
                    "constraint_count", "task_complexity", "tool_budget",
                    "expected_task_length", "backbone_slot", "harness_slot",
                ],
                "initial_snapshot_sha256": summary["initial_snapshot_sha256"],
                "residual_confounds": family["residual_confounds"],
                "claim_language":
                    "EXACT_UPDATE_ARTIFACT_PLUS_MATCHED_TOPOLOGY_CONTEXT",
            })

    contract = {
        "schema_version": "appworld-constraint-compiler-contract-v1",
        "generated_at": spec["generated_at"],
        "object_id": OBJECT_ID,
        "compiler_id": COMPILER_ID,
        "stage": "PRE_F0_5_STATIC_COMPILER",
        "outcome_read_authority": False,
        "provider_authority": False,
        "gpu_authority": False,
        "scientific_episode_authority": False,
        "allowed_edge_types": sorted(ALLOWED_EDGE_TYPES),
        "forbidden_edge_sources": [
            "embedding_similarity", "llm_semantic_relatedness",
            "observed_co_failure", "observed_regression", "post_hoc_graph_edit",
        ],
        "primary_structural_variable":
            "MUTABLE_RESOURCE_OR_PREREQUISITE_EXPOSURE",
        "structural_context_intervention":
            "AGENT_VISIBLE_MATCHED_NON_TARGET_OBLIGATION_BINDING",
        "evaluator_only_topology_change_forbidden": True,
        "instruction_matching": ["UTF8_BYTE_LENGTH", "WHITESPACE_WORD_COUNT"],
        "primary_update_surface": "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
        "topology_claim_language":
            "EXACT_UPDATE_ARTIFACT_PLUS_MATCHED_TOPOLOGY_CONTEXT",
        "protected_material_policy":
            "Exact text, field bindings, fixtures, and evaluators stay encrypted.",
    }
    constraint_schema = {
        "schema_version": "appworld-constraint-spec-schema-v1",
        "object_id": OBJECT_ID,
        "required_fields": [
            "constraint_id", "role", "semantic_description",
            "evaluator_binding", "affected_entities", "read_resources",
            "write_resources", "prerequisite_resources",
        ],
        "semantic_grouping_rule":
            "One independently interpretable obligation may bind several raw checks.",
        "raw_assertion_is_scientific_constraint": False,
        "outcome_blind": True,
        "protected_full_instances": bundle_path.name,
    }
    graph_schema = {
        "schema_version": "appworld-resource-graph-schema-v1",
        "object_id": OBJECT_ID,
        "node_type": "SCIENTIFIC_CONSTRAINT",
        "edge_types": sorted(ALLOWED_EDGE_TYPES),
        "edge_witness_required": True,
        "primary_variable":
            "SHARED_MUTABLE_RESOURCE_OR_PREREQUISITE_EXPOSURE_COUNT",
        "motif_status": "SECONDARY_SUMMARY_ONLY",
        "outcome_blind": True,
    }
    topology_payload = {
        "schema_version": "appworld-topology-arm-diff-v1",
        "generated_at": spec["generated_at"],
        "object_id": OBJECT_ID,
        "comparison_count": len(topology_diffs),
        "comparisons": topology_diffs,
        "forbidden_claim": "SAME_BASE_STATE_ACROSS_TOPOLOGY_ARMS",
        "allowed_claim":
            "EXACT_SAME_UPDATE_ARTIFACT_PLUS_MATCHED_TOPOLOGY_CONTEXT",
    }
    source_manifest = {
        "schema_version": "appworld-constraint-source-revision-manifest-v1",
        "generated_at": spec["generated_at"],
        "object_id": OBJECT_ID,
        **source,
        "protected_compiler_bundle": {
            "path": str(bundle_path.relative_to(output_root.parent)),
            "sha256": file_sha256(bundle_path),
            "plaintext_spec_sha256": digest(spec),
            "replay":
                "Decrypt locally with pinned AppWorld; never redistribute extracted plaintext.",
        },
        "public_redistribution_boundary":
            "Protected AppWorld material and detailed derivatives remain encrypted.",
        "scientific_outcomes_observed": 0,
    }
    qualification = {
        "schema_version": "appworld-constraint-compiler-qualification-v1",
        "generated_at": spec["generated_at"],
        "object_id": OBJECT_ID,
        "compiler_id": COMPILER_ID,
        "verdict": verdict,
        "family_count": len(family_summaries),
        "category_counts": {
            category: sum(
                item["category"] == category for item in family_summaries
            )
            for category in sorted(categories)
        },
        "independent_family_count": len(family_summaries),
        "coupled_family_count": len(family_summaries),
        "three_level_family_count": len(family_summaries),
        "pass_conditions": pass_conditions,
        "scientific_outcomes_observed": 0,
        "provider_calls": 0,
        "gpu_runs": 0,
        "f0_authority_opened": verdict == "PRE_F0_5_PASS",
    }

    outputs = {
        "agent-constraint-externality-appworld-compiler-contract-20260831.json":
            contract,
        "agent-constraint-externality-constraint-schema-20260831.json":
            constraint_schema,
        "agent-constraint-externality-resource-graph-schema-20260831.json":
            graph_schema,
        "agent-constraint-externality-matched-family-manifest-20260831.json":
            family_manifest,
        "agent-constraint-externality-topology-arm-diff-20260831.json":
            topology_payload,
        "agent-constraint-externality-appworld-source-manifest-20260831.json":
            source_manifest,
        "agent-constraint-externality-appworld-compiler-qualification-20260831.json":
            qualification,
    }
    for name, payload in outputs.items():
        write_json(output_root / name, payload)

    manifest_files = {
        str((output_root / name).relative_to(output_root.parent)): {
            "sha256": file_sha256(output_root / name),
            "bytes": (output_root / name).stat().st_size,
        }
        for name in outputs
    }
    manifest_files[str(bundle_path.relative_to(output_root.parent))] = {
        "sha256": file_sha256(bundle_path),
        "bytes": bundle_path.stat().st_size,
    }
    compilation_manifest = {
        "schema_version":
            "appworld-constraint-compiler-artifact-manifest-v1",
        "generated_at": spec["generated_at"],
        "object_id": OBJECT_ID,
        "compiler_id": COMPILER_ID,
        "verdict": verdict,
        "files": manifest_files,
        "scientific_outcomes_observed": 0,
        "authority": {
            "provider": False,
            "gpu": False,
            "f0": verdict == "PRE_F0_5_PASS",
            "p1": False,
            "method": False,
            "paper_claim": False,
        },
    }
    write_json(
        output_root
        / "agent-constraint-externality-appworld-compiler-manifest-20260831.json",
        compilation_manifest,
    )
    return qualification


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appworld-root", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("generated"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    qualification = compile_artifacts(
        args.appworld_root.resolve(),
        args.bundle.resolve(),
        args.output_root.resolve(),
    )
    print(json.dumps(
        qualification, ensure_ascii=False, indent=2, sort_keys=True
    ))


if __name__ == "__main__":
    main()
