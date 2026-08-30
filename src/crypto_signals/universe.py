"""Public asset-universe discovery with an extensible provider registry."""
from __future__ import annotations

from dataclasses import dataclass
from .live_data import _get_json


@dataclass(frozen=True)
class UniverseProvider:
    name: str
    url: str


PROVIDERS = (
    UniverseProvider("binance", "https://api.binance.com/api/v3/exchangeInfo"),
    UniverseProvider("kraken", "https://api.kraken.com/0/public/AssetPairs"),
    UniverseProvider("coinbase", "https://api.exchange.coinbase.com/products"),
)


class PublicUniverse:
    def __init__(self, fetcher=_get_json, providers=PROVIDERS):
        self.fetcher = fetcher
        self.providers = providers

    def discover(self, quote_assets=("USDT", "USD"), max_symbols=1000) -> list[str]:
        symbols: set[str] = set()
        for provider in self.providers:
            try:
                payload, _ = self.fetcher(provider.url)
                symbols.update(self._parse(provider.name, payload, quote_assets))
            except Exception:
                # One registry provider must never block the others.
                continue
        return sorted(symbols)[:max_symbols]

    @staticmethod
    def _parse(name, payload, quote_assets):
        result = set()
        if name == "binance":
            for item in payload.get("symbols", []):
                if item.get("status") == "TRADING" and item.get("quoteAsset") in quote_assets:
                    result.add(f"{item['baseAsset']}/{item['quoteAsset']}")
        elif name == "kraken":
            for key, item in payload.get("result", {}).items():
                if item.get("status") not in (None, "online"):
                    continue
                quote = item.get("quote", "").replace("Z", "").replace("X", "")
                if quote in quote_assets:
                    base = item.get("base", "").replace("X", "").replace("Z", "")
                    if base == "XBT": base = "BTC"
                    result.add(f"{base}/{quote}")
        else:
            for item in payload if isinstance(payload, list) else []:
                if item.get("status") == "online" and item.get("quote_currency") in quote_assets:
                    result.add(f"{item['base_currency']}/{item['quote_currency']}")
        return result
