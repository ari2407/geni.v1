from datetime import datetime, timezone
from crypto_signals.summary import DailySummaryAgent


def test_daily_summary_sends_once_after_23_utc():
    sent = []
    summary = DailySummaryAgent(sent.append)
    summary.record("spot", "long")
    at_22 = datetime(2026, 8, 30, 22, 59, tzinfo=timezone.utc)
    at_23 = datetime(2026, 8, 30, 23, 0, tzinfo=timezone.utc)
    assert not summary.maybe_send(at_22)
    assert summary.maybe_send(at_23)
    assert not summary.maybe_send(at_23)
    assert len(sent) == 1
    assert "Spot: 1 signal" in sent[0]
