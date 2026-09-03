from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
PARENT_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-20260831.bundle"
OUTPUT_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v2-20260902.bundle"
AUDIT_OUTPUT = GENERATED / "agent-constraint-externality-capability-substrate-v2-contract-20260902.json"
SUBSTRATE_ID = "ACE-APPWORLD-CAPABILITY-SUBSTRATE-V2-20260902"


def _canonical_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_v2_bundle() -> dict[str, Any]:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import bundle_file_path_to_content, pack_bundle

    contents = bundle_file_path_to_content(str(PARENT_BUNDLE), PASSWORD, SALT)
    spec = json.loads(contents["compiler_spec/family_spec.json"])
    if spec.get("object_id") != OBJECT_ID:
        raise RuntimeError("Protected family spec object mismatch.")
    changed_families: list[str] = []
    for family in spec["families"]:
        if family["category"] != "TODO_NOTE_FILE":
            continue
        before = family["target_instruction"]
        after = before.replace("Use todo ", "Use Inbox todo ", 1)
        if before == after:
            raise RuntimeError(f"TNF target instruction locator replacement failed for {family['family_id']}.")
        family["target_instruction"] = after
        for arm in family["arms"]:
            updated = arm["task_instruction"].replace("Use todo ", "Use Inbox todo ", 1)
            if updated == arm["task_instruction"]:
                raise RuntimeError(f"TNF arm instruction locator replacement failed for {arm['arm_id']}.")
            arm["task_instruction"] = updated
        changed_families.append(family["family_id"])
    if len(changed_families) != 6:
        raise RuntimeError("Capability substrate V2 must update exactly six TNF families.")
    spec["substrate_revision"] = SUBSTRATE_ID
    spec["parent_protected_bundle_sha256"] = sha256_file(PARENT_BUNDLE)
    spec["substrate_repairs"] = [
        "AGENT_VISIBLE_TODO_INBOX_LOCATOR",
        "RUNTIME_SUPERVISOR_IDENTITY_BOUND_TO_FIXTURE_OWNER_USER_99",
        "API_NATIVE_FIXTURE_DEFAULTS",
        "SIMPLE_NOTE_FTS_SYNC",
        "SEMANTIC_FILE_GMAIL_TARGET_EVALUATOR",
    ]

    rebuild_script = contents["compiler_spec/rebuild_spec.py"]
    old = 'f"Read note {source_note[1]}. Use todo {source_todo[1]} as the file name "'
    new = 'f"Read note {source_note[1]}. Use Inbox todo {source_todo[1]} as the file name "'
    if old not in rebuild_script:
        raise RuntimeError("Protected rebuild script TNF instruction template not found.")
    rebuild_script = rebuild_script.replace(old, new, 1)

    with tempfile.TemporaryDirectory(prefix="ace-substrate-v2-") as directory:
        root = Path(directory)
        for relative, content in contents.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if relative == "compiler_spec/family_spec.json":
                target.write_text(json.dumps(spec, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            elif relative == "compiler_spec/rebuild_spec.py":
                target.write_text(rebuild_script, encoding="utf-8")
            else:
                if isinstance(content, bytes):
                    target.write_bytes(content)
                else:
                    target.write_text(content, encoding="utf-8")
        packed = pack_bundle(
            str(OUTPUT_BUNDLE),
            str(root),
            ["compiler_spec"],
            PASSWORD,
            SALT,
            include_license=False,
        )
    if "compiler_spec/family_spec.json" not in packed or "compiler_spec/rebuild_spec.py" not in packed:
        raise RuntimeError("Capability substrate V2 bundle is incomplete.")

    replay = bundle_file_path_to_content(
        str(OUTPUT_BUNDLE), PASSWORD, SALT, include_file_paths=["compiler_spec/family_spec.json"]
    )
    replay_spec = json.loads(replay["compiler_spec/family_spec.json"])
    if replay_spec.get("substrate_revision") != SUBSTRATE_ID:
        raise RuntimeError("Capability substrate V2 replay revision mismatch.")
    for family in replay_spec["families"]:
        if family["category"] == "TODO_NOTE_FILE":
            if "Use Inbox todo " not in family["target_instruction"]:
                raise RuntimeError("TNF V2 instruction is not agent-visible locator complete.")
            if any("Use Inbox todo " not in arm["task_instruction"] for arm in family["arms"]):
                raise RuntimeError("TNF V2 arm instruction is not locator complete.")

    audit: dict[str, Any] = {
        "schema_version": "ace-appworld-capability-substrate-v2-contract-v1",
        "object_id": OBJECT_ID,
        "substrate_id": SUBSTRATE_ID,
        "status": "CAPABILITY_SUBSTRATE_V2_STATIC_REPAIR_READY",
        "parent_bundle": {
            "path": str(PARENT_BUNDLE.relative_to(ROOT)),
            "sha256": sha256_file(PARENT_BUNDLE),
        },
        "active_bundle": {
            "path": str(OUTPUT_BUNDLE.relative_to(ROOT)),
            "sha256": sha256_file(OUTPUT_BUNDLE),
        },
        "changed_family_ids": changed_families,
        "repairs": {
            "todo_locator": "ALL_TNF_TARGET_AND_ARM_INSTRUCTIONS_EXPLICITLY_NAME_INBOX",
            "note_discoverability": "SIMPLE_NOTE_FIXTURE_MUST_BE_PRESENT_IN_NOTES_FTS",
            "supervisor_identity": "USER_99_AARON_BURTON_MATCHES_ALL_FIXTURE_OWNERS",
            "fixture_api_schema": "RAW_FIXTURES_POPULATE_APPWORLD_API_NATIVE_DEFAULT_FIELDS",
            "fg_target_evaluator": "RECIPIENT_PLUS_TWO_ATTACHMENT_NAMES_AND_BYTES_PLUS_SUBJECT",
        },
        "unchanged_scientific_design": {
            "family_count": 12,
            "arms_per_family": 3,
            "constraint_count": 3,
            "coupling_levels": [0, 1, 2],
            "tool_call_cap": 12,
            "capability_thresholds": "UNCHANGED",
            "update_surface": "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
            "backbone": "NOT_CHANGED_BY_SUBSTRATE_REPAIR",
        },
        "provider_requests": 0,
        "f0_scientific_outcomes_observed": 0,
        "protected_plaintext_persisted": False,
    }
    audit["content_sha256"] = sha256_value(audit)
    _canonical_write(AUDIT_OUTPUT, audit)
    return audit


def main() -> None:
    audit = build_v2_bundle()
    print(json.dumps({
        "status": audit["status"],
        "active_bundle": audit["active_bundle"],
        "changed_family_count": len(audit["changed_family_ids"]),
        "provider_requests": audit["provider_requests"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
