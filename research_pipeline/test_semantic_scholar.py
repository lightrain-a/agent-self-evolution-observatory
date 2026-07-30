from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .config import SemanticScholarSettings
from .models import text
from .providers import ResearchScope
from .query_planner import DefaultQueryPlanner
from .semantic_scholar import SemanticScholarClient, paper_to_site_record, retrieved_paper_from_api


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.headers: dict[str, str] = {}
        self.text = json.dumps(payload)

    def json(self) -> dict:
        return self.payload


class SemanticScholarProviderTest(unittest.TestCase):
    def test_safe_summary_never_contains_key(self) -> None:
        settings = SemanticScholarSettings(api_key="secret-value")
        payload = settings.safe_summary()
        self.assertTrue(payload["configured"])
        self.assertNotIn("secret-value", json.dumps(payload))

    def test_five_route_planner_is_auditable(self) -> None:
        scope = ResearchScope(
            topic=text("self-evolving visual agents", "视觉 Agent 自进化"),
            target_venue="CVPR",
            seed_papers=["Seed Paper"],
            query_hints={
                "topic": ["self evolving visual agents"],
                "failure": ["visual agent failure"],
                "mechanism": ["causal trajectory attribution"],
                "analogy": ["software regression validation"],
            },
            year_range="2022-2026",
            fields_of_study=["Computer Science"],
        )
        queries = DefaultQueryPlanner().plan(scope, [])
        self.assertEqual({query.route for query in queries}, {"seed", "topic", "failure", "mechanism", "analogy"})
        self.assertTrue(all(query.purpose for query in queries))
        self.assertTrue(all(query.filters.get("fieldsOfStudy") == "Computer Science" for query in queries))

    def test_disk_cache_prevents_duplicate_network_calls(self) -> None:
        calls = []

        def requester(method, url, headers, timeout):
            calls.append((method, url, timeout, headers.get("x-api-key"), list(headers)))
            return _FakeResponse({"data": [{"paperId": "p1", "title": "Paper One"}]})

        with tempfile.TemporaryDirectory() as directory:
            settings = SemanticScholarSettings(
                api_key="secret-value",
                min_interval_seconds=1.01,
                cache_ttl_hours=1,
                cache_dir=Path(directory),
            )
            client = SemanticScholarClient(settings, requester=requester, sleeper=lambda _: None)
            first = client.get_json("paper/search", {"query": "test", "limit": 1})
            second = client.get_json("paper/search", {"query": "test", "limit": 1})
        self.assertEqual(first, second)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][3], "secret-value")
        self.assertIn("x-api-key", calls[0][4])

    def test_site_record_preserves_provider_metadata(self) -> None:
        paper = retrieved_paper_from_api(
            {
                "paperId": "p1",
                "title": "Self-Evolving Visual Agent",
                "year": 2026,
                "venue": "CVPR",
                "url": "https://example.org/p1",
                "abstract": "A visual agent improves through interaction.",
                "citationCount": 12,
                "fieldsOfStudy": ["Computer Science"],
            }
        )
        paper.metadata["matches"] = [{"route": "topic", "query": "visual agents", "rank": 1}]
        record = paper_to_site_record(paper)
        self.assertEqual(record["source"], "semantic-scholar")
        self.assertEqual(record["citationCount"], 12)
        self.assertTrue(record["vision"])
        self.assertEqual(record["s2Routes"], ["topic"])


if __name__ == "__main__":
    unittest.main()
