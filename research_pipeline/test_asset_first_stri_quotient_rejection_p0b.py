from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .asset_first_stri_quotient_rejection_p0b import projected_atom, replay, validate_inputs


class QuotientRejectionP0BTest(unittest.TestCase):
    def contract(self):
        schedule = []
        for cycle, overlap_source in [(1, "skill_003"), (2, "skill_015"), (3, "skill_003")]:
            schedule.extend([
                {"cycle": cycle, "target_atom": "skill_003", "source_skill_id": "skill_003"},
                {"cycle": cycle, "target_atom": "skill_004", "source_skill_id": "skill_004"},
                {"cycle": cycle, "target_atom": "skill_015", "source_skill_id": "skill_015"},
                {"cycle": cycle, "target_atom": "skill_003+skill_015", "source_skill_id": overlap_source},
                {"cycle": cycle, "target_atom": "skill_004+skill_015", "source_skill_id": "skill_004" if cycle != 2 else "skill_015"},
            ])
        return {
            "semantic_projection": {
                "relevant_skill_ids": ["skill_003", "skill_004", "skill_015"],
                "projected_atoms": ["skill_003", "skill_004", "skill_015", "skill_003+skill_015", "skill_004+skill_015"],
            },
            "online_rejection_protocol": {
                "target_schedule": schedule,
                "target_accepts_total": 15,
                "target_accepts_per_atom": 3,
                "maximum_total_consumed_calls": 72,
                "maximum_calls_per_source": 24,
            },
        }

    @staticmethod
    def row(source, index, atom, valid=True):
        accepted = [] if atom in {"NONE", "INVALID"} else atom.split("+")
        row = {
            "source_skill_id": source,
            "source_index": index,
            "contract": {"contract_valid": 1.0 if valid else 0.0},
            "tool_name": f"tool-{index}",
        }
        if valid:
            row["accepted_skill_ids"] = accepted
        return row

    def test_projected_atom_ignores_unrelated_validators(self):
        row = {"accepted_skill_ids": ["skill_003", "skill_015", "skill_099"]}
        self.assertEqual(projected_atom(row, {"skill_003", "skill_004", "skill_015"}), "skill_003+skill_015")

    def test_replay_passes_with_fixed_schedule_and_no_lookahead(self):
        contract = self.contract()
        rows = []
        needed = {
            "skill_003": ["skill_003", "skill_003+skill_015", "skill_003", "skill_003", "skill_003+skill_015"],
            "skill_004": ["skill_004", "skill_004+skill_015", "skill_004", "skill_004", "skill_004+skill_015"],
            "skill_015": ["skill_015", "skill_015", "skill_003+skill_015", "skill_004+skill_015", "skill_015"],
        }
        for source, atoms in needed.items():
            stream = atoms + ["NONE"] * (24 - len(atoms))
            rows.extend(self.row(source, i, atom) for i, atom in enumerate(stream))
        result = replay(contract, rows)
        self.assertTrue(result["complete"])
        self.assertEqual(result["accepted_total"], 15)
        self.assertLessEqual(result["calls_consumed_total"], 72)

    def test_replay_stops_when_unique_atom_never_realizes(self):
        contract = self.contract()
        rows = []
        for source in ["skill_003", "skill_004", "skill_015"]:
            atom = "skill_003+skill_015" if source == "skill_003" else "skill_004+skill_015" if source == "skill_004" else "skill_015"
            rows.extend(self.row(source, i, atom) for i in range(24))
        result = replay(contract, rows)
        self.assertFalse(result["complete"])
        self.assertEqual(result["decision"], "STOP_QUOTIENT_REJECTION_LOCAL_FEASIBILITY")
        self.assertEqual(result["failed_target"]["target_atom"], "skill_003")

    def test_input_binding_requires_p0a_go_and_raw_hash(self):
        contract = self.contract()
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "raw.jsonl"
            rows = []
            for source in ["skill_003", "skill_004", "skill_015"]:
                rows.extend(self.row(source, i, "skill_015") for i in range(24))
            raw.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            bad = validate_inputs(contract, {"decision": "STOP", "protocol_valid_for_scientific_update": True, "raw_sha256": "x"}, raw)
        self.assertFalse(bad["pass"])
        self.assertIn("p0a-not-go", bad["errors"])
        self.assertIn("raw-sha-mismatch", bad["errors"])


if __name__ == "__main__":
    unittest.main()
