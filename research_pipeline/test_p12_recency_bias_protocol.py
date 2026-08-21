from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .p12_recency_bias_execute import freeze_calibration, pending_calibration
from .p12_recency_bias_harness import difficulty_calibration_pairs, skill_calibration_bundles
from .p12_recency_bias_protocol import (
    REPAIRED_AUTHORIZATION_FILENAME,
    REVOKED_AUTHORIZATION_V2_FILENAME,
    authorization_ok,
    parse_difficulty_answers,
    parse_single_integer,
    parse_skills,
    provider_archive_payload,
)


class P12RecencyBiasProtocolTest(unittest.TestCase):
    def test_archive_keeps_recovery_fields(self):
        x=provider_archive_payload({"requested_model":"kimi-k3","resolved_model":"kimi-k3","response_id":"r1","status":"completed","text":"7","function_calls":[],"usage":{"total_tokens":9}})
        self.assertEqual(x["response_id"],"r1");self.assertEqual(x["text"],"7");self.assertEqual(x["usage"]["total_tokens"],9)

    def test_integer_parser_prefers_function_and_has_strict_text_fallback(self):
        call={"function_calls":[{"name":"submit_p12_answer","arguments":json.dumps({"answer":7})}],"text":"wrong"}
        self.assertEqual(parse_single_integer(call),(7,"FUNCTION_CALL"))
        self.assertEqual(parse_single_integer({"function_calls":[],"text":"-12"}),(-12,"INTEGER_TEXT_FALLBACK"))
        self.assertEqual(parse_single_integer({"function_calls":[],"text":'{"answer":5}'}),(5,"JSON_TEXT_FALLBACK"))
        with self.assertRaises(ValueError): parse_single_integer({"function_calls":[],"text":"The answer is 5"})

    def test_difficulty_and_skill_parsers_accept_only_exact_structures(self):
        d={"function_calls":[{"name":"submit_p12_difficulty_answers","arguments":json.dumps({"backward_answer":1,"forward_answer":2})}],"text":""}
        self.assertEqual(parse_difficulty_answers(d)[0],{"backward_answer":1,"forward_answer":2})
        s={"function_calls":[],"text":json.dumps({"older_skill_text":"Use a robust global pattern.","newer_skill_text":"Use a recent-window cross-check."})}
        out,source=parse_skills(s);self.assertEqual(source,"JSON_TEXT_FALLBACK");self.assertNotEqual(out["older_skill_text"],out["newer_skill_text"])
        with self.assertRaises(ValueError): parse_skills({"function_calls":[],"text":json.dumps({"older_skill_text":"same","newer_skill_text":"same"})})

    def test_failed_difficulty_receipt_remains_pending_until_explicit_repair(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/"difficulty").mkdir()
            pair=difficulty_calibration_pairs()[0]
            (root/"difficulty"/f"{pair['pair_id']}.json").write_text(json.dumps({"status":"DIFFICULTY_PROTOCOL_FAILURE","pair_id":pair["pair_id"]}))
            self.assertIn(pair["pair_id"],pending_calibration(root)["difficulty"])
            (root/"difficulty-repair-v2").mkdir()
            (root/"difficulty-repair-v2"/f"{pair['pair_id']}.json").write_text(json.dumps({"status":"DIFFICULTY_COMPLETE","pair_id":pair["pair_id"]}))
            self.assertNotIn(pair["pair_id"],pending_calibration(root)["difficulty"])

    def test_v2_revocation_blocks_stale_repaired_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/REPAIRED_AUTHORIZATION_FILENAME).write_text(json.dumps({"entries":[]}))
            (root/REVOKED_AUTHORIZATION_V2_FILENAME).write_text(json.dumps({"status":"EVIDENCE_HARNESS_IMPLEMENTATION_PENDING"}))
            with self.assertRaisesRegex(RuntimeError,"v2 authorization was revoked"):
                authorization_ok(root)

    def test_freeze_calibration_passes_only_with_matched_below_ceiling_difficulty(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/"difficulty").mkdir();(root/"skill-compilation").mkdir()
            for i,pair in enumerate(difficulty_calibration_pairs()):
                (root/"difficulty"/f"{pair['pair_id']}.json").write_text(json.dumps({"status":"DIFFICULTY_COMPLETE","pair_id":pair["pair_id"],"backward_success":i<3,"forward_success":i<3}))
            for bundle in skill_calibration_bundles():
                skills=[{"skill_id":bundle["older_skill_id"],"family":bundle["family"],"timestamp":bundle["older_timestamp"],"text":f"old procedure {bundle['family']}","retrieval_text":f"{bundle['family'].lower()} temporal numeric sequence endpoint extrapolation robust pattern analysis","origin":"DISJOINT_SKILL_CALIBRATION","source_bundle_id":bundle["bundle_id"],"scientific_authority":False},{"skill_id":bundle["newer_skill_id"],"family":bundle["family"],"timestamp":bundle["newer_timestamp"],"text":f"new procedure {bundle['family']}","retrieval_text":f"{bundle['family'].lower()} temporal numeric sequence endpoint extrapolation robust pattern analysis","origin":"DISJOINT_SKILL_CALIBRATION","source_bundle_id":bundle["bundle_id"],"scientific_authority":False}]
                (root/"skill-compilation"/f"{bundle['bundle_id']}.json").write_text(json.dumps({"status":"SKILL_COMPILATION_COMPLETE","bundle_id":bundle["bundle_id"],"skills":skills}))
            out=freeze_calibration(root)
            self.assertEqual(out["status"],"P12_PRE_EVALUATION_LOCK_PASS")
            self.assertTrue(out["evaluation_authorized_by_lock"])
            self.assertEqual(json.loads((root/"rollout-manifest.json").read_text())["unit_count"],96)


if __name__=="__main__": unittest.main()
