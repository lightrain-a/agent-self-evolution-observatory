from __future__ import annotations
import json
import pytest
import research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_q1 as q1


def test_plan_and_request():
    assert q1.K_Q1 == 20
    sampling = {"temperature": 1.0, "top_p": .95, "top_k": 40,
                "max_output_tokens": 32768, "max_retries": 0}
    body = q1.request_body(sampling)
    assert (body["model"], body["temperature"], body["top_p"], body["top_k"]) == (
        "qwen3-coder-next", 1.0, .95, 40)
    sampling["top_k"] = "OMITTED_UNPROVEN_OR_UNSUPPORTED"
    assert "top_k" not in q1.request_body(sampling)


@pytest.mark.parametrize(("text", "valid", "kind"), [
    (q1.FENCE + "bash\nprintf Q1_FIXED_ACTION\n" + q1.FENCE, True, "OTHER"),
    (q1.FENCE + "bash\nrg needle src/pkg.py\n" + q1.FENCE, True, "SEARCH"),
    (q1.FENCE + "bash\nsed -n '1,10p' src/pkg.py\n" + q1.FENCE, True, "READ"),
    ("not an action", False, "PARSE_INVALID"),
    (q1.FENCE + "bash\nls src\n" + q1.FENCE + "\n" +
     q1.FENCE + "bash\nls tests\n" + q1.FENCE, False, "PARSE_INVALID"),
])
def test_normalize_action(text, valid, kind):
    actual = q1.normalize_action(text)
    assert actual["parse_valid"] is valid
    assert actual["action_class"] == kind
    assert len(actual["signature_sha256"]) == 64


def test_q0_and_pin_gates(tmp_path, monkeypatch):
    path = tmp_path / "q0.json"
    path.write_text(json.dumps({"decision": "Q0_QWEN3_CODER_NEXT_PROVIDER_CAPABILITY_HOLD"}))
    monkeypatch.setattr(q1, "Q0_RESULT", path)
    with pytest.raises(RuntimeError, match="did not authorize"):
        q1.load_q0()
    monkeypatch.setattr(q1, "EXPECTED_CONTRACT_SHA256", "PENDING")
    with pytest.raises(RuntimeError, match="not pinned"):
        q1.execute(tmp_path / "out.json")
