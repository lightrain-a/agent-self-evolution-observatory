from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from .paper_first_external_paper_identity import (
    TITLE_MATCH_THRESHOLD,
    build_external_paper_identity_receipt,
    normalize_arxiv_ref,
    validate_external_paper_identity_receipt,
    write_external_paper_identity_receipt,
)


def atom(arxiv_id: str, title: str) -> str:
    return f'''<feed xmlns="http://www.w3.org/2005/Atom">
<entry>
<id>https://arxiv.org/abs/{arxiv_id}v1</id>
<title>{title}</title>
<summary>Primary abstract for identity verification.</summary>
<published>2026-08-16T00:00:00Z</published>
</entry>
</feed>'''


class ExternalPaperIdentityTest(unittest.TestCase):
    def now(self) -> datetime:
        return datetime(2026, 8, 18, tzinfo=timezone.utc)

    def requester(self, arxiv_id: str, title: str):
        def _requester(**kwargs):
            self.assertEqual(kwargs["arxiv_id"], arxiv_id)
            return SimpleNamespace(status_code=200, text=atom(arxiv_id, title))
        return _requester

    def empty_title_search(self, **kwargs):
        return SimpleNamespace(status_code=200, text='<feed xmlns="http://www.w3.org/2005/Atom"></feed>')

    def title_search(self, arxiv_id: str, title: str):
        def _requester(**kwargs):
            return SimpleNamespace(status_code=200, text=atom(arxiv_id, title))
        return _requester

    def test_normalize_arxiv_ref_accepts_versioned_and_prefixed_ids(self) -> None:
        self.assertEqual(normalize_arxiv_ref("arXiv:2608.14744v2"), ("arXiv:2608.14744", "2608.14744"))
        self.assertEqual(normalize_arxiv_ref("2608.14744"), ("arXiv:2608.14744", "2608.14744"))
        self.assertEqual(normalize_arxiv_ref("not-an-arxiv-id"), ("", ""))

    def test_matching_title_ref_pair_allows_read_only_asset_audit(self) -> None:
        title = "Iterative Refinement Diffusion for Super-Resolved Data Assimilation of Multiscale Physical Systems"
        state = build_external_paper_identity_receipt(
            claimed_title=title,
            claimed_ref="arXiv:2608.14744",
            requester=self.requester("2608.14744", title),
            now=self.now(),
        )
        self.assertEqual(state["status"], "VERIFIED_BIBLIOGRAPHIC_IDENTITY")
        self.assertTrue(state["asset_audit_authorized"])
        self.assertEqual(state["next_action"], "official-first-party-asset-audit")
        self.assertEqual(state["official_identity"]["ref"], "arXiv:2608.14744")
        self.assertEqual(state["identity_check"]["title_similarity"], 1.0)
        self.assertEqual(validate_external_paper_identity_receipt(state), [])
        for key in ("provider_calls_authorized", "method_authorized", "experiment_authorized", "p0_authorized", "gpu_authorized", "scientific_authority"):
            self.assertFalse(state[key])

    def test_gtp_bad_pair_is_quarantined_and_preserves_resolved_official_identity(self) -> None:
        official = "Iterative Refinement Diffusion for Super-Resolved Data Assimilation of Multiscale Physical Systems"
        state = build_external_paper_identity_receipt(
            claimed_title="Great Theorem Prover",
            claimed_ref="arXiv:2608.14744",
            requester=self.requester("2608.14744", official),
            title_search_requester=self.empty_title_search,
            now=self.now(),
        )
        self.assertEqual(state["status"], "QUARANTINED_TITLE_ARXIV_MISMATCH")
        self.assertFalse(state["asset_audit_authorized"])
        self.assertTrue(state["identity_check"]["ref_resolves"])
        self.assertFalse(state["identity_check"]["claimed_title_matches_resolved_ref"])
        self.assertLess(state["identity_check"]["title_similarity"], TITLE_MATCH_THRESHOLD)
        self.assertEqual(state["official_identity"]["title"], official)
        self.assertEqual(state["next_action"], "recover-primary-paper-identifier")
        self.assertEqual(state["identity_recovery"]["claimed_title_primary_identity_status"], "UNRESOLVED_NO_PRIMARY_TITLE_MATCH")
        self.assertEqual(state["identity_recovery"]["matching_candidate_count"], 0)
        self.assertEqual(validate_external_paper_identity_receipt(state), [])

    def test_mismatch_can_surface_unique_primary_recovery_candidate_without_authorizing_audit(self) -> None:
        official_wrong_ref = "Iterative Refinement Diffusion for Super-Resolved Data Assimilation of Multiscale Physical Systems"
        recovered_title = "Great Theorem Prover"
        state = build_external_paper_identity_receipt(
            claimed_title=recovered_title,
            claimed_ref="arXiv:2608.14744",
            requester=self.requester("2608.14744", official_wrong_ref),
            title_search_requester=self.title_search("2608.19999", recovered_title),
            now=self.now(),
        )
        self.assertEqual(state["status"], "QUARANTINED_TITLE_ARXIV_MISMATCH_RECOVERY_CANDIDATE_FOUND")
        self.assertFalse(state["asset_audit_authorized"])
        self.assertEqual(state["identity_recovery"]["claimed_title_primary_identity_status"], "UNIQUE_RECOVERY_CANDIDATE_FOUND")
        self.assertEqual(state["identity_recovery"]["matching_candidates"][0]["ref"], "arXiv:2608.19999")
        self.assertEqual(state["next_action"], "rebind-to-recovery-candidate-and-reverify")
        self.assertEqual(validate_external_paper_identity_receipt(state), [])

    def test_invalid_or_unreachable_identity_never_allows_asset_audit(self) -> None:
        invalid = build_external_paper_identity_receipt(
            claimed_title="Great Theorem Prover",
            claimed_ref="not-an-id",
            now=self.now(),
        )
        self.assertEqual(invalid["status"], "HOLD_INVALID_PAPER_IDENTITY_INPUT")
        self.assertFalse(invalid["asset_audit_authorized"])

        def failing(**kwargs):
            raise TimeoutError("primary metadata unavailable")

        failed = build_external_paper_identity_receipt(
            claimed_title="Great Theorem Prover",
            claimed_ref="arXiv:2608.14744",
            requester=failing,
            now=self.now(),
        )
        self.assertEqual(failed["status"], "HOLD_PRIMARY_IDENTITY_FETCH_FAILED")
        self.assertFalse(failed["asset_audit_authorized"])
        self.assertEqual(validate_external_paper_identity_receipt(failed), [])

    def test_validator_rejects_authorization_on_mismatch(self) -> None:
        official = "Iterative Refinement Diffusion for Super-Resolved Data Assimilation of Multiscale Physical Systems"
        state = build_external_paper_identity_receipt(
            claimed_title="Great Theorem Prover",
            claimed_ref="arXiv:2608.14744",
            requester=self.requester("2608.14744", official),
            title_search_requester=self.empty_title_search,
            now=self.now(),
        )
        state["asset_audit_authorized"] = True
        self.assertTrue(any("asset audit" in value for value in validate_external_paper_identity_receipt(state)))

    def test_writer_persists_a_content_bound_verified_receipt(self) -> None:
        title = "Paper Identity: A Test"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "identity.json"
            state = write_external_paper_identity_receipt(
                claimed_title="Paper Identity - A Test",
                claimed_ref="arXiv:2608.99999v1",
                path=path,
                requester=self.requester("2608.99999", title),
                now=self.now(),
            )
            self.assertTrue(path.exists())
            self.assertEqual(state["status"], "VERIFIED_BIBLIOGRAPHIC_IDENTITY")
            self.assertRegex(state["identity_check"]["identity_binding_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(validate_external_paper_identity_receipt(state), [])


if __name__ == "__main__":
    unittest.main()
