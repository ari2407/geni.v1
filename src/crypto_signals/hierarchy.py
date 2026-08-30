"""Explicit reporting line for each team; roles remain auditable."""
from dataclasses import dataclass
from .models import Team


@dataclass(frozen=True)
class Role:
    name: str
    reports_to: str
    permissions: tuple[str, ...]


TEAM_ROLES = {
    Team.SPOT: (
        Role("candidate_screener", "spot_manager", ("read_market",)),
        Role("deep_researcher", "spot_manager", ("read_public_data", "read_github_metadata")),
        Role("technical_analyst", "spot_manager", ("read_market",)),
        Role("risk_manager", "spot_manager", ("read_market",)),
        Role("spot_manager", "fund_manager", ("approve_signal",)),
        Role("telegram_notifier", "fund_manager", ("send_telegram",)),
    ),
    Team.LEVERAGE: (
        Role("candidate_screener", "leverage_manager", ("read_market",)),
        Role("deep_researcher", "leverage_manager", ("read_public_data", "read_github_metadata")),
        Role("technical_analyst", "leverage_manager", ("read_market",)),
        Role("risk_manager", "leverage_manager", ("read_market",)),
        Role("leverage_manager", "fund_manager", ("approve_signal",)),
        Role("telegram_notifier", "fund_manager", ("send_telegram",)),
    ),
}


def roles_for(team: Team) -> tuple[Role, ...]:
    return TEAM_ROLES[team]
