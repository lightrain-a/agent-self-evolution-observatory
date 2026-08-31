from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/compile_relational_topology_stage_3d_pre_f0.py"


class RelationalTopologyStagePreF0Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.log = root / "suite.log"
        cls.log.write_text(
            "FAIL: test_old_unrelated (legacy.test_old.LegacyTest)\n"
            "Ran 1820 tests in 4561.0s\n\n"
            "FAILED (failures=1, errors=24, skipped=3)\n"
        )
        cls.out = root / "out"
        subprocess.run(
            [sys.executable, str(SCRIPT), "--output-dir", str(cls.out),
             "--regression-log", str(cls.log), "--regression-base-sha", "f" * 40],
            cwd=ROOT, check=True, capture_output=True, text=True)
        cls.load = staticmethod(lambda name: json.loads((cls.out / name).read_text()))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_manifest_and_frozen_parent_content_addresses(self) -> None:
        manifest = self.load("manifest.json")
        self.assertEqual(manifest["artifact_count"], 19)
        self.assertEqual(manifest["scientific_gpu_runs"], 0)
        for name, expected in manifest["artifact_sha256"].items():
            got = hashlib.sha256((self.out / name).read_bytes()).hexdigest()
            self.assertEqual(got, expected, name)
        source = self.load("source_manifest.json")
        for path, expected in source["parent_artifacts"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)

    def test_seven_model_current_source_protocol(self) -> None:
        protocol = self.load("model_protocol.json")
        rows = {row["name"]: row for row in protocol["models"]}
        self.assertEqual(set(rows), {"ATISS", "DiffuScene", "InstructScene", "SceneNAT",
                                    "FreeScene", "SceneFactor", "LayoutGPT"})
        self.assertEqual(rows["InstructScene"]["repo_sha"],
                         "a9097a62c484c56ac7be5ec2928ef497cbbaaf24")
        self.assertEqual(rows["SceneNAT"]["repo_sha"],
                         "542b82ff0cda4e0350575ca8f1cd5d147529130c")
        self.assertEqual(rows["InstructScene"]["role"], "MECHANISM_CARRIER")
        self.assertEqual(rows["SceneNAT"]["classification"],
                         "CURRENT_UNPUBLISHED_STRONG_COMPARATOR")
        self.assertIn("code is coming", rows["FreeScene"]["checkpoint"])
        self.assertEqual(protocol["same_access_main_set"],
                         ["IS-SUPPORT-12", "IS-SUPPORT-14"])

    def test_topology_construct_is_matched_and_structurally_distinct(self) -> None:
        rows = [json.loads(x) for x in (self.out / "topology_cases.jsonl").read_text().splitlines()]
        self.assertEqual({r["topology_class"] for r in rows},
                         {"DISJOINT", "CHAIN", "HUB", "COMPONENT_BRIDGE"})
        self.assertEqual({r["relation_count"] for r in rows}, {5})
        self.assertEqual({tuple(r["object_universe"]) for r in rows},
                         {tuple("ABCDEFGHIJ")})
        self.assertEqual(len({json.dumps(r["relation_family_composition"], sort_keys=True)
                              for r in rows}), 1)
        maxima = {r["topology_class"]: r["graph_topology_statistics"]["maximum_degree"]
                  for r in rows}
        self.assertEqual(maxima["DISJOINT"], 1)
        self.assertEqual(maxima["CHAIN"], 2)
        self.assertEqual(maxima["HUB"], 5)
        self.assertTrue(all(r["exact_clip_token_count"] is None for r in rows))
        self.assertTrue(all(r["matching_status"].endswith("NO_SCIENTIFIC_SAMPLE") for r in rows))

    def test_support_crossover_is_identifiable_contract(self) -> None:
        support = self.load("construct_manifest.json")["support_intervention"]
        self.assertEqual(support["models"]["IS-SUPPORT-12"]["train_relation_support"], [1, 2])
        self.assertEqual(support["models"]["IS-SUPPORT-14"]["train_relation_support"], [1, 2, 3, 4])
        self.assertEqual(support["labels"]["3-4"], "OUT_12_IN_14")
        self.assertIn("SG2SC", support["same_decoder_runtime_gate"])
        self.assertIn("intrinsic capacity", support["forbidden_inference"])

    def test_token_and_pairing_gates_fail_closed(self) -> None:
        token = json.loads((self.out / "tokenization.jsonl").read_text())
        self.assertEqual(token["scientific_samples"], 0)
        self.assertEqual(token["exact_token_counts_materialized"], [])
        self.assertIn("tokenizer_truncated == true", token["forbidden_primary_condition"])
        pairing = json.loads((self.out / "graph_pairing.jsonl").read_text())
        self.assertIn("exact padded-slot", pairing["eligibility"])
        self.assertIn("Hungarian matching", pairing["forbidden"])
        self.assertTrue(pairing["fail_closed"].startswith("STOP_AND_ADJUDICATE"))
        self.assertEqual(pairing["relation_edge_source_intervention"]["label"],
                         "RELATION_EDGE_SOURCE_INTERVENTION")

    def test_stage_metrics_have_exact_numerator_denominator_and_failure_policy(self) -> None:
        evaluator = self.load("evaluator_contract.json")
        self.assertEqual(set(evaluator["observables"]), {
            "text_to_graph_relation_recall", "graph_to_scene_relation_retention",
            "end_to_end_relation_iRecall"})
        for spec in evaluator["observables"].values():
            self.assertTrue(spec["numerator"])
            self.assertTrue(spec["denominator"])
            self.assertTrue(spec["failure"])
        self.assertEqual(evaluator["primary"], "relation_level_iRecall")
        self.assertEqual(evaluator["secondary"], "exact_all_success")
        self.assertIn("failures contribute zero", evaluator["missingness"])

    def test_analysis_has_no_forced_breakpoint_and_masks_capability(self) -> None:
        analysis = self.load("analysis_plan.json")
        self.assertIn("relation_count_c * exact_clip_token_count_c", analysis["formula"])
        self.assertIn("training_support_regime * topology_class", analysis["formula"])
        self.assertIn("smooth degradation default", analysis["shape"])
        self.assertIn("NA_NOT_MEASURED", analysis["capability_masking"][0])
        self.assertGreaterEqual(len(analysis["continuous_topology_sensitivity"]), 7)

    def test_authority_port_and_paper_firewalls(self) -> None:
        authority = self.load("authority.json")
        for key in ("gpu_authority", "official_two_stage_training", "p1",
                    "data_license_confirmed", "data_materialization", "provider_calls"):
            self.assertFalse(authority[key])
        self.assertEqual(authority["scientific_gpu_runs"], 0)
        self.assertEqual(authority["port_010"]["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual(authority["port_010"]["evidence_review"], "BLOCK_BAKE_IN")
        paper = self.load("paper_boundary.json")
        self.assertIn("Agent paper", paper["forbidden_overlap"])
        self.assertEqual(paper["results"], "EMPTY_PRE_F0_NO_SCIENTIFIC_OUTCOMES")

    def test_debt_classification_and_pass_proposal_only(self) -> None:
        debt = self.load("regression_debt.json")
        self.assertEqual(debt["status"], "COMPLETE")
        self.assertEqual(debt["authority_impact"], "SCOPED_NON_BLOCKING_DEBT")
        self.assertEqual(debt["counts"], {"failures": 1, "errors": 24, "skips": 3})
        adj = self.load("adjudication.json")
        self.assertEqual(adj["verdict"], "PRE_F0_CHILD_PASS_PROPOSAL_ONLY")
        self.assertTrue(all(value != "HOLD" for value in adj["gates"].values()))
        self.assertFalse(adj["authority_requested_this_round"])
        self.assertEqual(adj["scientific_gpu_runs"], 0)


if __name__ == "__main__":
    unittest.main()
