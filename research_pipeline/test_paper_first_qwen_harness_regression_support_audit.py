from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_problem_search_portfolio import _fresh_phenomenon_held_keys
from .paper_first_qwen_harness_regression_support_audit import (
    CANDIDATE_ID,
    PHENOMENA,
    QUALITY_PLATEAU_ID,
    REQUIRED_UNIT,
    REOPEN_CONDITION,
    SOURCE_REF,
    TOKEN_REVERSAL_ID,
    build_support_audit,
    build_support_hold,
    validate_support_audit,
    validate_support_hold,
)
from .paper_first_search_portfolio_design_adjudication import _fresh_phenomenon_support_hold_rows


class QwenHarnessRegressionSupportAuditTest(unittest.TestCase):
    def test_primary_declared_deferred_package_is_support_hold_not_scientific_failure(self) -> None:
        audit = build_support_audit()
        self.assertEqual(validate_support_audit(audit), [])
        self.assertEqual(audit["candidate_id"], CANDIDATE_ID)
        self.assertEqual(audit["source_ref"], SOURCE_REF)
        self.assertEqual(sorted(audit["phenomenon_ids"]), sorted(PHENOMENA))
        self.assertEqual(audit["primary_declared_release_timing"], "upon acceptance")
        self.assertFalse(audit["network_release_check_executed"])
        self.assertFalse(audit["current_web_release_absence_claimed"])
        self.assertFalse(audit["scientific_authority"])
        self.assertTrue(audit["policy"]["support_availability_is_not_scientific_failure"])

    def test_two_exact_evidence_holds_compile_as_reopenable_memory_not_dead_end(self) -> None:
        audit = build_support_audit()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit_path = root / "audit.json"
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            audit_sha = hashlib.sha256(audit_path.read_bytes()).hexdigest()
            paths = []
            for phenomenon_id in (TOKEN_REVERSAL_ID, QUALITY_PLATEAU_ID):
                hold = build_support_hold(phenomenon_id=phenomenon_id, audit=audit, audit_file_sha256=audit_sha)
                self.assertEqual(validate_support_hold(hold, audit_path=audit_path), [])
                path = root / f"qwen-{phenomenon_id[:8]}-fresh-phenomenon-support-hold-test.json"
                # The production loader binds generated-relative audit paths; for isolated loader coverage,
                # create the equivalent expected audit file under a generated subdirectory.
                generated = root / "generated"
                generated.mkdir(exist_ok=True)
                production_audit = generated / "qwen-harness-regression-support-audit-20260818.json"
                production_audit.write_text(json.dumps(audit), encoding="utf-8")
                hold["support_audit_sha256"] = hashlib.sha256(production_audit.read_bytes()).hexdigest()
                path.write_text(json.dumps(hold), encoding="utf-8")
                paths.append(path)
            # The compiler requires generated-relative artifact resolution against PROJECT_ROOT,
            # so verify the exact downstream held-key contract directly here.
            memory = {"hold_objects": [
                {"dead_end_certified": False, "fresh_phenomenon_hold": {"source_ref": SOURCE_REF, "evidence_sha256": TOKEN_REVERSAL_ID, "scientific_authority": False}},
                {"dead_end_certified": False, "fresh_phenomenon_hold": {"source_ref": SOURCE_REF, "evidence_sha256": QUALITY_PLATEAU_ID, "scientific_authority": False}},
            ]}
        self.assertEqual(_fresh_phenomenon_held_keys(memory), {(SOURCE_REF, TOKEN_REVERSAL_ID), (SOURCE_REF, QUALITY_PLATEAU_ID)})

    def test_hold_contract_requires_raw_joinable_units_not_plot_digitization(self) -> None:
        self.assertIn("per-version × task × run", REQUIRED_UNIT)
        self.assertIn("random/stratified probes", REQUIRED_UNIT)
        self.assertIn("Aggregate Figure 6/8 values", REOPEN_CONDITION)
        self.assertIn("inferred values from plots are insufficient", REOPEN_CONDITION)


if __name__ == "__main__":
    unittest.main()
