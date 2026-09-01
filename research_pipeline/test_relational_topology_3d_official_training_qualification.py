from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from research_pipeline.relational_topology_training_qualification import (
    CHECKPOINT_REQUIRED,
    CORPUS_FIELDS,
    LICENSE_RECEIPT,
    REGIME_SUPPORT,
    compile_synthetic_corpus,
    derive_example_seed,
    empty_p1_schema,
    replay_matrix,
    require_license,
    validate_checkpoint_record,
    validate_exact_pairing,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/compile_relational_topology_3d_official_training_qualification.py"


class TrainingQualificationCoreTest(unittest.TestCase):
    def test_license_gate_is_exact_and_fail_closed(self) -> None:
        require_license(LICENSE_RECEIPT)
        for value in (None, "", "user_confirmed_research_license_accepted",
                      LICENSE_RECEIPT + " "):
            with self.assertRaises(PermissionError):
                require_license(value)

    def test_content_seed_is_stable_and_content_sensitive(self) -> None:
        a = derive_example_seed("scene-1", "IS-SUPPORT-12", 3)
        self.assertEqual(a, derive_example_seed("scene-1", "IS-SUPPORT-12", 3))
        self.assertNotEqual(a, derive_example_seed("scene-2", "IS-SUPPORT-12", 3))
        self.assertNotEqual(a, derive_example_seed("scene-1", "IS-SUPPORT-14", 3))
        self.assertNotEqual(a, derive_example_seed("scene-1", "IS-SUPPORT-12", 4))

    def test_traversal_and_worker_replay_are_identical(self) -> None:
        scenes = ["s1", "s2", "s3", "s4"]
        for regime in REGIME_SUPPORT:
            replay = replay_matrix(scenes, regime, 24, "a" * 40)
            self.assertTrue(replay["byte_identical"])
            self.assertEqual(len(set(replay["hashes"].values())), 1)

    def test_corpus_schema_support_and_hashes(self) -> None:
        for regime, support in REGIME_SUPPORT.items():
            rows, digest = compile_synthetic_corpus(
                ["s1", "s2"], regime, 24, "b" * 40)
            self.assertEqual({row["relation_count"] for row in rows}, set(support))
            self.assertTrue(all(tuple(row) == CORPUS_FIELDS for row in rows))
            self.assertTrue(all(row["room_type"] == "BEDROOM" for row in rows))
            self.assertTrue(all(row["exact_clip_token_count"] is None for row in rows))
            self.assertTrue(all(row["tokenizer_truncated"] is None for row in rows))
            self.assertRegex(digest, r"^[0-9a-f]{64}$")
            for row in rows:
                body = dict(row)
                expected = body.pop("example_sha256")
                payload = (json.dumps(body, ensure_ascii=False, sort_keys=True,
                                      separators=(",", ":")) + "\n").encode()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), expected)

    def test_oracle_identity_is_exact_only(self) -> None:
        record = {
            "slot_ids": [0, 1], "object_ids": ["a", "b"],
            "object_classes": [1, 2], "objfeat_ids": [4, 5],
            "obj_masks": [True, True],
        }
        self.assertTrue(validate_exact_pairing(record, dict(record)))
        changed = dict(record)
        changed["object_ids"] = ["b", "a"]
        self.assertFalse(validate_exact_pairing(record, changed))
        missing = dict(record)
        missing.pop("slot_ids")
        self.assertFalse(validate_exact_pairing(record, missing))

    def test_checkpoint_schema_and_empty_p1(self) -> None:
        complete = {field: "x" for field in CHECKPOINT_REQUIRED}
        self.assertEqual(validate_checkpoint_record(complete), [])
        complete.pop("rng_state_sha256")
        self.assertEqual(validate_checkpoint_record(complete), ["rng_state_sha256"])
        p1 = empty_p1_schema()
        self.assertFalse(p1["authorized"])
        self.assertEqual(p1["scientific_cases"], [])
        self.assertEqual(p1["scientific_outcomes"], [])


class OfficialTrainingQualificationArtifactTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        temp_root = Path(cls.tmp.name)
        cls.audit = temp_root / "targeted.log"
        cls.audit.write_text(
            "Ran 6 tests in 0.2s\n\nOK\n"
            "Ran 12 tests in 0.4s\n\nOK\n"
        )
        cls.out = temp_root / "out"
        subprocess.run(
            [sys.executable, str(SCRIPT), "--output-dir", str(cls.out),
             "--targeted-audit-log", str(cls.audit)],
            cwd=ROOT, check=True, capture_output=True, text=True)
        cls.load = staticmethod(
            lambda name: json.loads((cls.out / name).read_text()))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_manifest_and_parent_content_addresses(self) -> None:
        manifest = self.load("manifest.json")
        self.assertEqual(manifest["artifact_count"], 25)
        self.assertEqual(manifest["verdict"], "HOLD_USER_LICENSE_CONFIRMATION")
        self.assertEqual(manifest["scientific_gpu_runs"], 0)
        self.assertEqual(manifest["scientific_outcomes"], 0)
        self.assertEqual(manifest["official_training_runs"], 0)
        for name, expected in manifest["artifact_sha256"].items():
            actual = hashlib.sha256((self.out / name).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, name)
        source = self.load("source_manifest.json")
        for relative, expected in source["parent_artifacts"].items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                             expected)

    def test_license_hold_and_zero_authority(self) -> None:
        license_gate = self.load("license_gate.json")
        self.assertEqual(license_gate["status"], "LICENSE_NOT_CONFIRMED")
        self.assertEqual(license_gate["accepted_receipt_exactly"], LICENSE_RECEIPT)
        self.assertIsNone(license_gate["observed_receipt"])
        self.assertFalse(license_gate["licensed_corpus_materialized"])
        authority = self.load("authority.json")
        for key in ("data_license_confirmed", "data_materialization_authority",
                    "gpu_authority_requested", "gpu_authority",
                    "official_instructscene_training", "training_qualification_run",
                    "p1", "p2", "p3"):
            self.assertFalse(authority[key])
        self.assertEqual(authority["port_010"]["status"],
                         "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual(authority["port_010"]["evidence_review"], "BLOCK_BAKE_IN")

    def test_shared_decoder_and_checkpoint_audit(self) -> None:
        decoder = self.load("decoder_audit.json")
        self.assertEqual(decoder["decision"], "SHARED_DECODER_IDENTIFIABLE")
        self.assertTrue(decoder["single_checkpoint_for_both_regimes"])
        self.assertFalse(decoder["sgp_hidden_state_dependency"])
        self.assertEqual(decoder["sg2sc_inputs"],
                         ["objs", "edges", "objfeat_vq_indices", "obj_masks"])
        checkpoint = self.load("official_checkpoint_audit.json")
        self.assertFalse(checkpoint["official_room_checkpoint_available"])
        self.assertIn("UNOFFICIAL", checkpoint["community_room_checkpoints"])
        self.assertTrue(checkpoint["child_adapter_required_before_gpu_qualification"])

    def test_support_and_matching_contract(self) -> None:
        support = self.load("support_intervention.json")
        self.assertEqual(support["regimes"]["IS-SUPPORT-12"]
                         ["relation_count_support"], [1, 2])
        self.assertEqual(support["regimes"]["IS-SUPPORT-14"]
                         ["relation_count_support"], [1, 2, 3, 4])
        self.assertEqual(support["only_intentionally_varied_factor"],
                         "TRAINING_RELATION_COUNT_SUPPORT")
        self.assertIn("shared_SG2SC_decoder", support["matched_exactly"])
        relation = self.load("relation_matching.json")
        self.assertTrue(relation["equal_example_count"])
        self.assertTrue(relation["family_proportions_equal"])
        self.assertEqual(relation["family_proportions"]["IS-SUPPORT-12"],
                         relation["family_proportions"]["IS-SUPPORT-14"])
        token = self.load("token_matching.json")
        self.assertEqual(token["exact_token_counts_materialized"], [])
        self.assertIn("tokenizer_truncated == true",
                      token["primary_scientific_exclusion"])

    def test_synthetic_replay_and_no_science(self) -> None:
        replay = self.load("synthetic_replay.json")
        self.assertEqual(replay["result"], "PASS")
        self.assertFalse(replay["scientific_evidence"])
        for spec in replay["replay_matrix"].values():
            self.assertTrue(spec["byte_identical"])
        dataset = self.load("dataset_manifest.json")
        self.assertEqual(dataset["licensed_rows"], 0)
        self.assertGreater(dataset["synthetic_rows"], 0)

    def test_resume_ledger_reproduction_and_p1_firewall(self) -> None:
        checkpoint = self.load("checkpoint_resume_contract.json")
        self.assertEqual(set(checkpoint["required_fields"]), set(CHECKPOINT_REQUIRED))
        self.assertIn("all RNG", checkpoint["kill_resume_protocol"]["must_restore"])
        self.assertIn("sampler position",
                      checkpoint["kill_resume_protocol"]["must_restore"])
        ledger = self.load("exactly_once_ledger.json")
        self.assertEqual(ledger["status"], "EMPTY_NO_TRAINING_RUN")
        self.assertEqual(ledger["run_claims"], [])
        reproduction = self.load("reproduction_preregistration.json")
        self.assertIn("reference_iRecall", reproduction["bands"]
                      ["relation_level_iRecall_lower"])
        p1 = self.load("p1_empty_schema.json")
        self.assertEqual(p1["status"], "CLOSED_EMPTY_SCHEMA_ONLY")
        self.assertEqual(p1["scientific_cases"], [])
        self.assertEqual(p1["scientific_outcomes"], [])

    def test_novelty_regression_and_adjudication(self) -> None:
        novelty = self.load("novelty_watch.json")
        self.assertEqual(novelty["status"], "NO_MATERIAL_NOVELTY_PIN_DRIFT")
        self.assertEqual(novelty["scenenat_arxiv_revision"], "2601.07218v2")
        self.assertEqual(novelty["scenenat_repo_sha"],
                         "542b82ff0cda4e0350575ca8f1cd5d147529130c")
        debt = self.load("regression_debt.json")
        self.assertEqual(debt["inherited_counts"],
                         {"failures": 1, "errors": 29, "skips": 3})
        self.assertEqual(debt["inherited_authority_impact"],
                         "SCOPED_NON_BLOCKING_DEBT")
        self.assertEqual(debt["targeted_dependency_audit"]["status"], "PASS")
        self.assertEqual(debt["targeted_dependency_audit"]["blocking_incidents"], [])
        adjudication = self.load("adjudication.json")
        self.assertEqual(adjudication["verdict"],
                         "HOLD_USER_LICENSE_CONFIRMATION")
        self.assertFalse(adjudication["gpu_authority_requested_this_round"])
        self.assertFalse(adjudication["p1_open"])


if __name__ == "__main__":
    unittest.main()
