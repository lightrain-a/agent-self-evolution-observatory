from __future__ import annotations

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from .paper_first_external_asset_audit import build_external_asset_audit, validate_external_asset_audit
from .paper_first_external_paper_identity import build_external_paper_identity_receipt


def atom(arxiv_id: str, title: str) -> str:
    return f'''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
<id>https://arxiv.org/abs/{arxiv_id}v1</id><title>{title}</title>
<summary>Primary abstract.</summary><published>2026-08-16T00:00:00Z</published>
</entry></feed>'''


class ExternalAssetAuditTest(unittest.TestCase):
    def now(self) -> datetime:
        return datetime(2026, 8, 18, tzinfo=timezone.utc)

    def identity(self, *, claimed_title: str, official_title: str, arxiv_id: str = "2608.14744", search_text: str | None = None) -> dict:
        def by_id(**kwargs):
            return SimpleNamespace(status_code=200, text=atom(arxiv_id, official_title))

        def by_title(**kwargs):
            return SimpleNamespace(status_code=200, text=search_text or '<feed xmlns="http://www.w3.org/2005/Atom"></feed>')

        return build_external_paper_identity_receipt(
            claimed_title=claimed_title,
            claimed_ref=f"arXiv:{arxiv_id}",
            requester=by_id,
            title_search_requester=by_title,
            now=self.now(),
        )

    def test_unverified_identity_blocks_before_any_network_asset_probe(self) -> None:
        receipt = self.identity(
            claimed_title="Great Theorem Prover",
            official_title="Iterative Refinement Diffusion for Super-Resolved Data Assimilation of Multiscale Physical Systems",
        )
        calls = []

        def fetcher(**kwargs):
            calls.append(kwargs)
            raise AssertionError("network asset probe must not run")

        state = build_external_asset_audit(identity_receipt=receipt, fetcher=fetcher, now=self.now())
        self.assertEqual(state["status"], "HOLD_BIBLIOGRAPHIC_IDENTITY")
        self.assertEqual(calls, [])
        self.assertEqual(state["declared_asset_endpoints"], [])
        self.assertFalse(state["asset_content_review_authorized"])
        self.assertEqual(validate_external_asset_audit(state), [])

    def test_verified_identity_forwards_only_primary_declared_asset_hosts(self) -> None:
        title = "A Verified Lean Prover"
        receipt = self.identity(claimed_title=title, official_title=title, arxiv_id="2608.19999")
        page = '''<html><body>
          <a href="https://github.com/example/lean-prover/tree/main">Code</a>
          <a href="https://huggingface.co/example/lean-prover">Model</a>
          <a href="https://example.github.io/lean-prover/">Project</a>
          <a href="https://unrelated.example.org/tool">Other</a>
          <a href="https://arxiv.org/pdf/2608.19999">PDF</a>
        </body></html>'''

        def fetcher(**kwargs):
            self.assertEqual(kwargs["url"], "https://arxiv.org/abs/2608.19999")
            return SimpleNamespace(status_code=200, text=page, url=kwargs["url"])

        state = build_external_asset_audit(identity_receipt=receipt, fetcher=fetcher, now=self.now())
        self.assertEqual(state["status"], "READY_FOR_DECLARED_ASSET_CONTENT_REVIEW")
        self.assertTrue(state["asset_content_review_authorized"])
        self.assertEqual(state["summary"]["declared_asset_endpoints"], 3)
        self.assertEqual(state["summary"]["github_endpoints"], 1)
        self.assertEqual(state["summary"]["huggingface_endpoints"], 1)
        self.assertEqual(state["summary"]["project_page_endpoints"], 1)
        urls = {row["url"] for row in state["declared_asset_endpoints"]}
        self.assertIn("https://github.com/example/lean-prover", urls)
        self.assertIn("https://huggingface.co/example/lean-prover", urls)
        self.assertIn("https://example.github.io/lean-prover", urls)
        self.assertNotIn("https://unrelated.example.org/tool", urls)
        self.assertEqual(validate_external_asset_audit(state), [])
        for key in ("provider_calls_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized", "scientific_authority"):
            self.assertFalse(state[key])

    def test_verified_identity_without_declared_assets_is_not_a_scientific_negative(self) -> None:
        title = "A Verified Lean Prover"
        receipt = self.identity(claimed_title=title, official_title=title, arxiv_id="2608.19999")

        def fetcher(**kwargs):
            return SimpleNamespace(status_code=200, text='<html><a href="https://arxiv.org/pdf/2608.19999">PDF</a></html>', url=kwargs["url"])

        state = build_external_asset_audit(identity_receipt=receipt, fetcher=fetcher, now=self.now())
        self.assertEqual(state["status"], "VERIFIED_IDENTITY_NO_DECLARED_ASSET_ENDPOINTS")
        self.assertEqual(state["declared_asset_endpoints"], [])
        self.assertFalse(state["asset_content_review_authorized"])
        self.assertTrue(state["policy"]["no_declared_endpoint_is_evidence_absence_not_scientific_negative"])
        self.assertFalse(state["scientific_authority"])
        self.assertEqual(validate_external_asset_audit(state), [])


if __name__ == "__main__":
    unittest.main()
