from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_problem_discovery_contract import DISCOVERY_LANES, FORBIDDEN_DISCOVERY_LANES
from .paper_first_problem_gate_queue import build_problem_gate_queue
from .test_paper_first_problem_discovery_contract import valid_candidate


def write_primary_pool(root: Path, candidate: dict | None = None) -> Path:
    candidate = candidate or valid_candidate()
    sources = candidate["empirical_evidence"]
    records = []
    for key in ("source_a", "source_b"):
        source = sources[key]
        records.append(
            {
                "ref": source["ref"],
                "title": source["title"],
                "primary_url": source["primary_url"],
                "source_sha256": source["source_sha256"],
                "primary_source_verified": True,
                "abstract": source["claim"] + " Additional private primary evidence context.",
                "typed_evidence": {
                    "operational_assumptions": [{"section":"Method Assumptions","text":source["claim"],"text_sha256":"a"*64}] if source.get("evidence_role")=="OPERATIONAL_ASSUMPTION" else [],
                    "measured_failures": [],
                    "boundary_observations": [],
                },
            }
        )
    path = root / "primary.json"
    path.write_text(json.dumps({"records": records}), encoding="utf-8")
    return path


class PaperFirstProblemGateQueueTest(unittest.TestCase):
    def test_missing_inboxes_are_valid_empty_multilane_queue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            state = build_problem_gate_queue(root / "missing.json", auto_inbox_path=root / "auto-missing.json", primary_pool_path=root / "primary-missing.json")
        self.assertEqual((state["summary"]["submitted"], state["summary"]["passed_problem_gate"], state["summary"]["blocked_problem_gate"]), (0, 0, 0))
        self.assertEqual(state["inbox_errors"], [])
        self.assertTrue(state["policy"]["zero_candidates_or_zero_passes_is_valid"])
        self.assertEqual((state["summary"]["method_authorized"], state["summary"]["experiment_authorized"], state["summary"]["p0_authorized"]), (0, 0, 0))
        for lane in DISCOVERY_LANES:
            self.assertEqual(state["summary"]["submitted_by_lane"][lane], 0)

    def test_each_allowed_lane_only_enters_human_paper_design_with_verified_registry(self) -> None:
        for lane in DISCOVERY_LANES:
            with self.subTest(lane=lane), tempfile.TemporaryDirectory() as td:
                root = Path(td); candidate = valid_candidate(lane); path = root / "inbox.json"
                path.write_text(json.dumps({"candidates": [candidate]}), encoding="utf-8")
                state = build_problem_gate_queue(path, auto_inbox_path=root / "none.json", primary_pool_path=write_primary_pool(root, candidate))
            self.assertEqual((state["summary"]["submitted"], state["summary"]["passed_problem_gate"], state["summary"]["paper_design_eligible"]), (1, 1, 1))
            self.assertEqual(state["passed"][0]["status"], "AWAIT_HUMAN_PAPER_DESIGN_REVIEW")
            self.assertEqual(state["passed"][0]["discovery_lane"], lane)
            self.assertEqual(state["summary"]["submitted_by_lane"][lane], 1)
            self.assertEqual(state["summary"]["passed_by_lane"][lane], 1)
            self.assertEqual(state["summary"]["primary_evidence_records"], 2)
            self.assertEqual((state["summary"]["method_authorized"], state["summary"]["experiment_authorized"], state["summary"]["p0_authorized"]), (0, 0, 0))

    def test_forbidden_lane_never_enters_human_queue(self) -> None:
        for lane in FORBIDDEN_DISCOVERY_LANES:
            with self.subTest(lane=lane), tempfile.TemporaryDirectory() as td:
                root = Path(td); candidate = valid_candidate(); candidate["discovery_lane"] = lane; path = root / "inbox.json"
                path.write_text(json.dumps({"candidates": [candidate]}), encoding="utf-8")
                state = build_problem_gate_queue(path, auto_inbox_path=root / "none.json", primary_pool_path=write_primary_pool(root, candidate))
            self.assertEqual((state["summary"]["passed_problem_gate"], state["summary"]["blocked_problem_gate"]), (0, 1))
            self.assertIn(f"forbidden-discovery-lane:{lane}", state["blocked"][0]["blockers"])

    def test_candidate_without_primary_registry_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); path = root / "inbox.json"; path.write_text(json.dumps({"candidates": [valid_candidate("CONVERGENT_FAILURE")]}), encoding="utf-8")
            state = build_problem_gate_queue(path, auto_inbox_path=root / "none.json", primary_pool_path=root / "missing-primary.json")
        self.assertEqual((state["summary"]["passed_problem_gate"], state["summary"]["blocked_problem_gate"]), (0, 1))
        self.assertTrue(any(value.startswith("primary-source-not-in-registry:") for value in state["blocked"][0]["blockers"]))

    def test_saturation_match_is_blocked_before_paper_design(self) -> None:
        candidate = valid_candidate("UNEXPLAINED_BOUNDARY")
        candidate["saturation_scan"] = {"checked": True, "matched_patterns": ["externalization-internalization-portability"]}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); path = root / "inbox.json"; path.write_text(json.dumps({"candidates": [candidate]}), encoding="utf-8")
            state = build_problem_gate_queue(path, auto_inbox_path=root / "none.json", primary_pool_path=write_primary_pool(root, candidate))
        self.assertEqual((state["summary"]["passed_problem_gate"], state["summary"]["blocked_problem_gate"]), (0, 1))
        self.assertTrue(any(value.startswith("saturation-pattern-match:") for value in state["blocked"][0]["blockers"]))

    def test_manual_and_auto_inboxes_merge_but_duplicate_ids_are_never_eligible(self) -> None:
        first = valid_candidate(); second = valid_candidate("ASSUMPTION_BREAK"); second["title"] = "duplicate"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); manual = root / "manual.json"; auto = root / "auto.json"
            manual.write_text(json.dumps({"candidates": [first]}), encoding="utf-8")
            auto.write_text(json.dumps({"candidates": [second]}), encoding="utf-8")
            # Registry must contain both source pairs. Their refs are intentionally identical in fixtures,
            # so the first candidate registry is sufficient for provenance identity.
            state = build_problem_gate_queue(manual, auto_inbox_path=auto, primary_pool_path=write_primary_pool(root, first))
        self.assertEqual(state["summary"]["submitted"], 2)
        self.assertEqual(state["summary"]["paper_design_eligible"], 0)
        self.assertEqual(state["summary"]["inbox_errors"], 1)
        self.assertTrue(state["inbox_errors"][0].startswith("duplicate-candidate-ids:"))

    def test_primary_sha_mismatch_is_blocked(self) -> None:
        candidate = valid_candidate(); candidate["empirical_evidence"]["source_a"]["source_sha256"] = "d" * 64
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); path = root / "inbox.json"; path.write_text(json.dumps({"candidates": [candidate]}), encoding="utf-8")
            pool = write_primary_pool(root, candidate)
            payload = json.loads(pool.read_text()); payload["records"][0]["source_sha256"] = "a" * 64; pool.write_text(json.dumps(payload))
            state = build_problem_gate_queue(path, auto_inbox_path=root / "none.json", primary_pool_path=pool)
        self.assertIn("primary-source-sha-mismatch:1", state["blocked"][0]["blockers"])


if __name__ == "__main__":
    unittest.main()
