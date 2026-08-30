from crypto_signals.data_sources import SourceHealth, SourcePool


def test_pool_rotates_before_reserve_limit():
    first = SourceHealth("first", remaining=1, limit=100)
    second = SourceHealth("second", remaining=10, limit=100)
    assert SourcePool([first, second]).next().name == "second"


def test_pool_fails_safe_when_all_sources_unavailable():
    pool = SourcePool([SourceHealth("a", remaining=0, limit=10, healthy=False)])
    assert pool.next() is None
