from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .reopened_principle_memory_closure import build_principle_scientific_closure
from .research_memory_wiki import build_research_memory_wiki, compile_research_memory_query_pack
from .test_reopened_principle_memory_closure import ReopenedPrincipleMemoryClosureTest
from .test_research_memory_wiki import base_inputs


class ReopenedPrincipleMemoryWikiIntegrationTest(unittest.TestCase):
    def build_base(self, *, principle_closure_registry=None):
        search, failures, meta, portfolio, iteration, generator, claims = base_inputs()
        kwargs = dict(
            search_design_state=search,
            failure_asset_library=failures,
            scientific_meta_trace=meta,
            candidate_portfolio=portfolio,
            experiment_iteration=iteration,
            generator_state=generator,
            claim_ledger=claims,
            generated_at="2027-04-13T13:00:00+00:00",
        )
        if principle_closure_registry is not None:
            kwargs["principle_closure_registry"] = principle_closure_registry
        return build_research_memory_wiki(**kwargs)

    def closure(self, root: Path) -> dict:
        helper = ReopenedPrincipleMemoryClosureTest(methodName="test_persisted_closure_is_scoped_reopenable_and_zero_downstream_authority")
        return build_principle_scientific_closure(
            memory_handoff=helper.handoff(root),
            persisted_at="2027-04-13T12:00:00+00:00",
        )

    def test_legacy_default_and_explicit_none_are_byte_semantically_identical(self) -> None:
        search, failures, meta, portfolio, iteration, generator, claims = base_inputs()
        kwargs = dict(
            search_design_state=search,
            failure_asset_library=failures,
            scientific_meta_trace=meta,
            candidate_portfolio=portfolio,
            experiment_iteration=iteration,
            generator_state=generator,
            claim_ledger=claims,
            generated_at="2027-04-13T13:00:00+00:00",
        )
        legacy = build_research_memory_wiki(**kwargs)
        explicit_none = build_research_memory_wiki(**kwargs, principle_closure_registry=None)
        self.assertEqual(legacy, explicit_none)
        self.assertNotIn("p0_principle_closures", legacy["source_manifest"])
        self.assertEqual(legacy["lint"]["status"], "PASS")

    def test_explicit_p0_principle_closure_becomes_scoped_scientific_closure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            closure = self.closure(Path(td))
            wiki = self.build_base(principle_closure_registry=[closure])
            self.assertEqual(wiki["status"], "MEMORY_COMPILED")
            self.assertEqual(wiki["lint"]["status"], "PASS")
            self.assertEqual(wiki["source_manifest"]["p0_principle_closures"], 1)
            row = next(item for item in wiki["entries"] if item["memory_id"] == closure["memory_id"])
            self.assertEqual(row["kind"], "SCIENTIFIC_CLOSURE")
            self.assertEqual(row["source_artifact"], "p0_principle_closure_registry")
            self.assertEqual(row["affected_layer"], "core_principle")
            self.assertEqual(row["memory_class"], "PRINCIPLE_DEAD_END")
            self.assertTrue(row["scientific_dead_end_certified"])
            self.assertTrue(row["principle_update_allowed"])
            self.assertTrue(row["prompt_eligible"])
            self.assertEqual(row["scope"], closure["scope"])
            self.assertEqual(row["reopen_condition"], closure["counter_explanation"]["reopen_condition"])
            self.assertEqual(row["opposite_search_seed"], closure["counter_explanation"]["opposite_search_seed"])
            self.assertEqual(row["source_refs"], sorted(closure["source_refs"]))
            self.assertFalse(row["scientific_authority"])

    def test_query_pack_uses_closure_as_context_not_global_veto_or_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            closure = self.closure(Path(td))
            wiki = self.build_base(principle_closure_registry=[closure])
            pack = compile_research_memory_query_pack(
                wiki,
                purpose="IDEA_SEARCH",
                context={"title": closure["title"], "scope": closure["scope"]},
                max_chars=8000,
                max_items=32,
            )
            self.assertIn(closure["memory_id"], pack["selected_memory_ids"])
            self.assertIn(closure["counter_explanation"]["reopen_condition"], pack["text"])
            self.assertTrue(pack["policy"]["past_failure_is_not_automatic_veto"])
            self.assertTrue(pack["policy"]["reopen_condition_requires_new_evidence"])
            self.assertTrue(pack["policy"]["downstream_scientific_gates_unchanged"])
            self.assertFalse(pack["scientific_authority"])
            self.assertNotIn("automatic_global_blacklist_authorized", json.dumps(pack))

    def test_multiple_persisted_closures_do_not_change_adjacent_source_objects(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            closure = self.closure(Path(td))
            second = dict(closure)
            second["memory_id"] = closure["memory_id"] + "-SECOND"
            second["source_candidate_id"] = closure["source_candidate_id"] + "-SECOND"
            second["title"] = closure["title"] + " (second scope)"
            second["scope"] = closure["scope"] + " Second frozen scope only."
            second["counter_explanation"] = dict(closure["counter_explanation"])
            second["counter_explanation"]["scope"] = second["scope"]
            wiki = self.build_base(principle_closure_registry=[closure, second])
            self.assertEqual(wiki["source_manifest"]["p0_principle_closures"], 2)
            self.assertEqual(wiki["summary"]["scientific_closures"], 2)
            self.assertEqual(wiki["summary"]["search_closures"], 1)
            existing = next(item for item in wiki["entries"] if item["kind"] == "SEARCH_CLOSURE")
            self.assertFalse(existing["principle_update_allowed"])
            self.assertEqual(existing["source_artifact"], "shadow_search_memory")
            self.assertEqual(wiki["lint"]["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
