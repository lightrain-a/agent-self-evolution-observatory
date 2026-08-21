from __future__ import annotations

import io
import re
from html.parser import HTMLParser
from urllib.parse import quote_plus, urlparse

import requests

USER_AGENT = "Mozilla/5.0 (compatible; P22RetrievalBudgetHarness/1.0; research)"


class _BingParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[dict[str, str]] = []
        self.depth = 0
        self.algo_depth: int | None = None
        self.in_h2 = False
        self.in_p = False
        self.href = ""
        self.title: list[str] = []
        self.snippet: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.depth += 1
        attrs = dict(attrs)
        classes = set(str(attrs.get("class") or "").split())
        if tag == "li" and "b_algo" in classes and self.algo_depth is None:
            self.algo_depth = self.depth
            self.href = ""; self.title = []; self.snippet = []
        if self.algo_depth is not None:
            if tag == "h2": self.in_h2 = True
            elif tag == "a" and self.in_h2 and not self.href: self.href = str(attrs.get("href") or "")
            elif tag == "p" and not self.snippet: self.in_p = True

    def handle_endtag(self, tag):
        if tag == "h2": self.in_h2 = False
        elif tag == "p": self.in_p = False
        if tag == "li" and self.algo_depth == self.depth:
            if self.href:
                title = " ".join(" ".join(self.title).split())
                snippet = " ".join(" ".join(self.snippet).split())
                self.rows.append({"title":title or "No title","snippet":snippet,"link":self.href})
            self.algo_depth = None
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if self.algo_depth is None: return
        if self.in_h2: self.title.append(data)
        elif self.in_p: self.snippet.append(data)


class _TextParser(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.parts: list[str] = []
    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP: self.skip_depth += 1
    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth: self.skip_depth -= 1
    def handle_data(self, data):
        if not self.skip_depth:
            text = " ".join(data.split())
            if text: self.parts.append(text)


def bing_search(query: str, filter_year=None, serp_num: int = 5, max_retries: int = 3):
    if not str(query or "").strip(): return [], "Query is empty. Please provide a valid query string."
    url = "https://www.bing.com/search?q=" + quote_plus(str(query))
    last_error = ""
    for _ in range(max(1, int(max_retries))):
        try:
            response = requests.get(url, headers={"User-Agent":USER_AGENT}, timeout=15)
            response.raise_for_status()
            parser = _BingParser(); parser.feed(response.text)
            results = []
            for row in parser.rows[:int(serp_num)]:
                host = urlparse(row["link"]).hostname or "Unknown source"
                results.append({"idx":len(results)+1,"title":row["title"],"date":"","snippet":"\n"+row["snippet"],"source":"\nSource: "+host,"link":row["link"]})
            if results: return results, ""
            last_error = "No parseable Bing results"
        except Exception as error:
            last_error = f"{type(error).__name__}: {error}"
    return [], f"Search failed after {max_retries} attempts: {last_error}"


def _html_to_text(data: bytes, encoding: str | None = None) -> str:
    parser = _TextParser(); parser.feed(data.decode(encoding or "utf-8", errors="replace"))
    return "\n".join(parser.parts)


def direct_read_page(url: str) -> str:
    if not str(url).startswith(("http://","https://")): return "Error reading page: invalid URL"
    try:
        response = requests.get(str(url), headers={"User-Agent":USER_AGENT}, timeout=20, allow_redirects=True)
        response.raise_for_status()
        content_type = (response.headers.get("content-type") or "").lower()
        if "pdf" in content_type or str(response.url).lower().endswith(".pdf"):
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(io.BytesIO(response.content))
            except Exception as error:
                return f"Error reading page: PDF extraction failed: {type(error).__name__}: {error}"
        else:
            encoding = response.encoding if response.encoding and response.encoding.lower() != "iso-8859-1" else response.apparent_encoding
            text = _html_to_text(response.content, encoding)
        text = re.sub(r"\n{3,}","\n\n",text).strip()
        return text if text else f"Error reading page: No content extracted from {url}"
    except Exception as error:
        return f"Error reading page: {type(error).__name__}: {error}"


def install_into_pinned_search_tools() -> dict[str, object]:
    import FlashOAgents.search_tools as search_tools
    search_tools.web_search_google_serper = bing_search
    search_tools.read_page = direct_read_page
    return {"search_tool_class_unchanged":search_tools.WebSearchTool.__name__=="WebSearchTool","crawl_tool_class_unchanged":search_tools.CrawlPageTool.__name__=="CrawlPageTool","search_transport":"bing-html-top5-v1","crawl_transport":"direct-https-html-pdf-v1","scientific_authority":False}
