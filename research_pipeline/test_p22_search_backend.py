from __future__ import annotations

import unittest
from unittest.mock import patch

from .p22_search_backend import bing_search, direct_read_page


class _Response:
    def __init__(self, text: str, *, content_type: str = "text/html"):
        self.text = text
        self.content = text.encode()
        self.headers = {"content-type": content_type}
        self.status_code = 200
        self.url = "https://example.test/page"
        self.encoding = "utf-8"
        self.apparent_encoding = "utf-8"

    def raise_for_status(self):
        return None


class P22SearchBackendTest(unittest.TestCase):
    def test_bing_parser_preserves_expected_result_shape(self):
        html = '<ol><li class="b_algo"><h2><a href="https://example.com/a">Example A</a></h2><div class="b_caption"><p>Alpha snippet.</p></div></li></ol>'
        with patch("research_pipeline.p22_search_backend.requests.get", return_value=_Response(html)):
            rows, error = bing_search("alpha", serp_num=5, max_retries=1)
        self.assertEqual(error, "")
        self.assertEqual(len(rows), 1)
        self.assertEqual(set(rows[0]), {"idx", "title", "date", "snippet", "source", "link"})
        self.assertEqual(rows[0]["link"], "https://example.com/a")

    def test_direct_reader_removes_script_and_returns_text(self):
        html = '<html><head><script>secret()</script></head><body><h1>Title</h1><p>Useful text.</p></body></html>'
        with patch("research_pipeline.p22_search_backend.requests.get", return_value=_Response(html)):
            text = direct_read_page("https://example.test/page")
        self.assertIn("Useful text.", text)
        self.assertNotIn("secret()", text)

    def test_direct_reader_rejects_non_http_url(self):
        self.assertTrue(direct_read_page("file:///tmp/a").startswith("Error reading page"))


if __name__ == "__main__":
    unittest.main()
