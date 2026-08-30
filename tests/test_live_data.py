import json
from pathlib import Path

from crypto_signals.live_data import LiveMarketData


def fake_fetcher(url):
    payload = [[i, "1", "2", "1", str(100 + i), "1"] for i in range(30)]
    return payload, {"x-mbx-used-weight-1m": "10"}


def test_public_adapter_creates_snapshot_and_cache(tmp_path: Path):
    data = LiveMarketData(tmp_path, fetcher=fake_fetcher)
    snapshot = data.fetch_snapshot("BTC/USDT", "H1")
    assert snapshot.price == 129
    assert snapshot.sources == ("binance",)
    assert list(tmp_path.glob("*.json"))


def test_cached_payload_is_used(tmp_path: Path):
    first = LiveMarketData(tmp_path, fetcher=fake_fetcher)
    first.fetch_snapshot("BTC/USDT", "H1")

    def must_not_call(_):
        raise AssertionError("network should not be used while cache is fresh")

    second = LiveMarketData(tmp_path, fetcher=must_not_call)
    assert second.fetch_snapshot("BTC/USDT", "H1").price == 129
