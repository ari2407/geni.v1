from crypto_signals.manager import CriticalManager
from crypto_signals.models import AgentOpinion, Signal, Team

def signal(**kwargs):
    values = dict(symbol="BTC/USDT", team=Team.SPOT, direction="long", timeframe="H1", entry=100, stop_loss=95, targets=[110], confidence=.8, risk_reward=1.5, reasons=[], opinions=[AgentOpinion("a", .5, .8, "ok")])
    values.update(kwargs)
    return Signal(**values)

def test_manager_rejects_bad_levels():
    assert not CriticalManager().approve(signal(stop_loss=0))[0]

def test_manager_approves_valid_signal():
    assert CriticalManager().approve(signal())[0]
