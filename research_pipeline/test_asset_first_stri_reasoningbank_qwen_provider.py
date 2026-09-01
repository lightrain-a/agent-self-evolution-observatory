from __future__ import annotations

import json

import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_provider import (
    DIANMING_BASE_URL,
    MODEL,
    QwenChatClient,
    QwenChatSettings,
    QwenProviderError,
)


class FakeResponse:
    def __init__(self, status_code: int, payload: dict, headers: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = ""
        self.headers = headers or {}

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.headers = {}
        self.requests = []

    def post(self, endpoint, *, json, timeout):
        self.requests.append({"endpoint": endpoint, "json": json, "timeout": timeout})
        return self.responses.pop(0)


def settings(**kwargs):
    base = dict(
        api_key="SECRET_SENTINEL",
        base_url=DIANMING_BASE_URL,
        model=MODEL,
        timeout_seconds=7.0,
        max_retries=0,
    )
    base.update(kwargs)
    return QwenChatSettings(**base)


def payload(text="OK", *, finish_reason="stop", tool_calls=None):
    message = {"role": "assistant", "content": text}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return {
        "id": "chatcmpl-receipt",
        "object": "chat.completion",
        "created": 1,
        "model": MODEL,
        "choices": [{"index": 0, "message": message, "finish_reason": finish_reason}],
        "usage": {"prompt_tokens": 9, "completion_tokens": 3, "total_tokens": 12},
    }


def test_exact_endpoint_and_safe_summary():
    s = settings()
    assert s.endpoint == "https://api.aa.com.cn/api/v1/chat/completions"
    summary = s.safe_summary()
    assert summary["model"] == MODEL
    assert "SECRET_SENTINEL" not in str(summary)
    assert summary["secret_value_exported"] is False


def test_chat_request_uses_messages_n1_and_actual_parameter_names():
    session = FakeSession([FakeResponse(200, payload())])
    client = QwenChatClient(settings(), session=session)
    out = client.create_response(
        input_items=[{"role": "user", "content": "hello"}],
        model=MODEL,
        max_output_tokens=123,
        temperature=1.0,
        top_p=.95,
        top_k=40,
        seed=731,
        stop=["END"],
        store=True,
    )
    request = session.requests[0]
    assert request["endpoint"] == "https://api.aa.com.cn/api/v1/chat/completions"
    body = request["json"]
    assert body == {
        "model": MODEL,
        "messages": [{"role": "user", "content": "hello"}],
        "n": 1,
        "stream": False,
        "max_completion_tokens": 123,
        "temperature": 1.0,
        "top_p": .95,
        "top_k": 40,
        "seed": 731,
        "stop": ["END"],
    }
    assert out["actual_request"] == body
    assert out["choice_count"] == 1
    assert out["text"] == "OK"
    assert out["usage"]["input_tokens"] == 9
    assert out["usage"]["output_tokens"] == 3


def test_instructions_become_system_message_without_rewriting_history():
    session = FakeSession([FakeResponse(200, payload())])
    client = QwenChatClient(settings(), session=session)
    history = [
        {"role": "user", "content": "one"},
        {"role": "assistant", "content": "two"},
        {"role": "user", "content": "three"},
    ]
    client.create_response(input_items=history, instructions="SYSTEM")
    assert session.requests[0]["json"]["messages"] == [
        {"role": "system", "content": "SYSTEM"}, *history
    ]


def test_responses_style_tool_is_converted_to_chat_tool_and_normalized_back():
    tool_calls = [{
        "id": "call-7",
        "type": "function",
        "function": {"name": "record_probe", "arguments": '{"value":731}'},
    }]
    session = FakeSession([FakeResponse(200, payload("", tool_calls=tool_calls))])
    client = QwenChatClient(settings(), session=session)
    out = client.create_response(
        input_items="call tool",
        tools=[{
            "type": "function", "name": "record_probe", "description": "record",
            "parameters": {"type": "object", "properties": {"value": {"type": "integer"}}},
        }],
        tool_choice={"type": "function", "function": {"name": "record_probe"}},
    )
    body = session.requests[0]["json"]
    sent = body["tools"][0]
    assert sent["type"] == "function"
    assert sent["function"]["name"] == "record_probe"
    assert "strict" not in sent["function"]
    assert body["tool_choice"] == {"type": "function", "function": {"name": "record_probe"}}
    assert out["function_calls"] == [{
        "type": "function_call", "call_id": "call-7", "name": "record_probe",
        "arguments": '{"value":731}',
    }]


def test_previous_response_is_fail_closed_without_provider_call():
    session = FakeSession([])
    client = QwenChatClient(settings(), session=session)
    with pytest.raises(QwenProviderError, match="previous_response_id") as caught:
        client.create_response(input_items="x", previous_response_id="resp-1")
    assert caught.value.status_code == 400
    assert session.requests == []


def test_multiple_choices_are_rejected_even_if_provider_ignores_n1():
    bad = payload()
    bad["choices"].append(json.loads(json.dumps(bad["choices"][0])))
    session = FakeSession([FakeResponse(200, bad)])
    client = QwenChatClient(settings(), session=session)
    with pytest.raises(QwenProviderError, match="exactly one choice"):
        client.create_response(input_items="x")
    assert session.requests[0]["json"]["n"] == 1


def test_only_safe_headers_and_errors_are_persisted():
    response = FakeResponse(
        200,
        payload(),
        headers={
            "X-RateLimit-Remaining-Requests": "17",
            "X-Request-Id": "req-1",
            "Authorization": "SECRET_SENTINEL",
            "Set-Cookie": "private",
        },
    )
    client = QwenChatClient(settings(), session=FakeSession([response]))
    out = client.create_response(input_items="x")
    assert out["response_headers"] == {
        "x-ratelimit-remaining-requests": "17", "x-request-id": "req-1"
    }
    assert "SECRET_SENTINEL" not in str(out)

    error_session = FakeSession([FakeResponse(400, {
        "error": {"message": "bad", "authorization": "SECRET_SENTINEL"}
    })])
    client = QwenChatClient(settings(), session=error_session)
    with pytest.raises(QwenProviderError) as caught:
        client.create_response(input_items="x")
    assert "SECRET_SENTINEL" not in str(caught.value.safe_receipt())


def test_no_hidden_retry_when_max_retries_zero():
    session = FakeSession([FakeResponse(503, {"error": {"message": "temporary"}})])
    client = QwenChatClient(settings(max_retries=0), session=session)
    with pytest.raises(QwenProviderError):
        client.create_response(input_items="x")
    assert len(session.requests) == 1
