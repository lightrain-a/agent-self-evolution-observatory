from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_state_materialization import (
    canonical_selected_scores,
    compile_comp_state,
    compile_scope_matched_control,
    compile_score_only_control,
    compiler_scope,
    materialize_actor_visible_state,
    selected_evidence,
)

BASE = "# Base Spreadsheet Skill\n\nUse the workbook tools carefully.\n"


def eight_units():
    texts_scores = [
        ("load_workbook('input.xlsx'); ws['A1'] = 1; wb.save('output.xlsx')", 0.0),
        ("load_workbook('input.xlsx'); tool error: stale worksheet name", 0.0),
        ("load_workbook('input.xlsx'); ws['B2'] = 2; wb.save('output.xlsx'); load_workbook('output.xlsx'); verify expected == output", 1.0),
        ("load_workbook('input.xlsx'); inspect sheetnames only", 0.0),
        ("load_workbook('input.xlsx'); ws['C3'] = 3; wb.save('output.xlsx'); load_workbook('output.xlsx'); verified expected match", 1.0),
        ("load_workbook('input.xlsx'); tool error then second attempt corrected; ws['D4'] = 4; wb.save('output.xlsx'); load_workbook('output.xlsx'); verify expected match", 0.0),
        ("load_workbook('input.xlsx'); ws['E5'] = 5; wb.save('output.xlsx')", 0.0),
        ("load_workbook('input.xlsx'); ws['F6'] = 6; wb.save('output.xlsx'); load_workbook('output.xlsx'); verified expected match", 1.0),
    ]
    return tuple(selected_evidence(text, score) for text, score in texts_scores)


class BridgeV4R2StateMaterializationTests(unittest.TestCase):
    def test_compilation_is_byte_deterministic_for_identical_selected_evidence(self) -> None:
        units = eight_units()
        a, da = compile_comp_state(base_skill_markdown=BASE, units=units)
        b, db = compile_comp_state(base_skill_markdown=BASE, units=units)
        self.assertEqual(a.skill_markdown, b.skill_markdown)
        self.assertEqual(a.skill_sha256, b.skill_sha256)
        self.assertEqual([d.diagnosis_sha256 for d in da], [d.diagnosis_sha256 for d in db])

    def test_score_only_control_is_text_blind(self) -> None:
        units = eight_units()
        scores = canonical_selected_scores(units)
        first = compile_score_only_control(base_skill_markdown=BASE, selected_scores=scores)
        second = compile_score_only_control(base_skill_markdown=BASE, selected_scores=list(scores))
        self.assertEqual(first.skill_sha256, second.skill_sha256)

    def test_scope_matched_control_receives_only_scores_and_scalar_k(self) -> None:
        units = eight_units()
        comp, diagnoses = compile_comp_state(base_skill_markdown=BASE, units=units)
        del comp
        k = compiler_scope(diagnoses)
        scores = canonical_selected_scores(units)
        a = compile_scope_matched_control(base_skill_markdown=BASE, selected_scores=scores, rendered_block_count=k)
        b = compile_scope_matched_control(base_skill_markdown=BASE, selected_scores=tuple(scores), rendered_block_count=k)
        self.assertEqual(a.skill_sha256, b.skill_sha256)

    def test_materialized_actor_directory_contains_only_exact_skill_bytes(self) -> None:
        units = eight_units()
        compiled, diagnoses = compile_comp_state(base_skill_markdown=BASE, units=units)
        diagnosis_bundle_sha = hashlib.sha256(
            json.dumps([d.diagnosis_sha256 for d in diagnoses], separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            state_root = Path(td) / "state"
            receipt = materialize_actor_visible_state(
                state_root=state_root,
                arm="FF4_COMP",
                compiled=compiled,
                source_evidence_sha256s=[u.evidence_sha256 for u in units],
                selected_scores=canonical_selected_scores(units),
                diagnosis_bundle_sha256=diagnosis_bundle_sha,
                rendered_block_count=compiler_scope(diagnoses),
            )
            skill_dir = Path(receipt["actor_skill_source"])
            skill_path = skill_dir / "SKILL.md"
            self.assertEqual(sorted(p.name for p in skill_dir.iterdir()), ["SKILL.md"])
            self.assertEqual(skill_path.read_text(encoding="utf-8"), compiled.skill_markdown)
            self.assertEqual(hashlib.sha256(skill_path.read_bytes()).hexdigest(), compiled.skill_sha256)
            self.assertFalse(receipt["raw_typed_diagnosis_actor_visible"])
            self.assertFalse(receipt["hidden_experiment_metadata_actor_visible"])
            self.assertEqual(receipt["post_compile_model_calls"], 0)
            self.assertEqual(receipt["post_compile_renderer"], "NONE")
            self.assertTrue((state_root / "state_receipt.json").is_file())
            self.assertFalse((skill_dir / "state_receipt.json").exists())

    def test_materialization_refuses_overwrite(self) -> None:
        units = eight_units()
        compiled, diagnoses = compile_comp_state(base_skill_markdown=BASE, units=units)
        with tempfile.TemporaryDirectory() as td:
            state_root = Path(td) / "state"
            kwargs = dict(
                state_root=state_root,
                arm="W_COMP",
                compiled=compiled,
                source_evidence_sha256s=[u.evidence_sha256 for u in units],
                selected_scores=canonical_selected_scores(units),
                diagnosis_bundle_sha256=None,
                rendered_block_count=compiler_scope(diagnoses),
            )
            materialize_actor_visible_state(**kwargs)
            with self.assertRaises(FileExistsError):
                materialize_actor_visible_state(**kwargs)

    def test_selected_evidence_sha_is_load_bearing(self) -> None:
        unit = selected_evidence("load_workbook('input.xlsx')", 0.0)
        broken = type(unit)(unit.evidence_text, unit.selected_score, "0" * 64)
        with self.assertRaisesRegex(ValueError, "SHA drift"):
            broken.validate()


if __name__ == "__main__":
    unittest.main()
