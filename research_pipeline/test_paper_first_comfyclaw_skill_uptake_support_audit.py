from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_comfyclaw_skill_uptake_support_audit import (
    CANDIDATE_ID, OFFICIAL_COMMIT, PHENOMENON_ID, SOURCE_REF, TRACKED_FILE_COUNT, TRACKED_MANIFEST_SHA256,
    REQUIRED_UNIT, REOPEN_CONDITION, _unit_level_candidates, build_support_hold, validate_support_audit, validate_support_hold,
)
from .paper_first_problem_search_portfolio import _fresh_phenomenon_held_keys
from .paper_first_search_portfolio_design_adjudication import _fresh_phenomenon_support_hold_rows


class ComfyClawSkillUptakeSupportAuditTest(unittest.TestCase):
    def audit(self)->dict:
        return {"schema_version":"1.0","status":"HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT","candidate_id":CANDIDATE_ID,"source_ref":SOURCE_REF,"phenomenon_id":PHENOMENON_ID,"official_commit":OFFICIAL_COMMIT,"tracked_file_count":TRACKED_FILE_COUNT,"tracked_manifest_sha256":TRACKED_MANIFEST_SHA256,"github_release_count":0,"github_release_asset_count":0,"paper_run_unit_candidates":[],"summary_docs_present":True,"runtime_log_capability_present":True,"required_unit":REQUIRED_UNIT,"reopen_only_if":REOPEN_CONDITION,"why_hold":"paper-run units unavailable","scientific_authority":False}

    def test_release_inventory_classifier_separates_code_from_unit_data(self)->None:
        files=["docs/RESULTS.md","comfyclaw/harness.py","scripts/run.py","paper-data/run-1.jsonl","foo/results/x.json"]
        self.assertEqual(_unit_level_candidates(files),["foo/results/x.json","paper-data/run-1.jsonl"])

    def test_hold_is_reopenable_exact_evidence_not_dead_end(self)->None:
        audit=self.audit();self.assertEqual(validate_support_audit(audit),[])
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);audit_path=root/"audit.json";audit_path.write_text(json.dumps(audit));sha=hashlib.sha256(audit_path.read_bytes()).hexdigest();hold=build_support_hold(audit=audit,audit_file_sha256=sha);hold_path=root/"comfyclaw-fresh-phenomenon-support-hold-test.json";hold_path.write_text(json.dumps(hold))
            self.assertEqual(validate_support_hold(hold,audit_path=audit_path),[])
            # Loader requires the audit path to be generated-relative, so construct the equivalent memory row contract directly here.
            memory={"hold_objects":[{"dead_end_certified":False,"fresh_phenomenon_hold":{"source_ref":SOURCE_REF,"evidence_sha256":PHENOMENON_ID,"scientific_authority":False}}]}
            self.assertEqual(_fresh_phenomenon_held_keys(memory),{(SOURCE_REF,PHENOMENON_ID)})
        self.assertEqual(hold["status"],"HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT");self.assertFalse(hold["scientific_authority"])
        self.assertTrue(all(v is False for v in hold["authority"].values()))


if __name__=="__main__":unittest.main()
