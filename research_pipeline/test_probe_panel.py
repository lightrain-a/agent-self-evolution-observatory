from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .a1_screening_review import build as build_screening_review
from .mastered_probe_panel import build as build_mastered_panel
from .p0_a1 import _candidate, synthetic_rows as synthetic_a1
from .p0_common import load_json
from .probe_panel_replay_qualification import analyze_replays


class ProbePanelTest(unittest.TestCase):
    def test_mastered_panel_never_selects_baseline_failures(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "qualification-traces.jsonl"
            rows = []
            families = ["look", "put", "clean", "heat", "put", "clean", "cool", "two"]
            successes = [1, 1, 1, 1, 1, 1, 0, 0]
            for index, (family, success) in enumerate(zip(families, successes)):
                rows.append({
                    "index": index,
                    "trace": {
                        "task_id": f"/data/json_2.1.1/valid_seen/{family}/trial-{index}/game.tw-pddl",
                        "task_family": family,
                        "success": success,
                        "steps": 5 + index,
                    },
                })
            source.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            panel = build_mastered_panel(source, panel_size=6)
            self.assertTrue(panel["pass"])
            self.assertEqual(len(panel["selected"]), 6)
            self.assertTrue(all(row["baseline_success"] == 1 for row in panel["selected"]))
            self.assertEqual(panel["task_family_coverage"], 4)

    def test_mastered_probe_replay_detects_a_perfect_development_signal(self) -> None:
        config = load_json(Path(__file__).with_name("p0_a1_screening_config.json"))
        candidate_rows = synthetic_a1()
        candidates = [_candidate(row, config) for row in candidate_rows]
        panel = {"selected": [{"task_id": "probe-1"}, {"task_id": "probe-2"}]}
        baseline = {
            "probe-1": {"task_id": "probe-1", "task_family": "put", "success": 1, "steps": 2, "actions": ["look", "take mug"], "invalid_choice_rate": 0.0},
            "probe-2": {"task_id": "probe-2", "task_family": "clean", "success": 1, "steps": 2, "actions": ["look", "take soap"], "invalid_choice_rate": 0.0},
        }
        replay_rows = []
        for candidate in candidates:
            for task_id in baseline:
                harmful = bool(candidate.harmful)
                replay_rows.append({
                    "candidate_id": candidate.candidate_id,
                    "trace": {
                        "task_id": task_id,
                        "task_family": baseline[task_id]["task_family"],
                        "success": 0 if harmful else 1,
                        "steps": 3 if harmful else 2,
                        "actions": ["look", "go elsewhere", "fail"] if harmful else list(baseline[task_id]["actions"]),
                        "invalid_choice_rate": 0.0,
                    },
                })
        result = analyze_replays(config, candidate_rows, panel, baseline, replay_rows)
        self.assertTrue(result["development_fidelity_pass"])
        self.assertGreaterEqual(result["probe_only_leave_one_candidate_out_auc"], 0.95)
        self.assertGreaterEqual(result["total_probe_success_loss_events"], 3)

    def test_directional_screening_does_not_override_failed_probe_fidelity(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            screening = root / "screening.json"
            fidelity = root / "fidelity.json"
            screening.write_text(json.dumps({
                "decision": "screening-signal",
                "analysis": {
                    "harmful_candidate_count": 6,
                    "matched_acceptance_count": 8,
                    "harmful_update_reduction": 1 / 3,
                    "target_gain_loss": 0.0,
                    "strongest_simple_baseline": "current-task-gain",
                },
            }), encoding="utf-8")
            fidelity.write_text(json.dumps({
                "fidelity_pass": False,
                "fixed_probe_count": 6,
                "probe_rows": [{"baseline_success": 0} for _ in range(6)],
                "aggregate_panel_leave_one_candidate_out_auc": 0.37,
                "best_single_probe_action_auc": 0.54,
                "minimum_fidelity_auc": 0.65,
            }), encoding="utf-8")
            review = build_screening_review(screening, fidelity)
            self.assertEqual(review["classification"], "SCREENING-SIGNAL / CONFIRMATORY-BLOCKED")
            self.assertFalse(review["confirmatory_authorized"])
            self.assertIn("probe-baseline-mastery:0/6", review["blockers"])
            self.assertFalse(review["method_result_available"])


if __name__ == "__main__":
    unittest.main()
