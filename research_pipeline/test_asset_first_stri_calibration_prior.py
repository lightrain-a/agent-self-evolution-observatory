from __future__ import annotations

import unittest

from .asset_first_stri_calibration_prior import FIVE_ATOMS, build_prior


class CalibrationPriorTest(unittest.TestCase):
    @staticmethod
    def row(index,tool,accepted):
        return {"level":1,"index":index,"tool":tool,"accepted_skill_ids":accepted}

    def test_prior_uses_only_calibration_tools(self):
        split={"split_id":"x","partitions":{"calibration":{"tools":["A","B"]},"heldout":{"tools":["C","D"]}}}
        rows=[
          self.row(0,"A",["skill_003"]),self.row(1,"A",["skill_004"]),self.row(2,"A",["skill_015"]),
          self.row(3,"B",["skill_003","skill_015"]),self.row(4,"B",["skill_004","skill_015"]),
          self.row(5,"C",["skill_003"]),self.row(6,"C",["skill_003"]),self.row(7,"D",["skill_004","skill_015"]),
        ]
        result=build_prior(rows,split)
        self.assertEqual(result["calibration_non_none_rows"],5)
        self.assertEqual(result["empirical_calibration_prior"],{a:0.2 for a in FIVE_ATOMS})
        self.assertEqual(result["heldout_frequency_audit_only"]["counts"]["skill_003"],2)
        self.assertFalse(result["heldout_frequency_audit_only"]["may_change_prior_or_structure"])

    def test_missing_calibration_atom_fails_closed(self):
        split={"split_id":"x","partitions":{"calibration":{"tools":["A"]},"heldout":{"tools":["B"]}}}
        with self.assertRaises(ValueError):
            build_prior([self.row(0,"A",["skill_003"])],split)

if __name__=="__main__":unittest.main()
