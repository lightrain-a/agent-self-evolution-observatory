from __future__ import annotations

import research_pipeline.asset_first_stri_swebench_aria2_acquire as acquire


class FakeResponse:
    def __init__(self, status_code, *, headers=None, payload=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.payload = payload or {}
        self.closed = False

    def close(self):
        self.closed = True

    def json(self):
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_signed_url_accepts_direct_blob_response(monkeypatch):
    response = FakeResponse(200)
    monkeypatch.setattr(acquire.requests, "get", lambda *args, **kwargs: response)
    expected = "https://mirror.test/v2/repo/name/blobs/sha256:abc"
    monkeypatch.setattr(acquire, "BASE", "https://mirror.test")
    assert acquire.signed_url("repo/name", "sha256:abc") == expected
    assert response.closed is True


def test_signed_url_accepts_registry_redirect(monkeypatch):
    response = FakeResponse(307, headers={"location": "https://blob.test/exact"})
    monkeypatch.setattr(acquire.requests, "get", lambda *args, **kwargs: response)
    monkeypatch.setattr(acquire, "BASE", "https://mirror.test")
    assert acquire.signed_url("repo/name", "sha256:abc") == "https://blob.test/exact"
    assert response.closed is True


def test_signed_url_uses_real_blob_bearer_challenge(monkeypatch):
    challenge = FakeResponse(401, headers={
        "www-authenticate": 'Bearer realm="https://auth.test/token",service="registry.test"'
    })
    token = FakeResponse(200, payload={"token": "opaque-token"})
    redirect = FakeResponse(302, headers={"location": "https://blob.test/exact"})
    responses = iter([challenge, token, redirect])
    calls = []

    def fake_get(*args, **kwargs):
        calls.append((args, kwargs))
        return next(responses)

    monkeypatch.setattr(acquire.requests, "get", fake_get)
    monkeypatch.setattr(acquire, "BASE", "https://mirror.test")
    assert acquire.signed_url("repo/name", "sha256:abc") == "https://blob.test/exact"
    assert calls[0][0][0].endswith("/v2/repo/name/blobs/sha256:abc")
    assert calls[1][0][0] == "https://auth.test/token"
    assert calls[2][1]["headers"] == {"Authorization": "Bearer opaque-token"}
    assert challenge.closed is True
    assert redirect.closed is True
