from pathlib import Path
import unittest

from research_pipeline.e2_r17_state_compiler_bridge import (
    RepairPrimitive,
    compile_skill,
    diagnose,
    extract_visible_signals,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = Path("/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md")
G1 = ROOT / "generated/e2-r17-single-case-constrained-state-micro-20260902/g1_verify/SKILL.md"
G2 = ROOT / "generated/e2-r17-single-case-constrained-state-micro-20260902/g2_complete/SKILL.md"
G3 = ROOT / "generated/e2-r17-single-case-constrained-state-micro-20260902/g3_complete_recover/SKILL.md"


class StateCompilerBridgeTest(unittest.TestCase):
    def test_successful_winner_does_not_receive_generic_repair(self) -> None:
        text = """
        [ASSISTANT] Inspect workbook.
        [ASSISTANT_TOOL_CALL name=python] {"code":"wb=load_workbook('input.xlsx'); ws['B2']=42; wb.save('output.xlsx')"}
        [ASSISTANT_TOOL_CALL name=python] {"code":"check=load_workbook('output.xlsx', data_only=True); assert check['Sheet1']['B2'].value == 42"}
        """
        d = diagnose(extract_visible_signals(evidence_text=text, selected_score=1.0))
        self.assertEqual(d.required_repairs, ())
        self.assertEqual(d.failure_stage, "NO_TYPED_REPAIR")

    def test_incomplete_failed_trajectory_maps_to_completion(self) -> None:
        text = """
        [ASSISTANT_TOOL_CALL name=python] {"code":"wb=load_workbook('input.xlsx'); print(wb.sheetnames); print(ws.max_row)"}
        [TOOL] ['Sheet1']
        """
        d = diagnose(extract_visible_signals(evidence_text=text, selected_score=0.0))
        self.assertIn(RepairPrimitive.COMPLETE_WORKFLOW, d.required_repairs)
        self.assertEqual(d.failure_stage, "EXECUTION_COMPLETION")

    def test_saved_but_unverified_failure_maps_to_verify(self) -> None:
        text = """
        [ASSISTANT_TOOL_CALL name=python] {"code":"wb=load_workbook('input.xlsx'); ws['B2']=42; wb.save('output.xlsx')"}
        [TOOL] done
        """
        d = diagnose(extract_visible_signals(evidence_text=text, selected_score=0.0))
        self.assertEqual(d.required_repairs, (RepairPrimitive.VERIFY_OUTPUT,))
        self.assertEqual(d.failure_stage, "OUTPUT_CLOSURE")

    def test_unrecovered_tool_error_adds_recovery(self) -> None:
        text = """
        [ASSISTANT_TOOL_CALL name=python] {"code":"wb=load_workbook('input.xlsx'); ws['B2']=42; wb.save('output.xlsx')"}
        [TOOL] Traceback: SyntaxError
        """
        d = diagnose(extract_visible_signals(evidence_text=text, selected_score=0.0))
        self.assertEqual(
            d.required_repairs,
            (RepairPrimitive.VERIFY_OUTPUT, RepairPrimitive.RECOVER_TOOL_ERROR),
        )

    def test_clean_recovery_does_not_add_recovery_primitive(self) -> None:
        text = """
        [TOOL] Traceback: SyntaxError
        [ASSISTANT] Corrected command; retry.
        [ASSISTANT_TOOL_CALL name=python] {"code":"wb=load_workbook('input.xlsx'); ws['B2']=42; wb.save('output.xlsx')"}
        """
        d = diagnose(extract_visible_signals(evidence_text=text, selected_score=0.0))
        self.assertNotIn(RepairPrimitive.RECOVER_TOOL_ERROR, d.required_repairs)

    def test_compiler_is_byte_deterministic_and_deduplicates(self) -> None:
        base = BASE.read_text(encoding="utf-8")
        d = diagnose(
            extract_visible_signals(
                evidence_text="load_workbook('input.xlsx'); print(ws.max_row)",
                selected_score=0.0,
            )
        )
        a = compile_skill(base_skill_markdown=base, diagnoses=[d, d])
        b = compile_skill(base_skill_markdown=base, diagnoses=[d, d])
        self.assertEqual(a.skill_sha256, b.skill_sha256)
        self.assertEqual(a.skill_markdown, b.skill_markdown)
        self.assertEqual(a.skill_markdown.count("## Completion Loop"), 1)

    def test_compiler_reproduces_current_g1_surface_for_verify_only(self) -> None:
        base = BASE.read_text(encoding="utf-8")
        d = diagnose(
            extract_visible_signals(
                evidence_text="wb=load_workbook('input.xlsx'); ws['B2']=42; wb.save('output.xlsx')",
                selected_score=0.0,
            )
        )
        compiled = compile_skill(base_skill_markdown=base, diagnoses=[d])
        self.assertEqual(compiled.skill_markdown, G1.read_text(encoding="utf-8"))

    def test_compiler_reproduces_current_g2_surface_for_completion(self) -> None:
        base = BASE.read_text(encoding="utf-8")
        d = diagnose(
            extract_visible_signals(
                evidence_text="wb=load_workbook('input.xlsx'); print(wb.sheetnames)",
                selected_score=0.0,
            )
        )
        compiled = compile_skill(base_skill_markdown=base, diagnoses=[d])
        self.assertEqual(compiled.skill_markdown, G2.read_text(encoding="utf-8"))

    def test_compiler_reproduces_current_g3_surface_for_completion_plus_error(self) -> None:
        base = BASE.read_text(encoding="utf-8")
        d = diagnose(
            extract_visible_signals(
                evidence_text="load_workbook('input.xlsx'); print(ws.max_row)\nTraceback: SyntaxError",
                selected_score=0.0,
            )
        )
        compiled = compile_skill(base_skill_markdown=base, diagnoses=[d])
        self.assertEqual(compiled.skill_markdown, G3.read_text(encoding="utf-8"))

    def test_hidden_experiment_labels_are_not_inputs(self) -> None:
        # The public extraction API accepts only learner-visible text + score.
        # This test documents the causal-purity interface: no arm/family/projection
        # argument exists to condition the compiler.
        signals = extract_visible_signals(evidence_text="Traceback: tool error", selected_score=0.0)
        self.assertFalse(hasattr(signals, "arm"))
        self.assertFalse(hasattr(signals, "family"))
        self.assertFalse(hasattr(signals, "projection"))
        self.assertFalse(hasattr(signals, "task_id"))


if __name__ == "__main__":
    unittest.main()
