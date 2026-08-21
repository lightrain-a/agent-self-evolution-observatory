from __future__ import annotations

import hashlib
import io
import json
import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import requests

USER_AGENT = "Mozilla/5.0 (compatible; P22RetrievalBudgetHarness/1.0; research)"
SEARCH_BACKEND = "bing-html-top5-v2-frozen-cache"
CRAWL_BACKEND = "direct-https-html-pdf-v2-frozen-cache"
CACHE_ENV = "P22_WEB_CACHE_DIR"


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
                self.rows.append({"title": title or "No title", "snippet": snippet, "link": self.href})
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


def _cache_dir() -> Path | None:
    raw = os.getenv(CACHE_ENV, "").strip()
    return Path(raw) if raw else None


def _cache_path(kind: str, payload: dict[str, object]) -> Path | None:
    root = _cache_dir()
    if root is None: return None
    digest = hashlib.sha256(json.dumps({"kind":kind,"payload":payload},ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return root / kind / f"{digest}.json"


def _read_cache(path: Path | None):
    if path is None or not path.is_file(): return None
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return None


def _write_cache(path: Path | None, payload: dict[str, object]) -> None:
    if path is None: return
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text,encoding="utf-8"); os.replace(tmp,path)


def bing_search(query: str, filter_year=None, serp_num: int = 5, max_retries: int = 3):
    query = str(query or "").strip()
    if not query: return [], "Query is empty. Please provide a valid query string."
    cache = _cache_path("search", {"backend":SEARCH_BACKEND,"query":query,"filter_year":filter_year,"serp_num":int(serp_num)})
    cached = _read_cache(cache)
    if isinstance(cached,dict): return list(cached.get("results") or []), str(cached.get("error") or "")
    url = "https://www.bing.com/search?q=" + quote_plus(query)
    last_error = ""
    for _ in range(max(1, int(max_retries))):
        try:
            response = requests.get(url, headers={"User-Agent":USER_AGENT}, timeout=15)
            response.raise_for_status(); parser = _BingParser(); parser.feed(response.text)
            results = []
            for row in parser.rows[:int(serp_num)]:
                link = row["link"]
                if not link.startswith(("http://","https://")): continue
                host = urlparse(link).hostname or "Unknown source"
                results.append({"idx":len(results)+1,"title":row["title"],"date":"","snippet":"\n"+row["snippet"],"source":"\nSource: "+host,"link":link})
            if results:
                _write_cache(cache,{"backend":SEARCH_BACKEND,"results":results,"error":"","scientific_authority":False})
                return results, ""
            last_error = "No parseable Bing results"
        except Exception as error:
            last_error = f"{type(error).__name__}: {error}"
    error = f"Search failed after {max_retries} attempts: {last_error}"
    _write_cache(cache,{"backend":SEARCH_BACKEND,"results":[],"error":error,"scientific_authority":False})
    return [], error


def _html_to_text(data: bytes, encoding: str | None = None) -> str:
    parser = _TextParser(); parser.feed(data.decode(encoding or "utf-8", errors="replace"))
    return "\n".join(parser.parts)


def _js_only_or_empty(html: str, text: str) -> bool:
    lowered = (html + "\n" + text).lower()
    markers = ("enable javascript", "javascript is required", "requires javascript", "please turn on javascript")
    return any(marker in lowered for marker in markers)


def direct_read_page(url: str) -> str:
    url = str(url or "")
    if not url.startswith(("http://","https://")): return "Error reading page: invalid URL"
    cache = _cache_path("crawl", {"backend":CRAWL_BACKEND,"url":url})
    cached = _read_cache(cache)
    if isinstance(cached,dict): return str(cached.get("text") or "")
    try:
        response = requests.get(url, headers={"User-Agent":USER_AGENT}, timeout=20, allow_redirects=True)
        response.raise_for_status(); content_type = (response.headers.get("content-type") or "").lower()
        if "pdf" in content_type or str(response.url).lower().endswith(".pdf"):
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(io.BytesIO(response.content))
            except Exception as error:
                text = f"Error reading page: PDF extraction failed: {type(error).__name__}: {error}"
        else:
            encoding = response.encoding if response.encoding and response.encoding.lower() != "iso-8859-1" else response.apparent_encoding
            html = response.content.decode(encoding or "utf-8",errors="replace")
            text = _html_to_text(response.content, encoding)
            if _js_only_or_empty(html,text): text = "Error reading page: P22_UNSUPPORTED_JS_ONLY_PAGE"
        text = re.sub(r"\n{3,}","\n\n",str(text)).strip()
        if not text: text = f"Error reading page: No content extracted from {url}"
    except Exception as error:
        text = f"Error reading page: {type(error).__name__}: {error}"
    _write_cache(cache,{"backend":CRAWL_BACKEND,"url":url,"text":text,"scientific_authority":False})
    return text


def install_experimental_bing_direct() -> dict[str, object]:
    """Install the rejected Bing/direct transport only for reproducible support probes."""
    import FlashOAgents.search_tools as search_tools
    search_tools.web_search_google_serper = bing_search
    search_tools.read_page = direct_read_page
    return {"status":"EXPERIMENTAL_NOT_AUTHORIZED","search_transport":SEARCH_BACKEND,"crawl_transport":CRAWL_BACKEND,"scientific_authority":False}


def install_original_transport_with_cache() -> dict[str, object]:
    """Keep the pinned Serper/Jina semantics and add only byte-stable replay caching."""
    import FlashOAgents.search_tools as search_tools
    original_search = search_tools.web_search_google_serper
    original_read = search_tools.read_page

    def cached_search(query: str, filter_year=None, serp_num: int = 5, max_retries: int = 3):
        cache = _cache_path("original-search", {"backend":"serper-original-cache-v1","query":str(query),"filter_year":filter_year,"serp_num":int(serp_num)})
        cached = _read_cache(cache)
        if isinstance(cached,dict): return list(cached.get("results") or []), str(cached.get("error") or "")
        results,error = original_search(query,filter_year=filter_year,serp_num=serp_num,max_retries=max_retries)
        _write_cache(cache,{"backend":"serper-original-cache-v1","results":results,"error":error,"scientific_authority":False})
        return results,error

    def cached_read(url: str) -> str:
        cache = _cache_path("original-crawl", {"backend":"jina-original-cache-v1","url":str(url)})
        cached = _read_cache(cache)
        if isinstance(cached,dict): return str(cached.get("text") or "")
        text = original_read(url)
        _write_cache(cache,{"backend":"jina-original-cache-v1","url":str(url),"text":text,"scientific_authority":False})
        return text

    search_tools.web_search_google_serper = cached_search
    search_tools.read_page = cached_read
    return {"status":"ORIGINAL_TRANSPORT_CACHE_WRAPPER","search_transport":"Serper original + frozen replay cache","crawl_transport":"Jina original + frozen replay cache","same_query_url_replays_cached_bytes":_cache_dir() is not None,"scientific_authority":False}
