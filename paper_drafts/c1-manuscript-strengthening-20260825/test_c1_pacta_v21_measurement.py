from __future__ import annotations

import json
from pathlib import Path

import c1_pacta_v21_first_action_parser as parser
import qualify_c1_pacta_v21_measurement_20260831 as qualification


def test_strict_and_positive_recovery():
    strict='{"current_state":{"x":"ok"},"action":[{"wait":{"seconds":1}}]}'
    result=parser.parse_first_action(strict)
    assert result.signature=="wait"
    assert result.mode=="strict_full_envelope"
    for _,text,expected in qualification.positive_fixtures():
        recovered=parser.parse_first_action(text)
        assert recovered.signature==expected
        assert recovered.mode=="first_action_only_recovery"


def test_negative_fixtures_fail_closed():
    for _,text,_ in qualification.negative_fixtures():
        try:
            parser.parse_first_action(text)
        except parser.FirstActionParseError:
            continue
        raise AssertionError("negative fixture did not fail closed")


def test_string_aware_scanner_ignores_action_text_inside_string():
    text='{"note":"fake \\"action\\":[{\\"wait\\":{}}]","action":[{"go_back":{}}]} trailing'
    result=parser.parse_first_action(text)
    assert result.signature=="go_back"
    assert result.mode=="first_action_only_recovery"


def test_archived_replay_inventory_is_complete():
    rows,counts=qualification.archived_rows()
    assert len(rows)==636
    assert counts["B10"]["signature_only"]==432
    assert counts["B10"]["raw_available"]==0
    assert counts["R9_SCMB"]["clean_raw_available"]==432
    assert counts["PACTA_V2_SHADOW"]["clean_raw_available"]==144
    assert counts["PACTA_V2_CLEAN_FINAL"]["clean_raw_available"]==60
