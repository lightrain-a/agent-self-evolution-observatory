from __future__ import annotations

import json
import pickle
import tempfile
import unittest
from pathlib import Path

import numpy as np

from research_pipeline.relational_topology_real_corpus import (
    audit_pair, compile_pair, load_object_types,
)
from research_pipeline.relational_topology_real_protocol import (
    CLIP_REVISION, REAL_REGIME_SLOT_COUNTS, ScenePayload, derive_seed,
    filter_symmetric_duplicates, render_fixed_count,
)
from research_pipeline.relational_topology_training_qualification import LICENSE_RECEIPT


class FakeTokenizer:
    def __call__(self, text: str, add_special_tokens: bool = True, truncation: bool = False):
        assert add_special_tokens and not truncation
        return {"input_ids": [0] + list(range(len(text.split()))) + [1]}


class RealProtocolTest(unittest.TestCase):
    def payload(self) -> ScenePayload:
        return ScenePayload(
            scene_uid="scene-uid", scene_id="Bedroom-1",
            object_ids=("o0", "o1", "o2", "o3", "o4"),
            object_types=("armchair", "cabinet", "double_bed", "nightstand", "wardrobe"),
            object_class_ids=(0, 1, 2, 3, 4),
            object_descriptions=("a soft armchair", "a wood cabinet", "a double bed", "a small nightstand", "a tall wardrobe"),
            filtered_relations=((0, 1, 1), (1, 2, 2), (2, 6, 3), (3, 7, 4), (0, 0, 4)),
        )

    def test_seed_depends_on_scene_slot_not_regime(self) -> None:
        self.assertEqual(derive_seed("s", 0), derive_seed("s", 0))
        self.assertNotEqual(derive_seed("s", 0), derive_seed("s", 1))
        self.assertNotEqual(derive_seed("s", 0), derive_seed("t", 0))

    def test_symmetric_duplicate_filter_preserves_first_pair(self) -> None:
        value = filter_symmetric_duplicates([(0, 1, 1), (1, 6, 0), (0, 2, 2)])
        self.assertEqual(value, ((0, 1, 1), (0, 2, 2)))

    def test_fixed_count_protocol_is_deterministic_and_nested(self) -> None:
        payload = self.payload()
        seed = derive_seed(payload.scene_uid, 3)
        one = render_fixed_count(payload, 1, seed)
        four = render_fixed_count(payload, 4, seed)
        self.assertEqual(four, render_fixed_count(payload, 4, seed))
        self.assertEqual(len(four[1]), 4)
        self.assertEqual(one[1][0]["filtered_relation_index"], four[1][0]["filtered_relation_index"])
        self.assertEqual(one[1][0]["predicate"], four[1][0]["predicate"])


class RealCorpusCompileTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bedroom = self.root / "bedroom"
        self.bedroom.mkdir()
        self.stats = self.bedroom / "dataset_stats.txt"
        object_types = ["armchair", "cabinet", "double_bed", "nightstand", "wardrobe"]
        self.stats.write_text(json.dumps({"object_types": object_types}))
        self.split = self.root / "split.csv"
        self.split.write_text("Bedroom-1,train\nBedroom-2,train\n")
        for index in (1, 2):
            scene_uid = f"uid-{index}_Bedroom-{index}"
            scene = self.bedroom / scene_uid
            scene.mkdir()
            desc = {
                "obj_class_ids": [0, 1, 2, 3, 4],
                "obj_relations": [(0, 1, 1), (1, 2, 2), (2, 6, 3), (3, 7, 4), (0, 0, 4)],
            }
            with (scene / "descriptions.pkl").open("wb") as handle:
                pickle.dump(desc, handle)
            models = [{"chatgpt_caption": f"short object {j}"} for j in range(5)]
            with (scene / "models_info.pkl").open("wb") as handle:
                pickle.dump(models, handle)
            np.savez(scene / "boxes.npz",
                     scene_uid=np.array(scene_uid), scene_id=np.array(f"Bedroom-{index}"),
                     uids=np.array([f"m{j}" for j in range(5)]))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_exact_license_and_replay(self) -> None:
        kwargs = dict(
            bedroom_root=self.bedroom, split_csv=self.split,
            object_types=load_object_types(self.stats), tokenizer=FakeTokenizer(),
            generator_code_sha="a" * 40, license_receipt=LICENSE_RECEIPT,
        )
        forward = compile_pair(**kwargs, traversal="forward", workers=1)
        reverse = compile_pair(**kwargs, traversal="reverse", workers=1)
        shuffled = compile_pair(**kwargs, traversal="shuffled", workers=1)
        workers = compile_pair(**kwargs, traversal="forward", workers=2)
        hashes = {tuple(value["jsonl_sha256"].items()) for value in (forward, reverse, shuffled, workers)}
        self.assertEqual(len(hashes), 1)
        self.assertEqual(len(forward["eligible_scenes"]), 2)
        audit = audit_pair(forward)
        self.assertTrue(audit["gates"]["equal_example_count"])
        self.assertTrue(audit["gates"]["shared_1_2_relation_subset_exact"])
        self.assertTrue(audit["gates"]["zero_clip_truncation"])
        self.assertEqual(set(audit["relation_count_histogram"]["IS-SUPPORT-12"]), {"1", "2"})
        self.assertEqual(set(audit["relation_count_histogram"]["IS-SUPPORT-14"]), {"1", "2", "3", "4"})
        for regime, rows in forward["rows"].items():
            self.assertEqual(len(rows), 8, regime)
            self.assertTrue(all(row["clip_tokenizer_revision"] == CLIP_REVISION for row in rows))

    def test_bad_license_fails_closed(self) -> None:
        with self.assertRaises(PermissionError):
            compile_pair(
                self.bedroom, self.split, load_object_types(self.stats), FakeTokenizer(),
                "a" * 40, LICENSE_RECEIPT + " ",
            )


if __name__ == "__main__":
    unittest.main()
