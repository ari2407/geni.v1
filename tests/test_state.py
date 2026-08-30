from crypto_signals.state import PersistentState

def test_state_survives_reopen(tmp_path):
    path = tmp_path / "state.db"
    state = PersistentState(path)
    assert state.allowed("a", 100, 10)
    state.remember("a", 100)
    assert not state.allowed("a", 105, 10)
    reopened = PersistentState(path)
    assert reopened.allowed("a", 111, 10)
    reopened.record("2026-08-30", "spot")
    assert reopened.stats("2026-08-30")["spot"] == 1
