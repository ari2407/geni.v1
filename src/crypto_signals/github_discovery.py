"""Metadata-only GitHub research. Never clones or executes remote repositories."""
from __future__ import annotations
import json
from urllib.parse import quote
from urllib.request import Request, urlopen

QUERIES = ("crypto market data", "crypto technical analysis", "crypto sentiment", "crypto backtesting", "AI research agent finance")

def discover_github(fetcher=urlopen, per_query=5):
    findings = []
    for query in QUERIES:
        url = "https://api.github.com/search/repositories?q=" + quote(query) + "+stars:%3E10&sort=stars&order=desc&per_page=" + str(per_query)
        try:
            request = Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "crypto-signals-research"})
            with fetcher(request, timeout=10) as response:
                data = json.loads(response.read())
            for item in data.get("items", []):
                findings.append({"name": item.get("full_name"), "url": item.get("html_url"), "license": (item.get("license") or {}).get("spdx_id"), "stars": item.get("stargazers_count", 0), "query": query})
        except Exception:
            continue
    return {item["url"]: item for item in findings if item.get("url")}
