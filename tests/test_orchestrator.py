from crypto_signals.models import MarketSnapshot, Team
from crypto_signals.orchestrator import SignalOrchestrator
from crypto_signals.telegram import format_signal


def snapshot(**changes):
    values = dict(symbol="BTCUSDT", timeframe="H1", price=100.0, change_24h=1.0,
                  volume_ratio=1.5, trend_score=.7, momentum_score=.5,
                  volatility=.2, liquidity_score=.9, sources=("demo",))
    values.update(changes)
    return MarketSnapshot(**values)


def test_spot_signal_is_signal_only_and_user_friendly():
    signal = SignalOrchestrator().analyze(snapshot(), Team.SPOT)
    assert signal is not None
    assert signal.status == "paper"
    assert "bukan eksekusi otomatis" in format_signal(signal)


def test_rejects_scalping_below_m5():
    assert SignalOrchestrator().analyze(snapshot(timeframe="M1"), Team.SPOT) is None


def test_leverage_rejects_extreme_volatility():
    assert SignalOrchestrator().analyze(snapshot(volatility=.8), Team.LEVERAGE) is None


def test_stale_data_is_rejected():
    assert SignalOrchestrator().analyze(snapshot(data_age_seconds=901), Team.SPOT) is None


def test_self_review_is_bounded_and_non_executing():
    signal = SignalOrchestrator().analyze(snapshot(), Team.SPOT)
    result = SignalOrchestrator().self_review(signal)
    assert result["action"] == "signal_only"
