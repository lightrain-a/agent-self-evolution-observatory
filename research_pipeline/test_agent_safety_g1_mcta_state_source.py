from __future__ import annotations

import json
import unittest
from pathlib import Path

from research_pipeline.agent_safety_g1_mcta_state_source import (
    P1_FAMILY_QUOTAS,
    build_manifest,
    family_role_split,
    reconstruct_state_bytes,
    serialize_state,
    sha_bytes,
    split_workflow_units,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "generated" / "agent-safety-g1-mcta-fresh-state-source-manifest-20260904.json"


def tiny_source(prefix: str, n: int = 6) -> str:
    return "## Concrete Examples\n\n" + "\n\n".join(
        f"Query: {prefix} benign task {i}\nAction: benign_{prefix}_{i}()"
        for i in range(n)
    ) + "\n"


class MCTAStateSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_family_role_split_is_stable_and_disjoint(self) -> None:
        _, states, updates = family_role_split()
        self.assertEqual(states, ["shopping_admin", "gitlab", "reddit"])
        self.assertEqual(updates, ["shopping", "map"])
        self.assertFalse(set(states) & set(updates))

    def test_historical_serialization_rule(self) -> None:
        units = [
            {"raw": "Query: A\nAct: a\n\n"},
            {"raw": "Query: B\nAct: b\n\n"},
            {"raw": "Query: C\nAct: c\n"},
        ]
        self.assertEqual(
            serialize_state(units),
            b"Query: A\nAct: a\n\nQuery: B\nAct: b\n\nQuery: C\nAct: c\n",
        )

    def test_build_manifest_uses_no_outcomes_and_has_two_plus_eight_states(self) -> None:
        sources = {
            "gitlab": tiny_source("gitlab", 7),
            "map": tiny_source("map", 7),
            "reddit": tiny_source("reddit", 7),
            "shopping": tiny_source("shopping", 7),
            "shopping_admin": tiny_source("shopping_admin", 7),
        }
        hashes = {family: sha_bytes(text.encode()) for family, text in sources.items()}
        manifest = build_manifest(
            source_texts=sources,
            source_file_sha256=hashes,
            historical_exact_state_hashes=set(),
        )
        self.assertEqual(len(manifest["p0_states"]), 2)
        self.assertEqual(len(manifest["p1_states"]), 8)
        self.assertEqual(len(manifest["update_sequences"]), 2)
        self.assertEqual(
            [sum(row["family"] == family for row in manifest["p1_states"]) for family in manifest["state_families"]],
            list(P1_FAMILY_QUOTAS),
        )
        self.assertFalse(manifest["selection_policy"]["safety_outcomes_used"])
        self.assertFalse(manifest["selection_policy"]["semantic_evaluator_labels_used"])

    def test_exact_historical_state_hash_is_excluded(self) -> None:
        sources = {
            "gitlab": tiny_source("gitlab", 7),
            "map": tiny_source("map", 7),
            "reddit": tiny_source("reddit", 7),
            "shopping": tiny_source("shopping", 7),
            "shopping_admin": tiny_source("shopping_admin", 7),
        }
        units = split_workflow_units(sources["shopping_admin"])
        forbidden = sha_bytes(serialize_state([units[0], units[1], units[2]]))
        hashes = {family: sha_bytes(text.encode()) for family, text in sources.items()}
        manifest = build_manifest(
            source_texts=sources,
            source_file_sha256=hashes,
            historical_exact_state_hashes={forbidden},
        )
        all_state_hashes = {row["workflow_sha256"] for row in manifest["p0_states"] + manifest["p1_states"]}
        self.assertNotIn(forbidden, all_state_hashes)

    def test_static_manifest_has_expected_family_balance_and_unique_state_bytes(self) -> None:
        manifest = self.manifest
        self.assertEqual(manifest["state_families"], ["shopping_admin", "gitlab", "reddit"])
        self.assertEqual(manifest["update_families"], ["shopping", "map"])
        self.assertEqual(len(manifest["p0_states"]), 2)
        self.assertEqual(len(manifest["p1_states"]), 8)
        state_hashes = [row["workflow_sha256"] for row in manifest["p0_states"] + manifest["p1_states"]]
        self.assertEqual(len(state_hashes), len(set(state_hashes)))
        self.assertEqual(
            [sum(row["family"] == family for row in manifest["p1_states"]) for family in manifest["state_families"]],
            [3, 3, 2],
        )

    def test_static_manifest_is_zero_authority_and_exactly_two_three_step_updates(self) -> None:
        manifest = self.manifest
        self.assertTrue(all(value is False for value in manifest["authority"].values()))
        self.assertEqual(len(manifest["update_sequences"]), 2)
        self.assertTrue(all(len(seq["steps"]) == 3 for seq in manifest["update_sequences"]))
        self.assertFalse(manifest["selection_policy"]["replacement_after_future_outcome"])


if __name__ == "__main__":
    unittest.main()
