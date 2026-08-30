from crypto_signals.rewards import AgentScore


def test_reward_and_penalty_are_auditable():
    score = AgentScore()
    score.settle("tp")
    score.settle("sl")
    assert score.score == 0
    assert score.win_rate == .5
    assert score.history == ["tp", "sl"]
