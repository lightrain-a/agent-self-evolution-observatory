from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_f0_browser import format_listener
from .paper_first_agent_safety_r9_f0_journal import (
    begin,
    inconclusive,
    load_journal,
    recover_classifier_realization,
    reserve_agent,
    reserve_classifier,
)


class R9F0RuntimeTest(unittest.TestCase):
    def test_journal_enforces_episode_and_classifier_caps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            plan = {"plan_sha256": "abc"}
            journal = load_journal(out, plan)
            spec = {"episode_id": "e1", "max_agent_model_calls": 4}
            ep = begin(out, journal, spec)
            for _ in range(4):
                reserve_agent(out, journal, ep)
            with self.assertRaisesRegex(RuntimeError, "episode agent cap exceeded"):
                reserve_agent(out, journal, ep)
            reserve_classifier(out, journal, ep)
            with self.assertRaisesRegex(RuntimeError, "classifier retry forbidden"):
                reserve_classifier(out, journal, ep)
            self.assertEqual(journal["counters"]["agent_model_calls_reserved"], 4)
            self.assertEqual(journal["counters"]["classifier_evaluations_reserved"], 1)

    def test_classifier_realization_recovery_reuses_existing_reservation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp); plan = {"plan_sha256": "abc"}
            journal = load_journal(out, plan)
            ep = begin(out, journal, {"episode_id": "e1", "max_agent_model_calls": 4})
            reserve_classifier(out, journal, ep)
            inconclusive(out, journal, ep, "HTTPError:400 before model inference")
            recover_classifier_realization(
                out, journal, ep, prediction=0, raw_label="No", text="frozen text", source="thought-fallback",
                recovery={"classifier_service_counter_before": 2, "classifier_service_counter_after": 3},
            )
            self.assertEqual(ep["status"], "completed")
            self.assertTrue(ep["realization_recovered"])
            self.assertEqual(ep["prior_protocol_inconclusive"]["reason"], "HTTPError:400 before model inference")
            self.assertEqual(journal["counters"]["classifier_evaluations_reserved"], 1)
            self.assertEqual(journal["counters"]["protocol_inconclusive_episodes"], 0)
            self.assertEqual(journal["counters"]["completed_episodes"], 1)
            self.assertEqual(journal["status"], "R9_F0_RUNTIME_JOURNAL_ACTIVE")

    def test_begin_forbids_episode_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp); plan = {"plan_sha256": "abc"}
            journal = load_journal(out, plan)
            begin(out, journal, {"episode_id": "e1", "max_agent_model_calls": 4})
            with self.assertRaisesRegex(RuntimeError, "episode rerun forbidden"):
                begin(out, journal, {"episode_id": "e1", "max_agent_model_calls": 4})

    def test_browserart_listener_formatters_match_official_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            twitter = root / "twitter.txt"; twitter.write_text("hello\nworld\n", encoding="utf-8")
            self.assertEqual(format_listener(twitter, "local:twitter"), "hello\nworld\n")
            email = root / "email.json"; email.write_text(json.dumps([{"to": "x", "subject": "s"}, {"to": "y"}]), encoding="utf-8")
            self.assertEqual(json.loads(format_listener(email, "local:email")), {"to": "x", "subject": "s"})


if __name__ == "__main__":
    unittest.main()
