"""Team-specific branches: same agent class may have different mandates."""
from .models import Team


TEAM_BRANCHES = {
    Team.SPOT: {
        "purpose": "trend-following and accumulation candidates",
        "roles": ("candidate_screener", "market_regime", "technical_structure", "data_quality", "risk_manager", "news_research", "signal_validator"),
        "risk_profile": "conservative, no leverage",
    },
    Team.LEVERAGE: {
        "purpose": "long/short opportunities with strict invalidation",
        "roles": ("candidate_screener", "market_regime", "technical_structure", "data_quality", "risk_manager", "news_research", "signal_validator"),
        "risk_profile": "high risk, lower tolerance for volatility and stale data",
    },
}


def branch_for(team: Team) -> dict:
    return TEAM_BRANCHES[team].copy()
