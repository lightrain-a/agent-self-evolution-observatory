from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_fresh_support import REALIZATION_ID
from .paper_first_agent_safety_r9_fresh_support_classifier import aggregate, collect_items
from .paper_first_agent_safety_r9_harness import CANDIDATE_ID, CONTRACT_SHA256


class FreshSupportClassifierTest(unittest.TestCase):
    def contract(self) -> dict:
        return {
            "development_ids": [0, 9, 36],
            "qualification_ids": [2, 10, 38],
            "heldout_ids": [34, 21, 1, 8, 11, 22, 13, 33],
            "states": [
                {"state_id": "s0"}, {"state_id": "s1"}, {"state_id": "s2"}, {"state_id": "s3"},
            ],
        }

    def write_episode(self, root: Path, state_id: str, probe: int, mode: str, text: str) -> None:
        d = root / state_id / f"probe-{probe}"
        d.mkdir(parents=True, exist_ok=True)
        p = d / "classifier-input.txt"
        p.write_text(text, encoding="utf-8")
        (d / "episode-result.json").write_text(json.dumps({
            "status": "COMPLETE",
            "realization_id": REALIZATION_ID,
            "mode": mode,
            "classifier_evaluated": False,
            "classifier_input_path": str(p),
            "classifier_input_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }), encoding="utf-8")

    def write_hbb(self, root: Path) -> Path:
        p = root / "hbb.json"
        p.write_text(json.dumps([
            {"id": i, "behavior": f"behavior-{i}", "context": ""}
            for i in (0, 9, 36, 2, 10, 38)
        ]), encoding="utf-8")
        return p

    def test_collect_development_exact_grid(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); episodes = root / "episodes"
            for probe in (0, 9, 36): self.write_episode(episodes, "fresh-dev-empty-workflow", probe, "development", f"x-{probe}")
            items = collect_items(contract=self.contract(), mode="development", episode_root=episodes, hbb_dataset=self.write_hbb(root))
            self.assertEqual([(x["state_id"], x["probe_id"]) for x in items], [("fresh-dev-empty-workflow",0),("fresh-dev-empty-workflow",9),("fresh-dev-empty-workflow",36)])

    def test_collect_qualification_exact_4x3_grid(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); episodes = root / "episodes"
            for state in ("s0","s1","s2","s3"):
                for probe in (2,10,38): self.write_episode(episodes, state, probe, "qualification", f"{state}-{probe}")
            items = collect_items(contract=self.contract(), mode="qualification", episode_root=episodes, hbb_dataset=self.write_hbb(root))
            self.assertEqual(len(items), 12)
            self.assertEqual({x["probe_id"] for x in items}, {2,10,38})

    def test_digest_drift_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); episodes=root/"episodes"
            for probe in (0,9,36): self.write_episode(episodes,"fresh-dev-empty-workflow",probe,"development",f"x-{probe}")
            p=episodes/"fresh-dev-empty-workflow"/"probe-9"/"classifier-input.txt"; p.write_text("tampered",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"digest drift"):
                collect_items(contract=self.contract(),mode="development",episode_root=episodes,hbb_dataset=self.write_hbb(root))

    def test_aggregate_requires_all_non_violation(self) -> None:
        items=[
            {"state_id":"fresh-dev-empty-workflow","probe_id":0,"classifier_input_sha256":"a","classifier_input_bytes":1},
            {"state_id":"fresh-dev-empty-workflow","probe_id":9,"classifier_input_sha256":"b","classifier_input_bytes":0},
            {"state_id":"fresh-dev-empty-workflow","probe_id":36,"classifier_input_sha256":"c","classifier_input_bytes":2},
        ]
        ok=aggregate(contract=self.contract(),mode="development",items=items,binary=[False,False,False],classifier_sha="x")
        self.assertTrue(ok["all_states_all_probes_non_violation"]); self.assertEqual(ok["empty_classifier_input_count"],1)
        bad=aggregate(contract=self.contract(),mode="development",items=items,binary=[False,True,False],classifier_sha="x")
        self.assertFalse(bad["all_states_all_probes_non_violation"])


if __name__ == "__main__": unittest.main()
