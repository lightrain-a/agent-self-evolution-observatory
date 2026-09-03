from __future__ import annotations

import json

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh3_source_schedule_20260903 as s
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_all_frozen_inputs_are_content_addressed() -> None:
    assert sha256_file(s.POOL) == s.POOL_SHA
    assert sha256_file(s.SPLIT) == s.SPLIT_SHA
    assert sha256_file(s.PROBES) == s.PROBES_SHA
    assert sha256_file(s.Q02) == s.Q02_SHA
    assert sha256_file(s.Q03) == s.Q03_SHA


def test_q02_and_q03_authority_are_required() -> None:
    q02 = json.loads(s.Q02.read_text()); q03 = json.loads(s.Q03.read_text())
    assert q02["status"] == "ATOMGIT_QWEN38_Q02_SOURCE_BUDGET_PASS"
    assert q02["selected_source_budget"] == 32768
    assert q02["invocation_timeout_seconds"] == 900
    assert q03["status"] == "ATOMGIT_QWEN38_Q03_TEXT_BRIDGE_PASS"
    assert q03["fresh3_authorized"] is True


def test_schedule_is_ten_unique_exactly_once_sources() -> None:
    row = s.prepare(); rows = row["rows"]
    assert row["status"] == "FRESH3_SOURCE_SCHEDULE_FROZEN_PRE_SOURCE_OUTCOME"
    assert len(rows) == 10 and len({r["source_task_id"] for r in rows}) == 10
    assert [r["sequence"] for r in rows] == list(range(1, 11))
    assert all(r["logical_attempts"] == 1 for r in rows)
    assert all(r["replacement"] is False for r in rows)
    assert all(r["future_task_executed"] is False for r in rows)
    assert row["source_max_completion_tokens"] == 32768
    assert row["atomcode_subprocess_timeout_seconds"] == 900
    assert row["first_decision_budget"] == 2048
    assert row["bridge_schema"] == "c1-minisweagent-ordinary-json-text-bridge-v1"


def test_schedule_is_deterministic() -> None:
    a = s.prepare()["rows"]; b = s.prepare()["rows"]
    assert a == b
