from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_harnessbank_support_audit import (
    ARXIV_API,
    CANDIDATE_REPOSITORY_API,
    GITHUB_SEARCH_QUERIES,
    build_harnessbank_support_audit,
    build_harnessbank_support_hold,
    probe_current_primary_source,
    probe_current_release_surface,
    validate_harnessbank_support_audit,
    validate_harnessbank_support_hold,
)


class HarnessBankSupportAuditTest(unittest.TestCase):
    def hashes(self) -> dict[str, str]:
        return {
            "source_tree_sha256": "a" * 64,
            "paper_pdf_sha256": "b" * 64,
            "paper_text_sha256": "c" * 64,
        }

    def primary(self, *, changed: bool = False) -> dict:
        return {
            "checked_at": "2026-08-17T08:00:00+00:00",
            "arxiv_api_http_status": 200,
            "probe_complete": True,
            "arxiv_version": "v3" if changed else "v2",
            "last_revised": "2026-08-18" if changed else "2026-07-30",
            "updated_at": "2026-08-18T00:00:00Z" if changed else "2026-07-30T08:41:14Z",
            "title": "HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution",
            "code_disclosure": "" if changed else "Our code will be publicly available upon acceptance.",
            "code_release_is_future_conditional": not changed,
            "primary_source_changed": changed,
        }

    def no_release_getter(self, url: str):
        if url == CANDIDATE_REPOSITORY_API:
            return 404, {"message": "Not Found"}
        for query in GITHUB_SEARCH_QUERIES:
            if "search/repositories" in url and query.split()[0] in url:
                return 200, {"total_count": 0, "items": []}
        return 200, {"total_count": 0, "items": []}

    def test_primary_source_probe_reads_current_arxiv_version_and_disclosure(self) -> None:
        atom = b"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'>
  <entry>
    <id>http://arxiv.org/abs/2607.13683v2</id>
    <updated>2026-07-30T08:41:14Z</updated>
    <published>2026-07-15T10:26:26Z</published>
    <title>HarnessBank: Semantic Gene-Bank Search with Gated Verification for Agent-Harness Self-Evolution</title>
    <summary>Our code will be publicly available upon acceptance.</summary>
  </entry>
