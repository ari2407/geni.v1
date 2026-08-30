from crypto_signals.universe import PublicUniverse


def test_universe_merges_active_pairs_from_providers():
    payloads = {
        "binance": {"symbols": [{"status": "TRADING", "baseAsset": "BTC", "quoteAsset": "USDT"}]},
        "kraken": {"result": {"XXBTZUSD": {"status": "online", "base": "XXBT", "quote": "ZUSD"}}},
        "coinbase": [{"status": "online", "base_currency": "ETH", "quote_currency": "USD"}],
    }
    def fetch(url):
        name = "binance" if "binance" in url else "kraken" if "kraken" in url else "coinbase"
        return payloads[name], {}
    symbols = PublicUniverse(fetcher=fetch).discover(max_symbols=10)
    assert "BTC/USDT" in symbols
    assert "ETH/USD" in symbols


def test_one_broken_provider_does_not_block_other_providers():
    def fetch(url):
        if "binance" in url:
            raise RuntimeError("offline")
        return {"result": {}}, {} if "kraken" in url else ([], {})
    assert PublicUniverse(fetcher=fetch).discover(max_symbols=10) == []
