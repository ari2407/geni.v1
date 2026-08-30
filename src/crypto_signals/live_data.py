"""Public exchange market-data adapter with disk cache and safe fallback.

Only public endpoints are used. No API key, order endpoint, or private request
exists in this module. Network and JSON handling are deliberately dependency-free.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .data_sources import SourceHealth, SourcePool
from .models import MarketSnapshot


@dataclass(frozen=True)
class PublicSource:
    name: str
    base_url: str
    symbol_format: Callable[[str], str]
    endpoint: str


SOURCES = (
    PublicSource("binance", "https://api.binance.com", lambda s: s.replace("/", ""), "/api/v3/klines"),
    PublicSource("kraken", "https://api.kraken.com", lambda s: s.replace("USDT", "/USDT").replace("BTC/", "XBT/"), "/0/public/OHLC"),
    PublicSource("coinbase", "https://api.exchange.coinbase.com", lambda s: s.replace("USDT", "-USDT").replace("/", "-"), "/products/{symbol}/candles"),
)


def _get_json(url: str, timeout: int = 8) -> tuple[object, dict[str, str]]:
    request = Request(url, headers={"User-Agent": "multi-agent-crypto-signals/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read()), {k.lower(): v for k, v in response.headers.items()}


class LiveMarketData:
    def __init__(self, cache_dir: str | Path = "data/runtime/cache", cache_ttl: int = 30, reserve: int = 2, fetcher=_get_json):
        self.cache_dir = Path(cache_dir)
        self.cache_ttl = cache_ttl
        self.fetcher = fetcher
        self.health = [SourceHealth(source.name) for source in SOURCES]
        self.pool = SourcePool(self.health, reserve=reserve)

    def _cache_path(self, source: PublicSource, symbol: str, timeframe: str) -> Path:
        safe = symbol.replace("/", "_")
        return self.cache_dir / f"{source.name}_{safe}_{timeframe}.json"

    def _read_cache(self, source: PublicSource, symbol: str, timeframe: str) -> dict | None:
        path = self._cache_path(source, symbol, timeframe)
        try:
            payload = json.loads(path.read_text())
            if time.time() - payload["saved_at"] <= self.cache_ttl:
                return payload["data"]
        except (OSError, ValueError, KeyError, TypeError):
            return None
        return None

    def _write_cache(self, source: PublicSource, symbol: str, timeframe: str, data: object) -> None:
        path = self._cache_path(source, symbol, timeframe)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"saved_at": time.time(), "data": data}))

    def _request(self, source: PublicSource, symbol: str, timeframe: str, limit: int) -> tuple[object, dict[str, str]]:
        interval = {"M5": "5m", "M15": "15m", "H1": "1h", "H4": "4h", "D1": "1d"}[timeframe.upper()]
        pair = source.symbol_format(symbol)
        if source.name == "binance":
            query = urlencode({"symbol": pair, "interval": interval, "limit": limit})
            url = f"{source.base_url}{source.endpoint}?{query}"
        elif source.name == "kraken":
            query = urlencode({"pair": pair, "interval": {"5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}[interval]})
            url = f"{source.base_url}{source.endpoint}?{query}"
        else:
            granularity = {"5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}[interval]
            query = urlencode({"granularity": granularity})
            url = f"{source.base_url}{source.endpoint.format(symbol=pair)}?{query}"
        return self.fetcher(url)

    @staticmethod
    def _closes(source: str, payload: object) -> list[float]:
        if source == "binance":
            return [float(row[4]) for row in payload]
        if source == "kraken":
            result = payload.get("result", {})
            rows = next((value for key, value in result.items() if key != "last"), [])
            return [float(row[4]) for row in rows]
        return [float(row[4]) for row in payload]

    def fetch_snapshot(self, symbol: str = "BTC/USDT", timeframe: str = "H1", limit: int = 50) -> MarketSnapshot:
        timeframe = timeframe.upper()
        if timeframe not in {"M5", "M15", "H1", "H4", "D1"}:
            raise ValueError("timeframe must be M5, M15, H1, H4, or D1")
        for source in SOURCES:
            cached = self._read_cache(source, symbol, timeframe)
            if cached is not None:
                closes = self._closes(source.name, cached)
                return self._snapshot(symbol, timeframe, closes, source.name, cached=True)
        while (health := self.pool.next()) is not None:
            source = next(item for item in SOURCES if item.name == health.name)
            try:
                payload, headers = self._request(source, symbol, timeframe, limit)
                closes = self._closes(source.name, payload)
                if len(closes) < 5:
                    raise ValueError("source returned too few candles")
                if "x-mbx-used-weight-1m" in headers:
                    health.remaining = max(0, 1200 - int(headers["x-mbx-used-weight-1m"]))
                    health.limit = 1200
                else:
                    remaining = headers.get("x-ratelimit-remaining") or headers.get("ratelimit-remaining")
                    limit = headers.get("x-ratelimit-limit") or headers.get("ratelimit-limit")
                    if remaining is not None:
                        health.remaining = int(remaining)
                    if limit is not None:
                        health.limit = int(limit)
                self._write_cache(source, symbol, timeframe, payload)
                return self._snapshot(symbol, timeframe, closes, source.name, cached=False)
            except Exception as exc:  # fallback must keep the pipeline alive
                self.pool.mark_failure(health, str(exc))
        raise RuntimeError("all public market-data sources failed or are rate-limited")

    @staticmethod
    def _snapshot(symbol: str, timeframe: str, closes: list[float], source: str, cached: bool) -> MarketSnapshot:
        latest = closes[-1]
        previous = closes[-2]
        lookback = closes[max(0, len(closes) - 20)]
        trend = max(-1.0, min(1.0, (latest / lookback - 1) * 8)) if lookback else 0
        momentum = max(-1.0, min(1.0, (latest / previous - 1) * 40)) if previous else 0
        returns = [(closes[i] / closes[i - 1] - 1) for i in range(1, len(closes)) if closes[i - 1]]
        volatility = min(1.0, (sum(x * x for x in returns) / max(1, len(returns))) ** .5 * 20)
        return MarketSnapshot(symbol, timeframe, latest, (latest / closes[0] - 1) * 100, 1.0, trend, momentum, volatility, .8, 0 if not cached else 30, (source,))