</feed>"""

        def getter(url: str):
            self.assertEqual(ARXIV_API, url)
            return 200, atom

        primary = probe_current_primary_source(http_bytes=getter)
        self.assertTrue(primary["probe_complete"])
        self.assertEqual("v2", primary["arxiv_version"])
        self.assertEqual("2026-07-30", primary["last_revised"])
        self.assertTrue(primary["code_release_is_future_conditional"])
        self.assertFalse(primary["primary_source_changed"])

    def test_no_public_release_keeps_pa03_on_support_hold(self) -> None:
        release = probe_current_release_surface(http_json=self.no_release_getter)
        self.assertTrue(release["probe_complete"])
        self.assertFalse(release["release_surface_changed"])
        self.assertFalse(release["required_unit_release_confirmed"])
        state = build_harnessbank_support_audit(
            primary_source_probe=self.primary(), release_surface=release, **self.hashes()
        )
        self.assertEqual("HOLD_SUPPORT_NO_RELEASED_REQUIRED_UNIT", state["status"])
        self.assertFalse(state["released_required_unit_present"])
        self.assertEqual([], validate_harnessbank_support_audit(state))

    def test_incomplete_github_probe_cannot_be_recorded_as_release_negative(self) -> None:
        def getter(url: str):
            if url == CANDIDATE_REPOSITORY_API:
                return 404, {"message": "Not Found"}
            return 403, {"message": "rate limited"}

        release = probe_current_release_surface(http_json=getter)
        self.assertFalse(release["probe_complete"])
        state = build_harnessbank_support_audit(
            primary_source_probe=self.primary(), release_surface=release, **self.hashes()
        )
        self.assertIn(
            "harnessbank-release-surface-probe-incomplete",
            validate_harnessbank_support_audit(state),
        )

    def test_repository_hit_only_opens_manual_asset_review(self) -> None:
        def getter(url: str):
            if url == CANDIDATE_REPOSITORY_API:
                return 200, {"full_name": "GAIR-NLP/HarnessBank"}
            return 200, {"total_count": 1, "items": [{"full_name": "GAIR-NLP/HarnessBank"}]}

        release = probe_current_release_surface(http_json=getter)
        self.assertTrue(release["release_surface_changed"])
        self.assertFalse(release["required_unit_release_confirmed"])
        state = build_harnessbank_support_audit(
            primary_source_probe=self.primary(), release_surface=release, **self.hashes()
        )
        self.assertEqual("HOLD_SUPPORT_RELEASE_SURFACE_CHANGED_REVIEW_REQUIRED", state["status"])
        self.assertFalse(state["released_required_unit_present"])
        self.assertEqual([], validate_harnessbank_support_audit(state))

    def test_new_arxiv_version_only_opens_primary_source_review(self) -> None:
        release = probe_current_release_surface(http_json=self.no_release_getter)
        state = build_harnessbank_support_audit(
            primary_source_probe=self.primary(changed=True), release_surface=release, **self.hashes()
        )
        self.assertEqual("HOLD_SUPPORT_PRIMARY_SOURCE_CHANGED_REVIEW_REQUIRED", state["status"])
        self.assertFalse(state["released_required_unit_present"])
        self.assertEqual([], validate_harnessbank_support_audit(state))

    def test_release_surface_cannot_auto_claim_required_corpus(self) -> None:
        release = probe_current_release_surface(http_json=self.no_release_getter)
        state = build_harnessbank_support_audit(
            primary_source_probe=self.primary(), release_surface=release, **self.hashes()
        )
        state["current_release_surface_audit"]["required_unit_release_confirmed"] = True
        self.assertIn(
            "release-surface-probe-cannot-auto-confirm-required-unit",
            validate_harnessbank_support_audit(state),
        )

    def test_tampered_receipt_fails_content_hash(self) -> None:
        release = probe_current_release_surface(http_json=self.no_release_getter)
        state = build_harnessbank_support_audit(
            primary_source_probe=self.primary(), release_surface=release, **self.hashes()
        )
        tampered = copy.deepcopy(state)
        tampered["why_hold"] = "changed after audit"
        self.assertIn("harnessbank-support-audit-hash-mismatch", validate_harnessbank_support_audit(tampered))

    def test_support_hold_is_content_addressed_to_current_audit(self) -> None:
        release = probe_current_release_surface(http_json=self.no_release_getter)
        state = build_harnessbank_support_audit(
            primary_source_probe=self.primary(), release_surface=release, **self.hashes()
        )
        with tempfile.TemporaryDirectory(prefix="pa03-hold-test-") as tmp:
            audit_path = Path(tmp) / "audit.json"
            audit_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            file_sha = hashlib.sha256(audit_path.read_bytes()).hexdigest()
            hold = build_harnessbank_support_hold(audit=state, audit_file_sha256=file_sha)
            self.assertEqual([], validate_harnessbank_support_hold(hold, audit_path=audit_path))
            hold["support_audit_sha256"] = "0" * 64
            self.assertIn(
                "harnessbank-support-hold-audit-file-hash-mismatch",
                validate_harnessbank_support_hold(hold, audit_path=audit_path),
            )

    def test_audit_cannot_carry_scientific_or_execution_authority(self) -> None:
        release = probe_current_release_surface(http_json=self.no_release_getter)
        state = build_harnessbank_support_audit(
            primary_source_probe=self.primary(), release_surface=release, **self.hashes()
        )
        state["authority"]["experiment_authority"] = True
        errors = validate_harnessbank_support_audit(state)
        self.assertIn("harnessbank-support-audit-cannot-carry-authority", errors)


if __name__ == "__main__":
    unittest.main()
