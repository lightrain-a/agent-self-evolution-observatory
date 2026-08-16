from __future__ import annotations

import unittest

from .asset_first_stri_tool_disjoint_split import FIVE_ATOMS, build_split


class ToolDisjointSplitTest(unittest.TestCase):
    @staticmethod
    def row(index, tool, accepted):
        return {"level": 1, "index": index, "tool": tool, "accepted_skill_ids": accepted}

    def test_split_is_tool_disjoint_and_preserves_five_atoms(self):
        rows=[]; i=0
        for sid, tools in {
            "skill_003":["A","B","C","D"],
            "skill_004":["E","F","G","H"],
        }.items():
            for tool in tools:
                rows.append(self.row(i,tool,[sid])); i+=1
                rows.append(self.row(i,tool,[sid,"skill_015"])); i+=1
                rows.append(self.row(i,tool,["skill_015"])); i+=1
        result=build_split(rows)
        cal=set(result["partitions"]["calibration"]["tools"])
        test=set(result["partitions"]["heldout"]["tools"])
        self.assertFalse(cal & test)
        for role in ("calibration","heldout"):
            counts=result["partitions"][role]["five_atom_counts"]
            self.assertTrue(all(counts[atom]>0 for atom in FIVE_ATOMS))
            self.assertTrue(all(v["pass"] for v in result["partitions"][role]["mandatory_overlap_witnesses"].values()))

    def test_rejects_partition_without_generic_only_atom(self):
        rows=[]; i=0
        for sid, tools in {"skill_003":["A","B","C","D"],"skill_004":["E","F","G","H"]}.items():
            for tool in tools:
                rows.append(self.row(i,tool,[sid])); i+=1
                rows.append(self.row(i,tool,[sid,"skill_015"])); i+=1
        with self.assertRaises(RuntimeError):
            build_split(rows)


if __name__ == "__main__":
    unittest.main()
