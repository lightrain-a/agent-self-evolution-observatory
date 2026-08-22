from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .reopened_p0_principle_memory_authorization import build_principle_memory_authorization, build_principle_memory_handoff
from .reopened_principle_memory_closure import (
    STATUS,
    build_principle_scientific_closure,
    load_principle_closures,
    public_principle_closure_summary,
    publish_principle_scientific_closure,
    validate_principle_closure_ledger,
    validate_principle_scientific_closure,
)
from .test_reopened_p0_principle_memory_authorization import ReopenedP0PrincipleMemoryAuthorizationTest


class ReopenedPrincipleMemoryClosureTest(unittest.TestCase):
    def handoff(self, root: Path):
        helper = ReopenedP0PrincipleMemoryAuthorizationTest(methodName="test_memory_handoff_is_scoped_core_principle_closure_but_not_automatic_write")
        principle_handoff = helper.dead_end_handoff(root)
        authorization = build_principle_memory_authorization(
            principle_handoff=principle_handoff,
            external_authority_ref="pi:closure-authority",
            authorized_at="2027-04-12T12:00:00+00:00",
        )
        return build_principle_memory_handoff(
            principle_handoff=principle_handoff,
            authorization=authorization,
            memory_spec=helper.memory_spec(principle_handoff),
        )

    def test_persisted_closure_is_scoped_reopenable_and_zero_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.handoff(root)
            closure = build_principle_scientific_closure(memory_handoff=handoff, persisted_at="2027-04-13T12:00:00+00:00")
            self.assertTrue(validate_principle_scientific_closure(closure))
            self.assertEqual(closure["status"], STATUS)
            self.assertEqual(closure["failure_layer"], "core_principle")
            self.assertTrue(closure["dead_end_certified"])
            self.assertTrue(closure["principle_update_allowed"])
            self.assertTrue(closure["scope_match_required_for_reuse"])
            self.assertTrue(closure["reopen_condition_required_for_reentry"])
            self.assertTrue(closure["automatic_global_blacklist_forbidden"])
            self.assertTrue(closure["adjacent_scientific_objects_remain_open"])
            self.assertFalse(closure["parent_paper_claim_update_authorized"])
            self.assertFalse(closure["scientific_authority"])

    def test_persist_is_append_only_idempotent_and_loadable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); closure = build_principle_scientific_closure(memory_handoff=self.handoff(root), persisted_at="2027-04-13T12:00:00+00:00")
            first = publish_principle_scientific_closure(root, closure)
            second = publish_principle_scientific_closure(root, closure)
            self.assertEqual(len(first["events"]), 1)
            self.assertEqual(len(second["events"]), 1)
            self.assertEqual(validate_principle_closure_ledger(second), [])
            rows = load_principle_closures(root)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["principle_closure_sha256"], closure["principle_closure_sha256"])
            summary = public_principle_closure_summary(root)
            self.assertEqual(summary["scientific_closures"], 1)
            self.assertTrue(summary["all_scope_bound"])
            self.assertTrue(summary["all_reopenable"])
            self.assertFalse(summary["automatic_global_blacklist_authorized"])

    def test_closure_requires_reopen_condition_and_source_refs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); handoff = self.handoff(root)
            bad = copy.deepcopy(handoff); bad["memory_spec"]["reopen_condition"] = ""
            bad["memory_spec_sha256"] = "broken"
            with self.assertRaisesRegex(RuntimeError, "valid Research Memory principle handoff"):
                build_principle_scientific_closure(memory_handoff=bad, persisted_at="2027-04-13T12:00:00+00:00")

    def test_tamper_or_global_authority_upgrade_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); closure = build_principle_scientific_closure(memory_handoff=self.handoff(root), persisted_at="2027-04-13T12:00:00+00:00")
            bad = copy.deepcopy(closure); bad["automatic_global_blacklist_forbidden"] = False
            self.assertFalse(validate_principle_scientific_closure(bad))
            ledger = publish_principle_scientific_closure(root, closure)
            ledger["authority"]["scientific"] = True
            self.assertIn("principle-closure-ledger-authority-leak", validate_principle_closure_ledger(ledger))

    def test_public_summary_does_not_expose_private_human_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); closure = build_principle_scientific_closure(memory_handoff=self.handoff(root), persisted_at="2027-04-13T12:00:00+00:00")
            publish_principle_scientific_closure(root, closure)
            public = public_principle_closure_summary(root)
            raw = json.dumps(public)
            self.assertNotIn("pi:closure-authority", raw)
            self.assertNotIn("external_authority_ref", raw)


if __name__ == "__main__":
    unittest.main()
