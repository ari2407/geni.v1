from pathlib import Path

import pytest

from crypto_signals.live_data import SOURCES, LiveMarketData


def test_exchange_symbol_mapping_is_not_double_delimited():
    assert SOURCES[0].symbol_format("BTC/USDT") == "BTCUSDT"
    assert SOURCES[1].symbol_format("BTC/USDT") == "XBT/USDT"
    assert SOURCES[2].symbol_format("BTC/USDT") == "BTC-USDT"


def test_symbol_and_limit_are_validated_before_network(tmp_path: Path):
    data = LiveMarketData(tmp_path, fetcher=lambda _: pytest.fail("network must not be called"))
    with pytest.raises(ValueError):
        data.fetch_snapshot("../../secret", "H1")
    with pytest.raises(ValueError):
        data.fetch_snapshot("BTC/USDT", "H1", limit=1001)


def test_corrupt_cache_does_not_crash_or_be_trusted(tmp_path: Path):
    data = LiveMarketData(tmp_path, fetcher=lambda _: ([], {}))
    path = data._cache_path(SOURCES[0], "BTC/USDT", "H1")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"saved_at": 9999999999, "data": {"not": "candles"}}')
    with pytest.raises(RuntimeError):
        data.fetch_snapshot()
