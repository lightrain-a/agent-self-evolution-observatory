from __future__ import annotations

import unittest

from .asset_first_stri_quotient_invariance import (
    distribute_credit,
    joint_cell_primitive_mass,
    package_mass,
    primitive_mass,
)


class QuotientInvarianceTest(unittest.TestCase):
    def setUp(self):
        self.mu={"u3":0.2,"u15":0.3,"u3+u15":0.5}
        self.alpha={
            "u3":{"p3":1.0},
            "u15":{"p15":1.0},
            "u3+u15":{"p3":0.5,"p15":0.5},
        }

    def test_package_regrouping_does_not_change_cell_or_primitive_mass(self):
        joint=joint_cell_primitive_mass(self.mu,self.alpha)
        primitive=primitive_mass(joint)
        split=package_mass(primitive,{"p3":"skill_003","p15":"skill_015"})
        merged=package_mass(primitive,{"p3":"macro_003_015","p15":"macro_003_015"})
        self.assertAlmostEqual(sum(split.values()),1.0)
        self.assertAlmostEqual(sum(merged.values()),1.0)
        self.assertEqual(joint,joint_cell_primitive_mass(self.mu,self.alpha))
        self.assertEqual(primitive,primitive_mass(joint))
        self.assertNotEqual(split,merged)

    def test_credit_is_conserved_before_package_bookkeeping(self):
        semantic={"u3":1.0,"u15":2.0,"u3+u15":3.0}
        primitive=distribute_credit(semantic,self.alpha)
        self.assertAlmostEqual(sum(primitive.values()),sum(semantic.values()))
        self.assertAlmostEqual(primitive["p3"],2.5)
        self.assertAlmostEqual(primitive["p15"],3.5)

    def test_invalid_responsibility_fails_closed(self):
        bad=dict(self.alpha);bad["u3+u15"]={"p3":0.7,"p15":0.7}
        with self.assertRaises(ValueError):
            joint_cell_primitive_mass(self.mu,bad)

if __name__=="__main__":unittest.main()
