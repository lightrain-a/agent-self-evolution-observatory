from __future__ import annotations

import ast
import inspect
import unittest

from research_pipeline import temporal_skill_g0_reopen_preflight as g0


class TemporalSkillG0ReopenPreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.endpoints = g0.load_endpoints()
        cls.n0, cls.meta, cls.usage = g0.collect_frozen_deepseek_n0()

    def test_support_inventory_is_complete(self) -> None:
        self.assertEqual(set(self.endpoints), set(self.n0))
        self.assertEqual(len(self.endpoints), 35)
        self.assertTrue(all(len(rows) == 5 for rows in self.n0.values()))
        counts: dict[str, int] = {}
        for endpoint in self.endpoints.values():
            family = str(endpoint["failure_family"])
            counts[family] = counts.get(family, 0) + 1
        self.assertEqual(
            counts,
            {
                "temporal_cutoff": 20,
                "exogenous_grounding": 10,
                "release_alignment": 5,
            },
        )

    def test_noop_helper_is_information_empty(self) -> None:
        tree = ast.parse(g0.G0_SOURCE)
        fn = tree.body[0]
        self.assertIsInstance(fn, ast.FunctionDef)
        self.assertEqual([arg.arg for arg in fn.args.args], ["package", "context"])
        loaded_names = {
            node.id
            for node in ast.walk(fn)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        self.assertNotIn("package", loaded_names)
        self.assertNotIn("context", loaded_names)
        self.assertEqual(len(fn.body), 1)
        self.assertIsInstance(fn.body[0], ast.Return)
        self.assertIsInstance(fn.body[0].value, ast.Dict)
        self.assertEqual(len(fn.body[0].value.keys), 0)

    def test_plan_is_complete_and_position_balanced(self) -> None:
        plan = g0.build_plan(self.endpoints, self.meta)
        self.assertEqual(plan["summary"]["planned_model_calls"], 210)
        self.assertEqual(
            plan["summary"]["calls_by_arm"],
            {"N_FRESH": 70, "G0_NOOP": 70, "T_FROZEN": 70},
        )
        by_unit: dict[tuple[str, int], list[dict]] = {}
        for row in plan["rows"]:
            by_unit.setdefault((row["endpoint_id"], int(row["repeat_id"])), []).append(row)
        self.assertEqual(len(by_unit), 70)
        for rows in by_unit.values():
            self.assertEqual({row["arm"] for row in rows}, set(g0.ARMS))
            self.assertEqual({int(row["condition_position"]) for row in rows}, {0, 1, 2})
        for counts in plan["summary"]["condition_position_counts"].values():
            values = list(counts.values())
            self.assertLessEqual(max(values) - min(values), 1)

    def test_plan_body_hash_is_time_invariant(self) -> None:
        p1 = g0.build_plan(self.endpoints, self.meta)
        p2 = g0.build_plan(self.endpoints, self.meta)
        h1 = g0.canonical_sha({k: v for k, v in p1.items() if k != "created_at"})
        h2 = g0.canonical_sha({k: v for k, v in p2.items() if k != "created_at"})
        self.assertEqual(h1, h2)

    def test_preflight_is_fail_closed(self) -> None:
        receipt, plan = g0.build_receipt()
        request = g0.build_authorization_request(receipt, plan)
        self.assertFalse(receipt["authority"]["execution_authorized"])
        self.assertFalse(receipt["authority"]["scientific"])
        self.assertFalse(receipt["authority"]["experiment"])
        self.assertEqual(receipt["policy"]["new_model_calls"], 0)
        self.assertEqual(receipt["policy"]["new_provider_calls"], 0)
        self.assertEqual(plan["summary"]["planned_model_calls"], 210)
        self.assertEqual(receipt["canonical_ledger_snapshot"]["current_state"], "SUBMISSION_READY")
        self.assertEqual(request["bound_plan_body_sha256"], plan["plan_body_sha256"])
        self.assertEqual(request["status"], "AWAIT_EXPLICIT_HUMAN_AUTHORIZATION")
        self.assertFalse(request["execution_authorized"])
        self.assertFalse(request["experiment_authority"])
        self.assertEqual(request["budget"]["model_calls_upper_bound"], 210)
        self.assertFalse(request["budget"]["reruns_allowed"])
        self.assertIn("TEMP-O5_RETRIEVAL_BASELINE", request["explicitly_not_requested"])

    def test_preflight_has_no_generation_client(self) -> None:
        source = inspect.getsource(g0)
        self.assertNotIn("ArkResponsesClient", source)
        self.assertNotIn(".respond(", source)
        self.assertNotIn("requests.post", source)


if __name__ == "__main__":
    unittest.main()
