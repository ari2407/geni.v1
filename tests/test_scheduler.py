from crypto_signals.live_data import LiveMarketData
from crypto_signals.models import MarketSnapshot
from crypto_signals.orchestrator import SignalOrchestrator
from crypto_signals.scheduler import SchedulerConfig, SignalScheduler


class FakeData:
    def __init__(self):
        self.calls = 0

    def fetch_snapshot(self, symbol, timeframe):
        self.calls += 1
        return MarketSnapshot(symbol, timeframe, 100, 1, 1.5, .7, .5, .2, .9, sources=("fake",))


def test_cooldown_deduplicates_identical_signal():
    output = []
    clock = [100.0]
    scheduler = SignalScheduler(FakeData(), SignalOrchestrator(), SchedulerConfig(5, 1800, 0), output.append, lambda: clock[0])
    first = scheduler.run_cycle()
    second = scheduler.run_cycle()
    assert first
    assert not second
    # team is part of the key, so each team can emit once in the first cycle.
    assert len(first) == 2
    assert len(output) == 2


def test_retry_then_success():
    calls = [0]
    class RetryData:
        def fetch_snapshot(self, symbol, timeframe):
            calls[0] += 1
            if calls[0] == 1:
                raise RuntimeError("temporary")
            return MarketSnapshot(symbol, timeframe, 100, 1, 1.5, .7, .5, .2, .9, sources=("fake",))
    sleeps = []
    scheduler = SignalScheduler(RetryData(), config=SchedulerConfig(5, 0, 1, .01), sleep=sleeps.append)
    assert scheduler.run_cycle()
    assert calls[0] == 2
    assert sleeps == [.01]
