from crypto_signals.models import Team
from crypto_signals.roster import TeamRoster


def test_roster_has_five_active_roles_and_reserves():
    roster = TeamRoster(Team.SPOT)
    assert len(roster.active) == 5
    assert len(roster.reserves) == 5


def test_three_losses_replace_active_agent():
    roster = TeamRoster(Team.SPOT, penalty_limit=3)
    old = roster.active["risk_manager"].name
    for _ in range(3): roster.record(old, "sl")
    assert roster.active["risk_manager"].name != old
    assert any(item.name == old for item in roster.reserves)
