#!/usr/bin/env python3
"""Minimal Ark embedding adapter for ReasoningBank retrieval qualification."""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from research_pipeline.asset_first_stri_reasoningbank_ark_provider import (
    ArkReasoningBankSettings,
    CANONICAL_SECRET_FILE,
)


EMBEDDING_URL = "https://ark.cn-beijing.volces.com/api/v3/embeddings"
EMBEDDING_MODEL = "doubao-embedding-large-text-250515"


class ArkEmbeddingError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str = "",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body_sha256 = hashlib.sha256(
            response_body.encode("utf-8")
        ).hexdigest()

    def safe_receipt(self) -> dict[str, Any]:
        return {
            "error_type": type(self).__name__,
            "status_code": self.status_code,
            "response_body_sha256": self.response_body_sha256,
            "credential_material_present": False,
        }


@dataclass(frozen=True)
class ArkEmbeddingSettings:
    api_key: str
    url: str = EMBEDDING_URL
    model: str = EMBEDDING_MODEL
    timeout_seconds: float = 120.0
    max_retries: int = 2

    @classmethod
    def from_env_file(
        cls, path: Path = CANONICAL_SECRET_FILE
    ) -> "ArkEmbeddingSettings":
        base = ArkReasoningBankSettings.from_env_file(path)
        return cls(
            api_key=base.api_key,
            timeout_seconds=base.timeout_seconds,
            max_retries=base.max_retries,
        )

    def safe_summary(self) -> dict[str, Any]:
        return {
            "configured": bool(self.api_key),
            "url": self.url,
            "model": self.model,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "secret_value_exported": False,
        }


class ArkEmbeddingClient:
    def __init__(
        self,
        settings: ArkEmbeddingSettings,
        *,
        session: requests.Session | None = None,
    ) -> None:
        self.settings = settings
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json",
            }
        )

    def embed(self, inputs: list[str]) -> dict[str, Any]:
        body = {
            "model": self.settings.model,
            "input": inputs,
            "encoding_format": "float",
        }
        response = None
        for attempt in range(self.settings.max_retries + 1):
            response = self.session.post(
                self.settings.url,
                json=body,
                timeout=self.settings.timeout_seconds,
            )
            if response.status_code < 500:
                break
            if attempt < self.settings.max_retries:
                time.sleep(2**attempt)
        assert response is not None
        if response.status_code >= 400:
            raise ArkEmbeddingError(
                "Ark embedding request failed",
                status_code=response.status_code,
                response_body=response.text,
            )
        try:
            payload = response.json()
            data = payload["data"]
            ordered = sorted(data, key=lambda row: int(row["index"]))
            vectors = [[float(value) for value in row["embedding"]] for row in ordered]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ArkEmbeddingError(
                "Ark embedding response schema mismatch",
                status_code=response.status_code,
                response_body=response.text,
            ) from error
        if len(vectors) != len(inputs):
            raise ArkEmbeddingError(
                "Ark embedding response count mismatch",
                status_code=response.status_code,
                response_body=response.text,
            )
        if not vectors or any(not vector for vector in vectors):
            raise ArkEmbeddingError(
                "Ark embedding response contained an empty vector",
                status_code=response.status_code,
                response_body=response.text,
            )
        if any(not math.isfinite(value) for vector in vectors for value in vector):
            raise ArkEmbeddingError(
                "Ark embedding response contained a non-finite value",
                status_code=response.status_code,
                response_body=response.text,
            )
        return {
            "requested_model": self.settings.model,
            "resolved_model": payload.get("model"),
            "vectors": vectors,
            "usage": payload.get("usage") or {},
            "object": payload.get("object"),
        }
