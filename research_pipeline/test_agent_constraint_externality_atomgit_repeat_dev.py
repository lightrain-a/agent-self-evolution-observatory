from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_build import (
    CONTRACT_OUTPUT,
    DIRECT_LEDGER,
    OUTPUT_BUNDLE,
    QUAL_OUTPUT,
    _completion_rows,
    load_dev_spec,
)
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_family import (
    SELECTION_SALT,
    family_from_case,
    select_case_ids,
)
from research_pipeline.agent_constraint_externality_direct_sfq_a0_build import (
    OUTPUT_BUNDLE as DIRECT_BUNDLE,
    load_cases as load_direct_cases,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value
from research_pipeline.appworld_constraint_compiler import validate_family

APPWORLD_ROOT = Path(
    "/data/wyt/agent-self-evolution-observatory/worktrees/agent-constraint-externality-20260831/cache/substrates/appworld-official-20260831"
)
EXPECTED_SELECTED = [
    "DIRECT-SFQ-A0-FG-06",
    "DIRECT-SFQ-A0-FG-03",
    "DIRECT-SFQ-A0-FG-05",
    "DIRECT-SFQ-A0-TNF-02",
    "DIRECT-SFQ-A0-TNF-01",
    "DIRECT-SFQ-A0-TNF-05",
]


class AtomGitRepeatDevStaticTest(unittest.TestCase):
    def test_stable_selection_is_frozen_and_balanced(self) -> None:
        selected, ranking = select_case_ids(_completion_rows())
        self.assertEqual(selected, EXPECTED_SELECTED)
        self.assertEqual(SELECTION_SALT, "ACE-REPEAT-DEVELOPMENT-SELECTION-20260906-V1")
        self.assertEqual(sum("-FG-" in x for x in selected), 3)
        self.assertEqual(sum("-TNF-" in x for x in selected), 3)
        self.assertEqual(sum(bool(x["selected"]) for x in ranking), 6)

    def test_family_topology_and_matching_are_exact(self) -> None:
        cases = {row["case_id"]: row for row in load_direct_cases(DIRECT_BUNDLE)}
        for ordinal, case_id in enumerate(EXPECTED_SELECTED, 1):
            family = family_from_case(cases[case_id], ordinal)
            arms = {row["coupling_level"]: row for row in family["arms"]}
            self.assertEqual(set(arms), {"INDEPENDENT", "LOW", "HIGH"})
            target_hashes = {
                sha256_value(next(c for c in arm["constraints"] if c["role"] == "TARGET"))
                for arm in arms.values()
            }
            self.assertEqual(len(target_hashes), 1)
            self.assertEqual(family["source_case"]["task_instruction"], family["target_instruction"])
            self.assertEqual(
                len({len(arm["task_instruction"].encode("utf-8")) for arm in arms.values()}), 1
            )
            self.assertEqual(
                len({len(arm["task_instruction"].split()) for arm in arms.values()}), 1
            )
            with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-test-") as d:
                summary = validate_family(family, APPWORLD_ROOT, Path(d))
            self.assertEqual(
                summary["shared_resource_exposure"],
                {"INDEPENDENT": 0, "LOW": 1, "HIGH": 2},
            )
            self.assertTrue(summary["initial_non_target_constraints_satisfied"])

    def test_frozen_artifacts_keep_zero_execution_authority(self) -> None:
        contract = json.loads(CONTRACT_OUTPUT.read_text(encoding="utf-8"))
        qualification = json.loads(QUAL_OUTPUT.read_text(encoding="utf-8"))
        claimed_contract = contract.pop("content_sha256")
        claimed_qualification = qualification.pop("content_sha256")
        self.assertEqual(sha256_value(contract), claimed_contract)
        self.assertEqual(sha256_value(qualification), claimed_qualification)
        contract["content_sha256"] = claimed_contract
        qualification["content_sha256"] = claimed_qualification
        self.assertEqual(
            qualification["status"],
            "ATOMGIT_REPEAT_DEV_STATIC_QUALIFICATION_PASS_EXECUTION_CLOSED",
        )
        self.assertEqual(contract["selection"]["selected_case_ids"], EXPECTED_SELECTED)
        self.assertEqual(contract["provider_requests_created"], 0)
        self.assertEqual(qualification["provider_requests_created"], 0)
        self.assertTrue(contract["permanently_excluded_from_confirmatory"])
        self.assertFalse(contract["source_policy"]["old_direct_sfq_calls_count_as_new_source_units"])
        self.assertTrue(all(v is False for v in contract["authority"].values()))
        self.assertTrue(all(v is False for v in qualification["authority"].values()))
        replay = load_dev_spec()
        self.assertEqual(replay["family_count"], 6)
        self.assertEqual(
            sha256_value(replay["families"]),
            sha256_value(load_dev_spec()["families"]),
        )

    def test_parent_ledger_is_bound_and_complete(self) -> None:
        self.assertTrue(DIRECT_LEDGER.is_file())
        rows = _completion_rows()
        self.assertEqual(len(rows), 12)
        self.assertEqual(sum(bool(row["usable_target_failure"]) for row in rows), 9)
        self.assertEqual(sum(bool(row["target_success"]) for row in rows), 3)
        self.assertEqual(sum(bool(row.get("technical_failure")) for row in rows), 0)


if __name__ == "__main__":
    unittest.main()
